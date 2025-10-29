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
