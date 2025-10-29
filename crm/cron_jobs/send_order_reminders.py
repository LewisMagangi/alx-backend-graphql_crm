#!/usr/bin/env python3
"""
send_order_reminders.py
Fetches pending orders from the last 7 days using a GraphQL query
and logs reminders to /tmp/order_reminders_log.txt.
"""

import os
import sys
import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# --- Setup Logging ---
import tempfile, os
LOG_FILE = os.path.join(tempfile.gettempdir(), "order_reminders_log.txt")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- GraphQL Endpoint ---
GRAPHQL_URL = "http://localhost:8000/graphql"

# --- Date Range: Orders in the last 7 days ---
today = datetime.date.today()
seven_days_ago = today - datetime.timedelta(days=7)

# --- Define GraphQL Query ---
query = gql(f"""
{{
  orders(orderDate_Gte: "{seven_days_ago}", orderDate_Lte: "{today}") {{
    id
    customer {{
      email
    }}
  }}
}}
""")

def main():
    try:
        # --- Setup GraphQL Client ---
        transport = RequestsHTTPTransport(
            url=GRAPHQL_URL,
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # --- Execute Query ---
        result = client.execute(query)
        orders = result.get("orders", [])

        if not orders:
            logging.info("No recent orders found.")
        else:
            for order in orders:
                order_id = order.get("id")
                customer_email = order.get("customer", {}).get("email")
                logging.info(f"Reminder: Order {order_id} for customer {customer_email}")

        print("Order reminders processed!")

    except Exception as e:
        logging.error(f"Error fetching or logging order reminders: {e}")
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
