import datetime
import os

from celery import Celery
from celery.utils.log import get_task_logger

from .utils.activity import request_all_activities_data
from .utils.authentication import get_valid_token
from .utils.common import DATETIME_FORMAT_COMMON
from .utils.measurements import request_all_measurements_data
from .utils.sleep import request_all_sleep_data, DATETIME_FORMAT

CELERY_BROKER = os.environ.get("CELERY_BROKER")
LOGGER = get_task_logger(__name__)
app = Celery("tasks", broker=CELERY_BROKER)


@app.task(name="auto_appli_44", queue="sleep_tasks")
def celery_appli_44_sleep(json_body):
    user_id = json_body["userid"]
    start_date = datetime.datetime.fromtimestamp(int(json_body["startdate"]))
    end_date = datetime.datetime.fromtimestamp(int(json_body["enddate"]))

    # fetch a valid token
    LOGGER.info("Fetching valid token for user: %s", user_id)
    access_token_data = get_valid_token(user_id)

    # make data request
    LOGGER.info(
        "Fetching sleep entries for dates: %s to %s...",
        start_date.strftime(DATETIME_FORMAT),
        end_date.strftime(DATETIME_FORMAT),
    )
    raw_counter, summary_counter = request_all_sleep_data(
        access_token=access_token_data["access_token"],
        user_id=user_id,
        start_date=None,
        end_date=None,
        from_notification=True,
    )
    LOGGER.info(
        "Fetched and updated %s raw sleep entries and %s summary sleep entries",
        raw_counter,
        summary_counter,
    )
    return


@app.task(name="auto_appli_1", queue="default")
def celery_appli_1_measurements(json_body):
    user_id = json_body["userid"]
    start_date = datetime.datetime.fromtimestamp(int(json_body["startdate"]))
    end_date = datetime.datetime.fromtimestamp(int(json_body["enddate"]))

    # fetch a valid token
    LOGGER.info("Fetching valid token for user: %s", user_id)
    access_token_data = get_valid_token(user_id)

    # make data request
    LOGGER.info(
        "Fetching measurements of type 'weight' for dates %s to %s...",
        start_date.strftime(DATETIME_FORMAT),
        end_date.strftime(DATETIME_FORMAT),
    )
    measurements_counter = request_all_measurements_data(
        access_token_data["access_token"],
        user_id=user_id,
        start_date=None,
        end_date=None,
        meas_type="weight",
        offset=None,
        from_notification=True,
    )
    LOGGER.info(
        "Fetched and updated %s weight measurement entries.", measurements_counter,
    )
    return


@app.task(name="auto_appli_16", queue="default")
def celery_appli_16_activities(json_body):
    user_id = json_body["userid"]
    date = json_body["date"]

    # fetch a valid token
    LOGGER.info("Fetching valid token for user: %s", user_id)
    access_token_data = get_valid_token(user_id)

    # make data request
    LOGGER.info("Fetching activities with a date %s...", date)
    raw_counter, summary_counter = request_all_activities_data(
        access_token_data["access_token"],
        user_id=user_id,
        start_date=None,
        end_date=None,
        from_notification=True,
    )
    LOGGER.info(
        "Fetched and updated %s raw activity entries and %s summary activity entries",
        raw_counter,
        summary_counter,
    )
    return


@app.task(name="man_sleep", queue="default")
def celery_request_all_sleep_data(access_token_data, user_id, start_date, end_date):
    LOGGER.debug("Celery task received: sleep.")
    LOGGER.info(
        "Fetching sleep entries for dates: %s to %s...", start_date, end_date,
    )

    start_date = datetime.datetime.strptime(start_date, DATETIME_FORMAT_COMMON)
    end_date = datetime.datetime.strptime(end_date, DATETIME_FORMAT_COMMON)

    raw_counter, summary_counter = request_all_sleep_data(
        access_token=access_token_data["access_token"],
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    LOGGER.debug(
        f"Celery task finished: sleep. Fetched {raw_counter} raw and {summary_counter} summary entries."
    )
    return


@app.task(name="man_measurement", queue="default")
def celery_request_all_measurement_data(
    access_token_data, user_id, start_date, end_date, measurement_type
):
    LOGGER.debug("Celery task received: measurements.")
    LOGGER.info(
        "Fetching measurements of type '%s' for dates %s to %s...",
        measurement_type,
        start_date,
        end_date,
    )

    start_date = datetime.datetime.strptime(start_date, DATETIME_FORMAT_COMMON)
    end_date = datetime.datetime.strptime(end_date, DATETIME_FORMAT_COMMON)

    measurements_count = request_all_measurements_data(
        access_token=access_token_data["access_token"],
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        meas_type=measurement_type,
    )
    LOGGER.debug(
        f"Celery task finished: measurements. Fetched and updated {measurements_count} "
        f"entries for the following measurement type: {measurement_type}."
    )
    return


@app.task(name="man_activity", queue="default")
def celery_request_all_activity_data(access_token_data, user_id, start_date, end_date):
    LOGGER.debug("Celery task received: activity.")
    LOGGER.info(
        "Fetching activity entries for dates: %s to %s...", start_date, end_date,
    )

    start_date = datetime.datetime.strptime(start_date, DATETIME_FORMAT_COMMON)
    end_date = datetime.datetime.strptime(end_date, DATETIME_FORMAT_COMMON)

    raw_counter, summary_counter = request_all_activities_data(
        access_token=access_token_data["access_token"],
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    LOGGER.debug(
        f"Celery task finished: sleep. Fetched {raw_counter} raw and {summary_counter} summary entries."
    )
    return
