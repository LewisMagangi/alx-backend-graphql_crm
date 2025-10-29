import datetime
import logging
import gql
import requests
import os
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

def log_crm_heartbeat():
    """Logs a timestamped heartbeat message to confirm CRM health."""
    log_dir = "C:/tmp"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "crm_heartbeat_log.txt")

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    with open(log_path, "a") as f:
        f.write(message)

    # Optional GraphQL health check
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5,
        )
        if response.status_code == 200:
            logging.info("GraphQL endpoint responded OK.")
        else:
            logging.warning(f"GraphQL health check failed: {response.status_code}")
    except Exception as e:
        logging.error(f"GraphQL health check error: {e}")

    print(message.strip())
