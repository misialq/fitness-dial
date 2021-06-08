import os

from kombu import Queue, Exchange

broker_url = os.environ.get("CELERY_BROKER")

task_serializer = "json"
task_default_queue = "default"
task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("sleep_tasks", Exchange("sleep_tasks"), routing_key="sleep"),
)

# TODO: this just does not work. The only way to actually make it work
# was to explicitly specify queue names in the task decorator at every view
# task_routes = {
#     "man_*": {"queue": "default", "exchange": "default", "routing_key": "default",},
#     "auto_appli_1*": {
#         "queue": "default",
#         "exchange": "default",
#         "routing_key": "default",
#     },
#     "auto_appli_44": {
#         "queue": "sleep_tasks",
#         "exchange": "sleep_tasks",
#         "routing_key": "sleep",
#     },
# }

result_serializer = "json"
timezone = "UTC"
imports = ("connector.tasks",)
