import os
from datetime import datetime
import logging

from django.db import IntegrityError
from django.utils.timezone import make_aware

from ..models import ActivityRaw, ActivitySummary
from .common import send_data_request, prepare_date_pairs


WITHINGS_API_URL = os.environ.get("WITHINGS_API_URL", "https://wbsapi.withings.net/v2")
ACTIVITY_DATA_FIELDS_INTRADAY = [
    "steps",
    "elevation",
    "calories",
    "distance",
    "stroke",
    "pool_lap",
    "duration",
    "heart_rate",
    "spo2_auto",
]
ACTIVITY_DATA_FIELDS = [
    "steps",
    "elevation",
    "calories",
    "distance",
    "soft",
    "moderate",
    "intense",
    "active",
    "totalcalories",
    "hr_average",
    "hr_min",
    "hr_max",
    "hr_zone_0",
    "hr_zone_1",
    "hr_zone_2",
    "hr_zone_3",
]
DATETIME_FORMAT_ACTIVITY = "%Y-%m-%d"
LOGGER = logging.getLogger(__name__)


def get_activity_summary(
    access_token: str,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    offset: int = None,
    from_notification: bool = False,
) -> int:

    date_pairs = prepare_date_pairs(
        ActivitySummary, start_date, end_date, from_notification
    )

    counter = 0
    for sub_start_date, sub_end_date in date_pairs:
        req_params = {
            "action": "getactivity",
            "startdateymd": sub_start_date.strftime(DATETIME_FORMAT_ACTIVITY),
            "enddateymd": sub_end_date.strftime(DATETIME_FORMAT_ACTIVITY),
            "data_fields": ",".join(ACTIVITY_DATA_FIELDS),
            "offset": offset,
        }

        data = send_data_request(
            os.path.join(WITHINGS_API_URL, "measure"), req_params, access_token
        )

        for entry in data["activities"]:
            LOGGER.debug(entry)
            if "heart_rate" in entry.keys() or "steps" in entry.keys():
                measurement_type = (
                    "heart_rate" if "heart_rate" in entry.keys() else "steps"
                )
            else:
                LOGGER.debug("No steps or heart rate found in the data - skipping...")
                continue
            entry_date = datetime.strptime(entry.get("date"), DATETIME_FORMAT_ACTIVITY)
            measurement_time = make_aware(entry_date)
            potential_entry = ActivitySummary.objects.filter(
                measured_at=measurement_time, measurement_type=measurement_type
            )
            if len(potential_entry) == 0:
                try:
                    # save raw activity to DB
                    if measurement_type == "steps":
                        distance = entry.get("distance")
                        elevation = entry.get("elevation")
                        calories = entry.get("calories")
                        steps = entry.get("steps")
                    else:
                        distance, elevation, calories, steps = None, None, None, None

                    new_activity_summary = ActivitySummary(
                        device_type=entry.get("brand"),
                        device_id=0
                        if not entry.get("deviceid", 0)
                        else entry.get("deviceid", 0),
                        user_id=user_id,
                        measured_at=measurement_time,
                        measurement_type=measurement_type,
                        is_tracker=entry.get("is_tracker"),
                        steps=steps,
                        distance=distance,
                        elevation=elevation,
                        calories=calories,
                        soft_activities_duration=entry.get("soft"),
                        moderate_activities_duration=entry.get("moderate"),
                        intense_activities_duration=entry.get("intense"),
                        active_duration=entry.get("active"),
                        total_calories=entry.get("totalcalories"),
                        hr_average=entry.get("hr_average"),
                        hr_min=entry.get("hr_min"),
                        hr_max=entry.get("hr_max"),
                        hr_zone_light_duration=entry.get("hr_zone_0"),
                        hr_zone_moderate_duration=entry.get("hr_zone_1"),
                        hr_zone_intense_duration=entry.get("hr_zone_2"),
                        hr_zone_max_duration=entry.get("hr_zone_3"),
                    )
                    new_activity_summary.save()
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


def get_activity_detailed(
    access_token: str,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    from_notification: bool = False,
) -> int:

    date_pairs = prepare_date_pairs(
        ActivityRaw, start_date, end_date, from_notification
    )

    counter = 0
    skipped_counter = 0
    for sub_start_date, sub_end_date in date_pairs:
        req_params = {
            "action": "getintradayactivity",
            "startdate": int(sub_start_date.timestamp()),
            "enddate": int(sub_end_date.timestamp()),
            "data_fields": ",".join(ACTIVITY_DATA_FIELDS_INTRADAY),
        }

        data = send_data_request(
            os.path.join(WITHINGS_API_URL, "measure"), req_params, access_token
        )

        # TODO: double check that - is this ts going to work?
        for ts, entry in data["series"].items():
            LOGGER.debug(entry)
            if "heart_rate" in entry.keys() or "steps" in entry.keys():
                measurement_type = (
                    "heart_rate" if "heart_rate" in entry.keys() else "steps"
                )
            else:
                LOGGER.debug("No steps or heart rate found in the data - skipping...")
                skipped_counter += 1
                continue
            measurement_time = make_aware(datetime.fromtimestamp(int(ts)))
            LOGGER.debug(f"Measurement time: %s", measurement_time)
            potential_entry = ActivityRaw.objects.filter(
                measured_at=measurement_time, measurement_type=measurement_type
            )
            if len(potential_entry) == 0:
                try:
                    if measurement_type == "steps":
                        distance = entry.get("distance")
                        elevation = entry.get("elevation")
                        calories = entry.get("calories")
                        steps = entry.get("steps")
                    else:
                        distance, elevation = None, None
                        calories, steps = None, None

                    new_activity_raw = ActivityRaw(
                        device_type=entry.get("model"),
                        device_id=entry.get("model_id"),
                        user_id=user_id,
                        measured_at=measurement_time,
                        measurement_type=measurement_type,
                        steps=steps,
                        duration=entry.get("duration"),
                        distance=distance,
                        elevation=elevation,
                        calories=calories,
                        heart_rate=entry.get("heart_rate"),
                    )
                    new_activity_raw.save()
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
        if skipped_counter > 0:
            LOGGER.debug(
                f"Total of {skipped_counter} of of {counter + skipped_counter} entries without "
                f"heart rate or steps data were found "
            )
    return counter


def request_all_activities_data(
    access_token: str,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    from_notification: bool = False,
) -> (int, int):
    activities_raw_counter = get_activity_detailed(
        access_token=access_token,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        from_notification=from_notification,
    )
    activities_summary_counter = get_activity_summary(
        access_token=access_token,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        from_notification=from_notification,
    )
    return activities_raw_counter, activities_summary_counter
