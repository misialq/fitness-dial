import os
from datetime import datetime
import logging

from django.db import IntegrityError
from django.utils.timezone import make_aware

from .common import send_data_request, prepare_date_pairs
from ..models import SleepSummary, SleepRaw

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DATETIME_FORMAT_SLEEP = "%Y-%m-%d"
SLEEP_DATA_FIELDS = [
    "breathing_disturbances_intensity",
    "deepsleepduration",
    "durationtosleep",
    "durationtowakeup",
    "hr_average",
    "hr_max",
    "hr_min",
    "lightsleepduration",
    "remsleepduration",
    "rr_average",
    "rr_max",
    "rr_min",
    "sleep_score",
    "snoring",
    "snoringepisodecount",
    "wakeupcount",
    "wakeupduration",
]
SLEEP_DATA_FIELDS_RAW = ["hr", "rr", "snoring"]
SLEEP_PHASES = {0: "AWAKE", 1: "LIGHT", 2: "DEEP", 3: "REM"}
DEVICE_TYPES = {16: "TRACKER", 32: "SLEEP_MONITOR"}
LOGGER = logging.getLogger(__name__)
WITHINGS_API_URL = os.environ.get("WITHINGS_API_URL", "https://wbsapi.withings.net/v2")


def get_sleep_data_raw(
    access_token: str,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    from_notification: bool = False,
) -> int:

    date_pairs = prepare_date_pairs(SleepRaw, start_date, end_date, from_notification)

    counter = 0
    for sub_start_date, sub_end_date in date_pairs:
        req_params = {
            "action": "get",
            "startdate": int(sub_start_date.timestamp()),
            "enddate": int(sub_end_date.timestamp()),
            "data_fields": ",".join(SLEEP_DATA_FIELDS_RAW),
        }

        data = send_data_request(
            os.path.join(WITHINGS_API_URL, "sleep"), req_params, access_token
        )

        for entry in data["series"]:
            LOGGER.debug(entry)
            start_date_entry = make_aware(
                datetime.fromtimestamp(entry.get("startdate"))
            )
            end_date_entry = make_aware(datetime.fromtimestamp(entry.get("enddate")))
            potential_entry = SleepRaw.objects.filter(
                start_date=start_date_entry, end_date=end_date_entry
            )
            sleep_phase_id = entry.get("state")
            if len(potential_entry) == 0:
                new_sleep_raw = SleepRaw(
                    device_type=entry.get("model"),
                    device_id=entry.get("model_id"),
                    user_id=user_id,
                    start_date=start_date_entry,
                    end_date=end_date_entry,
                    sleep_phase=SLEEP_PHASES[sleep_phase_id],
                    sleep_phase_id=sleep_phase_id,
                    hr_series=[
                        prepare_timepoint_dict(x, y) for x, y in entry.get("hr").items()
                    ],
                    rr_series=[
                        prepare_timepoint_dict(x, y) for x, y in entry.get("rr").items()
                    ],
                    snoring_series=[
                        prepare_timepoint_dict(x, y)
                        for x, y in entry.get("snoring").items()
                    ],
                )
                new_sleep_raw.save()
                counter += 1
    return counter


def prepare_timepoint_dict(timestamp, value):
    return {
        "timestamp": make_aware(datetime.fromtimestamp(int(timestamp))).strftime(
            DATETIME_FORMAT
        ),
        "value": value,
    }


def get_sleep_data_summary(
    access_token: str,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    from_notification: bool = False,
) -> int:

    date_pairs = prepare_date_pairs(
        SleepSummary, start_date, end_date, from_notification
    )

    counter = 0
    for sub_start_date, sub_end_date in date_pairs:
        req_params = {
            "action": "getsummary",
            "startdateymd": sub_start_date.strftime(DATETIME_FORMAT_SLEEP),
            "enddateymd": sub_end_date.strftime(DATETIME_FORMAT_SLEEP),
            "data_fields": ",".join(SLEEP_DATA_FIELDS),
        }

        data = send_data_request(
            os.path.join(WITHINGS_API_URL, "sleep"), req_params, access_token
        )

        for entry in data["series"]:
            LOGGER.debug(entry)
            entry_date = datetime.strptime(entry["date"], DATETIME_FORMAT_SLEEP)
            measurement_time = make_aware(entry_date)
            start_date_entry = make_aware(
                datetime.fromtimestamp(entry.get("startdate"))
            )
            end_date_entry = make_aware(datetime.fromtimestamp(entry.get("enddate")))
            potential_entry = SleepSummary.objects.filter(
                start_date=start_date_entry, end_date=end_date_entry
            )
            if len(potential_entry) == 0:
                try:
                    entry_data = entry.get("data")
                    new_sleep_summary = SleepSummary(
                        start_date=start_date_entry,
                        end_date=end_date_entry,
                        user_id=user_id,
                        device_type=DEVICE_TYPES[entry.get("model")],
                        device_id=entry.get("model_id", 0),
                        breathing_disturbances_intensity=entry_data.get(
                            "breathing_disturbances_intensity", 0
                        ),
                        deep_sleep_duration=entry_data.get("deepsleepduration"),
                        duration_to_sleep=entry_data.get("durationtosleep", 0),
                        duration_to_wakeup=entry_data.get("durationtowakeup", 0),
                        hr_average=entry_data.get("hr_average"),
                        hr_max=entry_data.get("hr_max"),
                        hr_min=entry_data.get("hr_min"),
                        light_sleep_duration=entry_data.get("lightsleepduration"),
                        rem_sleep_duration=entry_data.get("remsleepduration"),
                        rr_average=entry_data.get("rr_average"),
                        rr_max=entry_data.get("rr_max"),
                        rr_min=entry_data.get("rr_min"),
                        sleep_score=entry_data.get("sleep_score"),
                        snoring=entry_data.get("snoring", 0),
                        snoring_episode_count=entry_data.get("snoringepisodecount", 0),
                        wakeup_count=entry_data.get("wakeupcount", 0),
                        wakeup_duration=entry_data.get("wakeupduration", 0),
                    )
                    new_sleep_summary.save()
                    counter += 1
                except IntegrityError as e:
                    LOGGER.error("An error occurred when writing to the DB: %s.", e)
                except KeyError as e:
                    LOGGER.error(
                        "An error occurred when writing to the DB: %s. Data contents: %s. Datetime: %s",
                        e,
                        entry,
                        measurement_time,
                    )
                    raise e
    return counter


def request_all_sleep_data(
    access_token: str,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    from_notification: bool = False,
) -> (int, int):
    sleep_raw_counter = get_sleep_data_raw(
        access_token=access_token,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        from_notification=from_notification,
    )
    sleep_summary_counter = get_sleep_data_summary(
        access_token=access_token,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        from_notification=from_notification,
    )
    return sleep_raw_counter, sleep_summary_counter
