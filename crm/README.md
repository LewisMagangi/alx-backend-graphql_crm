# CRM Celery Setup

## Prerequisites

- Install Redis and dependencies
- Run migrations: `python manage.py migrate`

## Start Celery Worker

``` bash
celery -A crm worker -l info
```

## Start Celery Beat

``` bash
celery -A crm beat -l info
```

## Verify Logs

Check `/tmp/crm_report_log.txt` for weekly CRM report output.
