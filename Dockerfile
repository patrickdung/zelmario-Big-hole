# Use a base image, for example, Ubuntu
# FROM ubuntu:20.04
FROM docker.io/library/ubuntu:22.04

# Set the working directory
WORKDIR /app

# Copy the necessary files into the container
COPY ftdc_decoder /app/ftdc_decoder
COPY run_scripts.sh /scripts/run_scripts.sh
COPY ftdc_parser.py /scripts/ftdc_parser.py
COPY get_url.py /scripts/get_url.py
COPY metrics_to_get.txt /app/metrics_to_get.txt

# Make sure the scripts and binaries have the correct permissions
# Install Python and any necessary dependencies
RUN set -eux && \
    chmod +x /app/ftdc_decoder /scripts/run_scripts.sh && \
    apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && pip3 install ijson influxdb-client tqdm \
    && apt-get -y clean

# Set the entrypoint to run your script
ENTRYPOINT ["/scripts/run_scripts.sh"]
