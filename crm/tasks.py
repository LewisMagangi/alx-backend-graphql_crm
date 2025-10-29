import requests
from datetime import datetime
from django.conf import settings
from celery import shared_task

@shared_task
def generate_crm_report():
    query = '''
    query {
      allCustomers {
        totalCount
      }
      allOrders {
        totalCount
        edges {
          node {
            totalAmount
          }
        }
      }
    }
    '''
    endpoint = 'http://localhost:8000/graphql/'
    response = requests.post(endpoint, json={'query': query}, headers={'Content-Type': 'application/json'})
    data = response.json().get('data', {})
    customers = data.get('allCustomers', {}).get('totalCount', 0)
    orders = data.get('allOrders', {}).get('totalCount', 0)
    revenue = sum(float(edge['node']['totalAmount']) for edge in data.get('allOrders', {}).get('edges', []))
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"
    with open('/tmp/crm_report_log.txt', 'a') as log:
        log.write(log_line)
