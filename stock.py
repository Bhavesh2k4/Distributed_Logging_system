import random
import time
import uuid
from datetime import datetime, timedelta
import json
import threading
import pytz
import sys
import signal
import socket
from fluent import sender
from colorama import init, Fore, Style

init()

class LogColors:
    INFO = Style.NORMAL + Fore.WHITE
    WARN = Style.BRIGHT + Fore.YELLOW
    ERROR = Style.BRIGHT + Fore.RED
    FATAL = Style.BRIGHT + Fore.RED
    ALERT = Style.BRIGHT + Fore.RED
    HEARTBEAT = Style.BRIGHT + Fore.GREEN
    REGISTRATION = Style.BRIGHT + Fore.GREEN
    RESET = Style.RESET_ALL

EMOJI_INFO = f"{LogColors.INFO}[INFO]{LogColors.RESET} "
EMOJI_WARN = f"{LogColors.WARN}[WARN]{LogColors.RESET} "
EMOJI_ERROR = f"{LogColors.ERROR}[ERROR]{LogColors.RESET} "
EMOJI_FATAL = f"{LogColors.FATAL}[FATAL]{LogColors.RESET} "
EMOJI_HEARTBEAT = f"{LogColors.HEARTBEAT}[HEARTBEAT]{LogColors.RESET} "
EMOJI_REGISTRATION = f"{LogColors.REGISTRATION}[REGISTRATION]{LogColors.RESET} "
EMOJI_ALERT = f"{LogColors.ALERT}[ALERT]{LogColors.RESET} "

# Global variables
is_running = True
last_heartbeat = None
heartbeat_threshold = 10
hostname = socket.gethostname()
node_id = f"StockService_{hostname}"
service_name = "StockTradingService"
service_status = "UP"
log_counter = 1
fluent_sender = sender.FluentSender('services', host='localhost', port=24226)

def generate_log_id(service_name):
    global log_counter
    log_id = f"{service_name}_{log_counter}"
    log_counter += 1  # Increment the counter
    return log_id

def get_iso_timestamp():
    return datetime.now(pytz.UTC).isoformat()

def print_log(log_data):
    # Add emoji based on message type or log level
    emoji = ""
    if log_data.get("message_type") == "LOG":
        if log_data.get("log_level") == "INFO":
            emoji = EMOJI_INFO
        elif log_data.get("log_level") == "WARN":
            emoji = EMOJI_WARN
        elif log_data.get("log_level") == "ERROR":
            emoji = EMOJI_ERROR
        elif log_data.get("log_level") == "FATAL":
            emoji = EMOJI_FATAL
        elif log_data.get("log_level") == "ALERT":
            emoji = EMOJI_ALERT
    elif log_data.get("message_type") == "HEARTBEAT":
        emoji = EMOJI_HEARTBEAT
    elif log_data.get("message_type") == "REGISTRATION":
        emoji = EMOJI_REGISTRATION

    try:
        message_type = log_data.get("message_type", "UNKNOWN")
        log_level = log_data.get("log_level", "UNKNOWN")
    
        # Add logging to debug routing
        print(f"Processing log - Type: {message_type}, Level: {log_level}")
    
        if message_type == "LOG":
            if log_level in ["INFO", "WARN", "ERROR"]:
                fluent_sender.emit('service_logs', log_data)
            elif log_level in ["FATAL", "ALERT"]:
                fluent_sender.emit('alert_logs', log_data)
            else:
                print(f"WARNING: Unhandled log level: {log_level}")
        elif message_type in ["HEARTBEAT", "REGISTRATION"]:
            fluent_sender.emit('health_logs', log_data)
        else:
            print(f"WARNING: Unhandled message type: {message_type}")
    except Exception as e:
        print(f"Error processing log: {e}")
        print(f"Problematic log data: {log_data}")

def send_heartbeat(node_id, service_name, status="UP"):
    global last_heartbeat
    if status == "UP":
        last_heartbeat = time.time()
    log_data = {
        "node_id": node_id,
        "message_type": "HEARTBEAT",
        "status": status,
        "timestamp": get_iso_timestamp()
    }
    print_log(log_data)

def generate_log(node_id, service_name, log_level, message, additional_info=None):
    log = {
        "log_id": generate_log_id(service_name),
        "node_id": node_id,
        "log_level": log_level,
        "message_type": "LOG",
        "message": message,
        "service_name": service_name,
        "timestamp": get_iso_timestamp()
    }
    if additional_info:
        log.update(additional_info)
    print_log(log)

def register_service(node_id, service_name, status="UP"):
    log_data = {
        "message_type": "REGISTRATION",
        "node_id": node_id,
        "service_name": service_name,
        "status": status,
        "timestamp": get_iso_timestamp()
    }
    print_log(log_data)

