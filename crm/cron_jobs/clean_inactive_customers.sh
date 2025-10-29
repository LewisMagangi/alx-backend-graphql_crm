#!/bin/bash
# Script to delete inactive customers (no orders in the past year)

# Move to project root (2 levels up from cron_jobs)
cd "$(dirname "$0")/../.." || exit 1

# Activate virtual environment
source venv/Scripts/activate

echo "Using Python from: $(which python)"

LOG_FILE="/tmp/customer_cleanup_log.txt"

deleted_count=$(python manage.py shell <<'EOF'
import os, sys, django
from datetime import timedelta
from django.utils import timezone

# Make sure Python can find the project package
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from crm.models import Customer

cutoff_date = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(orders__isnull=True) | Customer.objects.filter(orders__created_at__lt=cutoff_date)
count = inactive_customers.distinct().count()
inactive_customers.distinct().delete()
print(count)
EOF
)

echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $deleted_count inactive customers" >> "$LOG_FILE"
echo "Cleanup complete. Deleted $deleted_count inactive customers."
echo "Log written to $LOG_FILE"
