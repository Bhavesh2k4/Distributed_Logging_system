# Microservices Distributed Logging System

## Kafka-Fluentd Microservices Setup Guide

A fully functional microservices-based **distributed logging system** using **Kafka**, **Fluentd**, and **ElasticSearch**, designed for scalable log ingestion and monitoring.

---

## 📦 Components

| Component      | Description                              |
|----------------|------------------------------------------|
| `payment.py`   | Simulates a payment gateway (logs transactions, alerts) |
| `stock.py`     | Simulates a stock trading service         |
| `user.py`      | Simulates a user profile management service |
| `consumer_es.py` | Consumes logs from Kafka and indexes them in ElasticSearch |
| `*.conf`       | Fluentd configuration files for each service |

---

## 🧠 Log Types Handled

| Log Type     | Kafka Topic     | Description                                  |
|--------------|------------------|----------------------------------------------|
| `INFO`       | `service_logs`   | Normal system activity                       |
| `WARN`       | `service_logs`   | Latency or non-critical anomalies            |
| `ERROR`      | `service_logs`   | Recoverable service errors                   |
| `FATAL`      | `alert_logs`     | Critical failures, triggers recovery steps   |
| `ALERT`      | `alert_logs`     | Heartbeat misses, threshold warnings         |
| `HEARTBEAT`  | `health_logs`    | Regular ping from services                   |
| `REGISTRATION` | `health_logs`  | Service boot-up/shutdown announcements       |


## Prerequisites

- Apache Kafka
- Fluentd
- ElasticSearch
- Python 3.x
- Ubuntu 22.x or 24.x

## Starting Services

Start Kafka , Fluentd & ElasticSearch services:

```bash
# Start services
sudo systemctl start kafka
sudo systemctl start fluentd.service
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

# Verify services are running
sudo systemctl status kafka
sudo systemctl status fluentd.service
sudo systemctl status elasticsearch
```

```bash
# Elastic Search is succesfully installed if this command gets reply from the server
curl -X GET "http://127.0.0.1:9200"
```

## Create Kafka Topics

Create the required Kafka topics:

```bash
# Create health_logs topic
/usr/local/kafka/bin/kafka-topics.sh --create --topic health_logs \
    --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Create service_logs topic
/usr/local/kafka/bin/kafka-topics.sh --create --topic service_logs \
    --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Create alert_logs topic
/usr/local/kafka/bin/kafka-topics.sh --create --topic alert_logs \
    --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

## Running the Applications

1. Start the microservices:
```bash
python3 payment.py
python3 stock.py
python3 user.py
```

2. Start Fluentd configurations:
```bash
fluentd -c p_fluent.conf
fluentd -c s_fluent.conf
fluentd -c u_fluent.conf
```

3. Start the consumer for ElasticSearch
```bash
python3 consumer_es.py
```

## Monitoring Logs

Monitor each topic's logs:

```bash
# Monitor service logs
/usr/local/kafka/bin/kafka-console-consumer.sh --topic service_logs \
    --bootstrap-server localhost:9092 --from-beginning

# Monitor alert logs
/usr/local/kafka/bin/kafka-console-consumer.sh --topic alert_logs \
    --bootstrap-server localhost:9092 --from-beginning

# Monitor health logs
/usr/local/kafka/bin/kafka-console-consumer.sh --topic health_logs \
    --bootstrap-server localhost:9092 --from-beginning
```

## Topic Management

### List All Topics
```bash
/usr/local/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Delete Topics
If you need to recreate topics, delete them first:

```bash
# Delete service_logs topic
/usr/local/kafka/bin/kafka-topics.sh --delete --topic service_logs \
    --bootstrap-server localhost:9092

# Delete alert_logs topic
/usr/local/kafka/bin/kafka-topics.sh --delete --topic alert_logs \
    --bootstrap-server localhost:9092

# Delete health_logs topic
/usr/local/kafka/bin/kafka-topics.sh --delete --topic health_logs \
    --bootstrap-server localhost:9092
```

> **Note:** It's recommended to delete and recreate topics between runs to avoid buffer issues.

## Stopping Services

When finished, stop the services:

```bash
sudo systemctl stop kafka
sudo systemctl stop fluentd.service
sudo systemctl stop elasticsearch
```

## Troubleshooting

If you encounter issues:
1. Ensure all services are running using systemctl status
2. Check if topics are properly created using the list command
3. Verify that all ports (9092 for Kafka, Fluentd ports) are available
4. Check service logs for any error messages
