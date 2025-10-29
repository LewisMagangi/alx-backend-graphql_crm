import requests
import json
from datetime import datetime

# Adjust these as needed for your deployment
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql/"
LOG_FILE = "/tmp/low_stock_updates_log.txt"

def update_low_stock():
        mutation = '''
        mutation {
            updateLowStockProducts {
                updatedProducts {
                    id
                    name
                    stock
                }
                message
            }
        }
        '''
        try:
                response = requests.post(
                        GRAPHQL_ENDPOINT,
                        json={"query": mutation},
                        headers={"Content-Type": "application/json"}
                )
                data = response.json()
                updates = data.get("data", {}).get("updateLowStockProducts", {})
                products = updates.get("updatedProducts", [])
                message = updates.get("message", "")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(LOG_FILE, "a") as log:
                        log.write(f"[{timestamp}] {message}\n")
                        for p in products:
                                log.write(f"    Updated: {p['name']} (ID: {p['id']}) - New stock: {p['stock']}\n")
        except Exception as e:
                with open(LOG_FILE, "a") as log:
                        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: {str(e)}\n")
import datetime
import logging
import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Logs a timestamped heartbeat message to /tmp/crm_heartbeat_log.txt and checks GraphQL health."""

    # Ensure /tmp exists
    log_path = "/tmp/crm_heartbeat_log.txt"  # <-- exact string included
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Prepare heartbeat message
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    # Append heartbeat to file
    with open(log_path, "a") as f:
        f.write(message)

    logging.info(message.strip())

    # GraphQL health check using gql client
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            use_json=True,
            timeout=5,
            verify=True,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql("{ hello }")
        result = client.execute(query)
        logging.info(f"GraphQL health check successful: {result}")
    except Exception as e:
        logging.error(f"GraphQL health check failed: {e}")

    # Optional console print
    print(message.strip())
