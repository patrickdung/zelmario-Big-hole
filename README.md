# Big-hole
View all MongoDB FTDC Metrics that you want in Grafana.

I've been using the Keyhole tool from @simagix (Ken Chen) for a while and it's great! but with the new versions of MongoDB, sometimes I need to see more metrics to analyze specific issues.
Based on the same idea, I've written this small script to gather additional metrics and be able to obtain all the metrics that I need.

The script sends all the metrics data to a Dockerized InfluxDB instance. I chose InfluxDB because it's very simple and comes with its own dashboard, which is very useful for viewing the metrics and constructing queries to use in Grafana.

## Prerequisites
- Docker and Docker-compose

## Installation
1. Clone the repository
2. Navigate to the project directory
3. Create a diagnostic.data directory `mkdir -p ./diagnostic.data/`
4. Copy FTDC files to under directory diagnostic.data: `cp $SOMEWHERE/metrics.* ./diagnostic.data/`
5. Make the main script executable: `chmod +x ftdc_decoder bighole.sh`
6. Build the docker images `docker-compose build`
7. Run the script`./bighole.sh`

## Usage
The script will decode all the diagnostic data files and launch three docker containers:

```bash
zelmar@LAPTOP-MD0FVN06:~/ftdc_decoder$ ./bighole.sh
WARN[0000] /home/zelmar/ftdc_decoder/docker-compose.yml: `version` is obsolete
[+] Running 4/4
 ✔ Network ftdc_decoder_default                Created                                                                                                                                   0.0s
 ✔ Container ftdc_decoder-influxdb-1           Started                                                                                                                                   0.7s
 ✔ Container ftdc_decoder-metrics-processor-1  Started                                                                                                                                   1.0s
 ✔ Container ftdc_decoder-grafana-1            Started                                                                                                                                   1.1s
WARN[0000] /home/zelmar/ftdc_decoder/docker-compose.yml: `version` is obsolete
metrics-processor-1  | This can take some time... ☕
metrics-processor-1  |
metrics-processor-1  | Decoding MongoDB FTDC data...
metrics-processor-1  | Chunk processed
Processing metrics: 221it [00:03, 55.46it/s]
metrics-processor-1  | Chunk processed
metrics-processor-1  | Access your dashboard at: http://localhost:3001/d/ddnw277huiv40ae/ftdc-dashboard?orgId=1&from=1716347462000&to=1716379922000
metrics-processor-1  | Press Ctrl-C when you've finished to analyze the dashboard.

```

To see the default dashboard you can go to the link that the script shows when it finish the process:

![Screenshoot](https://github.com/zelmario/Big-hole/blob/main/big_hole.png?raw=true)


## How to get more metrics
There is a file named `metrics_to_get.txt` that contains the list of metrics to retrieve. If you want to gather more metrics, simply add the name of the desired metric to this file.
You'll find a complete list of all available metrics in another file called `metrics.txt`. Just add the metric you want to retrieve to `metrics_to_get.txt`, and the script will collect it.

You can use InfluxDB to view the metrics and construct the queries needed to display them in Grafana.
```bash
http://localhost:8086/
user: zelmario
pass: password
```

![Screenshoot](https://github.com/zelmario/Big-hole/blob/main/influxdb.png?raw=true)


You can edit the dashboard by login in to grafana:
```bash
http://localhost:3001/
user: admin
pass: admin
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
Contributions are welcome! Since I'm not a professional developer, your feedback is valuable. If you're a programmer and notice any mistakes or have ideas to enhance the script, please feel free to contribute! :)

