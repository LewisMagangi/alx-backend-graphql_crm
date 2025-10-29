import datetime
import logging
import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Logs a timestamped heartbeat message and checks GraphQL endpoint health using gql client."""

    # Ensure log directory exists
    log_dir = "C:/tmp"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "crm_heartbeat_log.txt")

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

    # Optional console print for debug
    print(message.strip())
