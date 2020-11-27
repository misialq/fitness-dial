## Broker settings.
import os

broker_url = os.environ.get("CELERY_BROKER")
task_serializer = "json"
result_serializer = "json"
timezone = "UTC"
imports = ("connector.tasks",)

print("I'm here")
