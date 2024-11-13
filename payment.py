import random
import time
import uuid
from datetime import datetime, timedelta
import json
import threading
import pytz
import sys
import signal

# Emoji indicators
EMOJI_INFO = "[INFO] "
EMOJI_WARN = "[WARN] "
EMOJI_ERROR = "[ERROR] "
EMOJI_FATAL = "[FATAL] "
EMOJI_HEARTBEAT = "[HEARTBEAT] "
EMOJI_REGISTRATION = "[REGISTRATION] "
EMOJI_ALERT = "[ALERT] "

# Global variables
is_running = True
last_heartbeat = None
heartbeat_threshold = 10  # seconds
node_id = f"PaymentService_{str(uuid.uuid4())[:8]}"
service_name = "PaymentGatewayService"
service_status = "UP"

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

    print(f"{emoji}{json.dumps(log_data, indent=2)}")

def send_heartbeat(node_id, service_name, status="UP"):
    global last_heartbeat
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
        "log_id": str(uuid.uuid4()),
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
    payment_methods = ["CREDIT_CARD", "DEBIT_CARD", "UPI", "NET_BANKING", "WALLET"]
    payment_providers = ["VISA", "MASTERCARD", "AMEX", "RUPAY", "PAYTM"]
    transaction_amounts = [random.randint(100, 10000) for _ in range(5)]
    
    info_messages = [
        f"Payment processed successfully - Amount: ₹{random.choice(transaction_amounts)} via {random.choice(payment_methods)}",
        f"New payment provider {random.choice(payment_providers)} integration health check completed",
        f"User {str(uuid.uuid4())[:8]} wallet recharged with ₹{random.choice(transaction_amounts)}",
        f"Daily transaction count: {random.randint(1000, 5000)} payments processed",
        f"Payment reconciliation completed for {random.choice(payment_providers)}"
    ]
    return random.choice(info_messages)

def generate_warn_log():
    payment_methods = ["CREDIT_CARD", "DEBIT_CARD", "UPI", "NET_BANKING"]
    response_time = random.randint(2000, 5000)
    threshold = 3000
    warn_scenarios = [
        {
            "message": f"High latency detected in {random.choice(payment_methods)} gateway",
            "response_time_ms": response_time,
            "threshold_limit_ms": threshold
        },
        {
            "message": "Payment gateway approaching rate limit threshold",
            "response_time_ms": response_time,
            "threshold_limit_ms": threshold
        }
    ]
    return random.choice(warn_scenarios)

def generate_error_log():
    payment_providers = ["VISA", "MASTERCARD", "AMEX", "RUPAY", "PAYTM"]
    error_types = [
        {
            "message": f"Payment authorization failed for transaction #{str(uuid.uuid4())[:8]}",
            "error_details": {
                "error_code": "PAY_001",
                "error_message": "Card declined by issuing bank"
            }
        },
        {
            "message": f"Payment gateway connection timeout with {random.choice(payment_providers)}",
            "error_details": {
                "error_code": "PAY_002",
                "error_message": "Gateway connection timeout after 30 seconds"
            }
        },
        {
            "message": "Invalid payment token detected",
            "error_details": {
                "error_code": "PAY_003",
                "error_message": "Payment token validation failed - possible security breach"
            }
        }
    ]
    return random.choice(error_types)

def generate_fatal_log():
    fatal_scenarios = [
        {
            "message": "Critical failure in payment processing system",
            "error_details": {
                "error_code": "FATAL_001",
                "error_message": "Payment gateway core services non-responsive"
            }
        },
        {
            "message": "Payment security system breach detected",
            "error_details": {
                "error_code": "FATAL_002",
                "error_message": "Multiple suspicious transactions detected - initiating emergency shutdown"
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
        "Initiating payment gateway shutdown",
        "Securing payment channels",
        "Backing up transaction logs",
        "Verifying payment security protocols",
        "Restarting payment processors",
        "Validating payment gateway integrations"
    ]
    
    for step in recovery_steps:
        generate_log(node_id, service_name, "INFO", f"Recovery: {step}")
        time.sleep(2)
    
    service_status = "UP"
    register_service(node_id, service_name, "UP")
    generate_log(node_id, service_name, "INFO", "Recovery complete: Payment gateway restored")

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
        if service_status == "UP" and random.random() < 0.03:  # 3% chance of fatal error
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
    print("\nShutting down payment gateway service...")
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
                    weights=[0.85, 0.1, 0.05],
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

            time.sleep(random.randint(1, 2))

    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    run_service()