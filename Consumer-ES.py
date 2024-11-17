import json
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import sys
from datetime import datetime
import pytz
from colorama import init, Fore, Style


init()

class LogColors:
    INFO = Style.NORMAL + Fore.WHITE
    WARN = Style.BRIGHT + Fore.YELLOW
    ERROR = Style.BRIGHT + Fore.RED
    FATAL = Style.BRIGHT + Fore.RED
    ALERT = Style.BRIGHT + Fore.MAGENTA
    HEARTBEAT = Style.BRIGHT + Fore.GREEN
    REGISTRATION = Style.BRIGHT + Fore.CYAN
    RESET = Style.RESET_ALL

EMOJI_INFO = f"{LogColors.INFO}[INFO]{LogColors.RESET} "
EMOJI_WARN = f"{LogColors.WARN}[WARN]{LogColors.RESET} "
EMOJI_ERROR = f"{LogColors.ERROR}[ERROR]{LogColors.RESET} "
EMOJI_FATAL = f"{LogColors.FATAL}[FATAL]{LogColors.RESET} "
EMOJI_HEARTBEAT = f"{LogColors.HEARTBEAT}[HEARTBEAT]{LogColors.RESET} "
EMOJI_REGISTRATION = f"{LogColors.REGISTRATION}[REGISTRATION]{LogColors.RESET} "
EMOJI_ALERT = f"{LogColors.ALERT}[ALERT]{LogColors.RESET} "

KAFKA_BROKER = 'localhost:9092'
TOPICS = ['service_logs', 'alert_logs', 'health_logs']
ELASTICSEARCH_HOST = 'http://localhost:9200'

es = Elasticsearch([ELASTICSEARCH_HOST])

IST = pytz.timezone('Asia/Kolkata')

def convert_utc_to_ist(utc_timestamp):
    """Convert UTC timestamp to IST, considering if it is naive or aware"""
    if isinstance(utc_timestamp, datetime):
        if utc_timestamp.tzinfo is None:
            utc_time = pytz.utc.localize(utc_timestamp)
        else:
            # If aware, just convert to IST
            utc_time = utc_timestamp
        ist_time = utc_time.astimezone(IST)
        return ist_time.isoformat()
    return utc_timestamp 

def display_log(log_data):
    emoji = ""
    log_level = log_data.get("log_level", "UNKNOWN")
    message_type = log_data.get("message_type", "UNKNOWN")

    if message_type == "LOG":
        if log_level == "INFO":
            emoji = EMOJI_INFO
        elif log_level == "WARN":
            emoji = EMOJI_WARN
        elif log_level == "ERROR":
            emoji = EMOJI_ERROR
        elif log_level == "FATAL":
            emoji = EMOJI_FATAL
        elif log_level == "ALERT":
            emoji = EMOJI_ALERT
    elif message_type == "HEARTBEAT":
        emoji = EMOJI_HEARTBEAT
    elif message_type == "REGISTRATION":
        emoji = EMOJI_REGISTRATION

    timestamp = log_data.get('timestamp', datetime.utcnow().isoformat())
    timestamp_ist = convert_utc_to_ist(datetime.fromisoformat(timestamp))

    print(f"{emoji}{timestamp_ist} - {log_data.get('node_id')} - {log_data.get('message')}")

def get_elasticsearch_index(log_data):
    """Get Elasticsearch index based on log type"""
    log_type = log_data.get('log_type', 'service')
    if log_type == 'alert':
        return 'alert_logs'
    elif log_type == 'health':
        return 'health_logs'
    else:
        return 'service_logs'

def store_in_elasticsearch(log_data):
    try:
        if 'timestamp' not in log_data:
            log_data['timestamp'] = datetime.utcnow().isoformat()

        index_name = get_elasticsearch_index(log_data)
        response = es.index(index=index_name, document=log_data)
        if response.get('result') != 'created':
            print(f"{EMOJI_ERROR}Failed to index log: {response}")
    except Exception as e:
        print(f"{EMOJI_ERROR}Elasticsearch error: {e}")

def consume_logs():
    logs = []
    try:
        consumer = KafkaConsumer(
            *TOPICS,
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id="log_consumer_group"
        )
        print(f"Connected to Kafka broker at {KAFKA_BROKER}. Listening to topics: {', '.join(TOPICS)}")
        for message in consumer:
            log_data = message.value
            logs.append(log_data)
            store_in_elasticsearch(log_data)

            logs_sorted = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=False)
         
            for log in logs_sorted:
                display_log(log)
            
    except KeyboardInterrupt:
        print("\nConsumer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"{EMOJI_ERROR}Error while consuming logs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not es.ping():
        print(f"{EMOJI_ERROR}Unable to connect to Elasticsearch at {ELASTICSEARCH_HOST}")
        sys.exit(1)

    print(f"Connected to Elasticsearch at {ELASTICSEARCH_HOST}")
    consume_logs()

