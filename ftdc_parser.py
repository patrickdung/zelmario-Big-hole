# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 10:55:10 2024

@author: zelmar@michelini.com.uy
"""

import argparse
import ijson
import requests
from datetime import datetime
import re
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up argument parser
parser = argparse.ArgumentParser(description='Process a JSON file.')
parser.add_argument('file_path', type=str, help='The path to the JSON file')

# Parse the arguments
args = parser.parse_args()

# VictoriaMetrics details
victoria_url = "http://ftdc-victoriametrics:8428"  # Update with your VictoriaMetrics URL

# Function to send data to VictoriaMetrics
def send_to_victoriametrics(data):
    url = f"{victoria_url}/write"
    headers = {
        "Content-Type": "text/plain; charset=utf-8"
    }
    response = requests.post(url, data=data, headers=headers)
    if response.status_code != 204:
        print(f"Failed to write data to VictoriaMetrics: {response.text}")

# Get metrics and process them
def generate_timestamps(metric_set):
    return metric_set['DataPointsMap']['serverStatus.localTime']

metrics_file = '/app/metrics_to_get.txt'
keys_to_check = []

with open(metrics_file, 'r') as file:
    keys_to_check = [line.strip() for line in file]

# Patterns for various metrics
disk_metrics_pattern = re.compile(
    r'^systemMetrics\.disks\..*\.(io_in_progress|io_queued_ms|io_time_ms|read_sectors|read_time_ms|reads|reads_merged|write_sectors|write_time_ms|writes|writes_merged)$'
)

member_metrics_pattern = re.compile(
    r'^replSetGetStatus\.members\.\d+\.(pingMs|lastAppliedWallTime|health)$'
)

mount_metrics_pattern = re.compile(
    r'^systemMetrics\.mounts\.(\/(?:[^\/]+\/?)*)\.(available|capacity|free)$'
)

def process_metrics(metric_set):
    timestamps = generate_timestamps(metric_set)
    lines = []

    for key, values in metric_set["DataPointsMap"].items():
        if key in keys_to_check or disk_metrics_pattern.match(key) or member_metrics_pattern.match(key) or mount_metrics_pattern.match(key):
            for ts, value in zip(timestamps, values):
                timestamp = int(ts * 1e6)  # Convert milliseconds to nanoseconds
                measurement = "ftdc"
                # Prepare tags if needed
                tags = ""

                # For mount metrics, extract the mount point as a tag
                mount_match = mount_metrics_pattern.match(key)
                if mount_match:
                    mount_point = mount_match.group(1)
                    key_name = key.split('.')[-1]
                    tags = f',mount_point={mount_point}'
                    field_key = key_name
                else:
                    field_key = key.replace('.', '_')

                # Prepare the line in InfluxDB line protocol
                line = f"{measurement}{tags} {field_key}={value} {timestamp}"
                lines.append(line)

    return lines

# Parallel processing function
def process_batch(batch):
    all_lines = []
    for metric_set in batch:
        lines = process_metrics(metric_set)
        all_lines.extend(lines)
    if all_lines:
        data = '\n'.join(all_lines)
        send_to_victoriametrics(data)

# Streaming and processing JSON data
batch_size = 5000
batch = []

with open(args.file_path, 'r') as file:
    objects = ijson.items(file, 'Data.item')
    with ThreadPoolExecutor(max_workers=2) as executor:  # Adjust max_workers as needed
        futures = []
        for metric_set in tqdm(objects, desc="Processing metrics"):
            batch.append(metric_set)
            if len(batch) >= batch_size:
                futures.append(executor.submit(process_batch, batch))
                batch = []
        if batch:  # Process any remaining metrics
            futures.append(executor.submit(process_batch, batch))

        # Wait for all threads to complete before exiting
        for future in as_completed(futures):
            future.result()

time.sleep(1)
print("Processing completed")

