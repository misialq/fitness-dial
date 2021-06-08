from datetime import datetime, timedelta
import json
import logging

import requests
from django.core.exceptions import FieldError
from django.utils.timezone import make_aware


class APIError(Exception):
    pass


DATETIME_FORMAT_COMMON = "%Y-%m-%dT%H:%M:%S%z"
LOGGER = logging.getLogger(__name__)


def parse_dates(start_date: str, end_date: str) -> (str, str):
    if not end_date:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=11)

    if not start_date:
        start_date = end_date - timedelta(hours=24)
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=18)

    return (
        make_aware(start_date).strftime(DATETIME_FORMAT_COMMON),
        make_aware(end_date).strftime(DATETIME_FORMAT_COMMON),
    )


def extract_and_parse_dates(request) -> (str, str):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    start_date, end_date = parse_dates(start_date, end_date)
    return start_date, end_date


def send_data_request(endpoint: str, params: dict, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.post(endpoint, data=params, headers=headers,)
    LOGGER.debug("Endpoint: %s, params: %s", endpoint, params)
    if response.status_code > 300:
        raise APIError(f"API returned error {response.status_code}: {response.reason}")

    data = json.loads(response.text)
    if data["status"] != 0:
        raise APIError(
            f"An error occurred while fetching data from {endpoint}. The reason was: {data['error']}"
        )
    return data["body"]


def prepare_date_pairs(db_model, start_date, end_date, from_notification):
    if from_notification:
        # find the last available entry in the DB
        try:
            start_date = (
                db_model.objects.filter(measured_at__isnull=False)
                .latest("measured_at")
                .measured_at
            )
        # sleep entries do not have measured_at attribute
        except FieldError as e:
            LOGGER.debug("Error: %s - will try to fetch by end date.", e)
            start_date = (
                db_model.objects.filter(end_date__isnull=False)
                .latest("end_date")
                .end_date
            )
        end_date = make_aware(datetime.now())
        LOGGER.debug(
            "Request from notification - start and end dates will be reset to %s and %s.",
            start_date.strftime(DATETIME_FORMAT_COMMON),
            end_date.strftime(DATETIME_FORMAT_COMMON),
        )

    time_diff = end_date - start_date
    if int(time_diff.days) > 0:
        time_range = range(int(time_diff.days + 1))
    else:
        time_range = range(2)
    all_dates = [start_date + timedelta(n) for n in time_range]
    LOGGER.debug("All dates: %s", all_dates)
    date_pairs = list(zip(all_dates, all_dates[1:]))
    LOGGER.debug("Date pairs: %s", date_pairs)
    return date_pairs