def generate_info_log():
    stocks = [
        "ADANIENT", "ADANIPORTS", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO",
        "BAJFINANCE", "BAJAJFINSV", "BHARTIARTL", "BPCL", "BRITANNIA"
    ]
    info_messages = [
        f"Successfully processed buy order for {random.choice(stocks)} stock",
        f"Market data update received for {random.randint(1, 5)} stocks",
        f"User {str(uuid.uuid4())[:8]} accessed portfolio dashboard",
        f"Daily trading volume: {random.randint(10000, 50000)} transactions",
        f"New stock {random.choice(['GAIL','TATAPOWER','DMART'])} added to watchlist"
    ]
    return random.choice(info_messages)

def generate_warn_log():
    stocks = [
        "ADANIENT", "ADANIPORTS", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO"
    ]
    response_time = random.randint(100, 500)
    threshold = 100
    return {
        "message": f"API response time exceeding threshold for {random.choice(stocks)}",
        "response_time_ms": response_time,
        "threshold_limit_ms": threshold
    }

def generate_error_log():
    stocks = [
        "ADANIENT", "ADANIPORTS", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO"
    ]
    error_types = [
        {
            "message": f"Failed to execute trade order #{str(uuid.uuid4())[:8]}",
            "error_details": {
                "error_code": "TRADE_001",
                "error_message": "Insufficient funds in account"
            }
        },
        {
            "message": f"Database connection timeout for stock {random.choice(stocks)}",
            "error_details": {
                "error_code": "DB_001",
                "error_message": "Connection timed out after 30 seconds"
            }
        }
    ]
    return random.choice(error_types)

def generate_fatal_log():
    fatal_scenarios = [
        {
            "message": "Critical system failure detected in trading engine",
            "error_details": {
                "error_code": "FATAL_001",
                "error_message": "Trading engine core components non-responsive"
            }
        },
        {
            "message": "Catastrophic database corruption detected",
            "error_details": {
                "error_code": "FATAL_002",
                "error_message": "Database integrity check failed - immediate attention required"
            }
        }
    ]
    return random.choice(fatal_scenarios)

def recovery_procedure():
    global service_status
    service_status = "DOWN"
    register_service(node_id, service_name, "DOWN")
    
    # Simulate recovery steps
    recovery_steps = [
        "Initiating emergency shutdown",
        "Backing up critical data",
        "Resetting system state",
        "Reinitializing core components",
        "Performing integrity checks"
    ]
    
    for step in recovery_steps:
        generate_log(node_id, service_name, "INFO", f"Recovery: {step}")
        time.sleep(2)
    time.sleep(6)
    service_status = "UP"
    register_service(node_id, service_name, "UP")
    generate_log(node_id, service_name, "INFO", "Recovery complete: System restored")

def heartbeat_monitor():
    global last_heartbeat
    while is_running:
        if last_heartbeat and time.time() - last_heartbeat > heartbeat_threshold:
            generate_log(
                node_id,
                service_name,
                "ALERT",
                f"Missing heartbeat detected! Last heartbeat was {int(time.time() - last_heartbeat)} seconds ago"
            )
        time.sleep(1)

def heartbeat_thread():
    while is_running:
        send_heartbeat(node_id, service_name, service_status)
        time.sleep(5)  # Heartbeat every 5 seconds

def simulate_service_status():
    global service_status
    while is_running:
        if service_status == "UP" and random.random() < 0.05:  # 5% chance of fatal error
            fatal_log = generate_fatal_log()
            generate_log(
                node_id,
                service_name,
                "FATAL",
                fatal_log["message"],
                {"error_details": fatal_log["error_details"]}
            )
            recovery_procedure()
        
        time.sleep(10)

def signal_handler(signum, frame):
    global is_running
    print("\nShutting down service...")
    is_running = False
    register_service(node_id, service_name, "DOWN")
    sys.exit(0)

def run_service():
    global is_running
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Register service
    register_service(node_id, service_name, "UP")
    
    # Start heartbeat thread
    heartbeat_thread_instance = threading.Thread(target=heartbeat_thread)
    heartbeat_thread_instance.daemon = True
    heartbeat_thread_instance.start()
    
    # Start heartbeat monitor thread
    monitor_thread = threading.Thread(target=heartbeat_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Start service status simulation thread
    status_thread = threading.Thread(target=simulate_service_status)
    status_thread.daemon = True
    status_thread.start()
    
    try:
        while True:
            if service_status == "UP":
                log_type = random.choices(
                    ["INFO", "WARN", "ERROR"],
                    weights=[0.6, 0.25, 0.15],
                    k=1
                )[0]

                if log_type == "INFO":
                    generate_log(node_id, service_name, log_type, generate_info_log())
                
                elif log_type == "WARN":
                    warn_data = generate_warn_log()
                    generate_log(node_id, service_name, log_type, warn_data["message"], {
                        "response_time_ms": warn_data["response_time_ms"],
                        "threshold_limit_ms": warn_data["threshold_limit_ms"]
                    })
                
                elif log_type == "ERROR":
                    error_log = generate_error_log()
                    generate_log(node_id, service_name, log_type, error_log["message"], 
                            {"error_details": error_log["error_details"]})

            time.sleep(random.randint(1, 4))  # Random delay between logs

    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    run_service()
