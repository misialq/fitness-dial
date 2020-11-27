import datetime
import json
import logging
import pytz

import requests
from django.db import IntegrityError
from django.utils.timezone import make_aware
from withings_api import WithingsApi, MeasureGetActivityResponse, GetActivityField

from ..models import ActivityRaw, ActivitySummary
from .common import APIError

ACTIVITY_INTRADAY_DATA_FIELDS = [
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
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    offset: int = None,
    from_notification: bool = False,
) -> int:

    if from_notification:
        # find the last available entry in the DB
        start_date = (
            ActivitySummary.objects.filter(measured_at__isnull=False)
            .latest("measured_at")
            .measured_at
        )
        end_date = make_aware(datetime.datetime.now())
        LOGGER.debug(
            "Activity request from notification - start and end dates will be reset to %s and %s.",
            start_date.strftime(DATETIME_FORMAT_ACTIVITY),
            end_date.strftime(DATETIME_FORMAT_ACTIVITY),
        )

    all_dates = [
        start_date + datetime.timedelta(n)
        for n in range(int((end_date - start_date).days + 1))
    ]
    date_pairs = list(zip(all_dates, all_dates[1:]))

    counter = 0
    for sub_start_date, sub_end_date in date_pairs:
        req_params = {
            "action": "getactivity",
            "startdateymd": sub_start_date.strftime(DATETIME_FORMAT_ACTIVITY),
            "enddateymd": sub_end_date.strftime(DATETIME_FORMAT_ACTIVITY),
            "data_fields": ",".join(ACTIVITY_DATA_FIELDS),
            "offset": offset,
        }
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.post(
            "https://wbsapi.withings.net/v2/measure", data=req_params, headers=headers,
        )
        meas = json.loads(response.text)

        if meas["status"] != 0:
            raise APIError(
                f"An error ocurred while fetching activities. The reason wsa: {meas['error']}"
            )
        else:
            # check whether entries already exist (by start- and end-date)
            activity = meas["body"]

            for entry in activity["activities"]:
                LOGGER.debug(entry)
                if "heart_rate" in entry.keys() or "steps" in entry.keys():
                    measurement_type = (
                        "heart_rate" if "heart_rate" in entry.keys() else "steps"
                    )
                else:
                    LOGGER.debug(
                        "No steps or heart rate found in the data - skipping..."
                    )
                    continue
                measurement_time = make_aware(
                    datetime.datetime.strptime(entry["date"], DATETIME_FORMAT_ACTIVITY)
                )
                potential_entry = ActivitySummary.objects.filter(
                    measured_at=measurement_time, measurement_type=measurement_type
                )
                if len(potential_entry) == 0:
                    try:
                        # save raw activity to DB
                        new_activity_summary = ActivitySummary(
                            device_type=entry["brand"],
                            device_id=0 if not entry["deviceid"] else entry["deviceid"],
                            user_id=user_id,
                            measured_at=measurement_time,
                            measurement_type=measurement_type,
                            is_tracker=entry["is_tracker"],
                            steps=entry["steps"]
                            if measurement_type == "steps"
                            else None,
                            distance=entry["distance"]
                            if measurement_type == "steps"
                            and "distance" in entry.keys()
                            else None,
                            elevation=entry["elevation"]
                            if measurement_type == "steps"
                            and "elevation" in entry.keys()
                            else None,
                            calories=entry["calories"]
                            if measurement_type == "steps"
                            and "calories" in entry.keys()
                            else None,
                            soft_activities_duration=entry["soft"]
                            if "soft" in entry.keys()
                            else None,
                            moderate_activities_duration=entry["moderate"]
                            if "moderate" in entry.keys()
                            else None,
                            intense_activities_duration=entry["intense"]
                            if "intense" in entry.keys()
                            else None,
                            active_duration=entry["active"]
                            if "active" in entry.keys()
                            else None,
                            total_calories=entry["totalcalories"]
                            if "totalcalories" in entry.keys()
                            else None,
                            hr_average=entry["hr_average"]
                            if "hr_average" in entry.keys()
                            else None,
                            hr_min=entry["hr_min"]
                            if "hr_min" in entry.keys()
                            else None,
                            hr_max=entry["hr_max"]
                            if "hr_max" in entry.keys()
                            else None,
                            hr_zone_light_duration=entry["hr_zone_0"]
                            if "hr_zone_0" in entry.keys()
                            else None,
                            hr_zone_moderate_duration=entry["hr_zone_1"]
                            if "hr_zone_1" in entry.keys()
                            else None,
                            hr_zone_intense_duration=entry["hr_zone_2"]
                            if "hr_zone_2" in entry.keys()
                            else None,
                            hr_zone_max_duration=entry["hr_zone_3"]
                            if "hr_zone_3" in entry.keys()
                            else None,
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
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    from_notification: bool = False,
) -> int:

    if from_notification:
        # find the last available entry in the DB
        start_date = (
            ActivityRaw.objects.filter(measured_at__isnull=False)
            .latest("measured_at")
            .measured_at
        )
        end_date = make_aware(datetime.datetime.now())
        LOGGER.debug(
            "Activity request from notification - start and end dates will be reset to %s and %s.",
            start_date.strftime(DATETIME_FORMAT_ACTIVITY),
            end_date.strftime(DATETIME_FORMAT_ACTIVITY),
        )

    all_dates = [
        start_date + datetime.timedelta(n)
        for n in range(int((end_date - start_date).days + 1))
    ]
    date_pairs = list(zip(all_dates, all_dates[1:]))

    counter = 0
    skipped_counter = 0
    for sub_start_date, sub_end_date in date_pairs:
        req_params = {
            "action": "getintradayactivity",
            "startdate": int(sub_start_date.timestamp()),
            "enddate": int(sub_end_date.timestamp()),
            "data_fields": ",".join(ACTIVITY_INTRADAY_DATA_FIELDS),
        }
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.post(
            "https://wbsapi.withings.net/v2/measure", data=req_params, headers=headers,
        )
        meas_detailed = json.loads(response.text)

        if meas_detailed["status"] != 0:
            raise APIError(
                f"An error ocurred while fetching intra-day activities. The reason wsa: {meas_detailed['error']}"
            )
        else:
            # check whether entries already exist (by start- and end-date)
            activity_raw = meas_detailed["body"]

            for ts, entry in activity_raw["series"].items():
                LOGGER.debug(entry)
                if "heart_rate" in entry.keys() or "steps" in entry.keys():
                    measurement_type = (
                        "heart_rate" if "heart_rate" in entry.keys() else "steps"
                    )
                else:
                    LOGGER.debug(
                        "No steps or heart rate found in the data - skipping..."
                    )
                    skipped_counter += 1
                    continue
                measurement_time = make_aware(datetime.datetime.fromtimestamp(int(ts)))
                LOGGER.debug(f"Measurement time: %s", measurement_time)
                potential_entry = ActivityRaw.objects.filter(
                    measured_at=measurement_time, measurement_type=measurement_type
                )
                if len(potential_entry) == 0:
                    try:
                        # save raw activity to DB
                        new_activity_raw = ActivityRaw(
                            device_type=entry["model"],
                            device_id=entry["model_id"],
                            user_id=user_id,
                            measured_at=measurement_time,
                            measurement_type=measurement_type,
                            steps=entry["steps"]
                            if measurement_type == "steps"
                            else None,
                            duration=entry["duration"],
                            distance=entry["distance"]
                            if measurement_type == "steps"
                            and "distance" in entry.keys()
                            else None,
                            elevation=entry["elevation"]
                            if measurement_type == "steps"
                            and "elevation" in entry.keys()
                            else None,
                            calories=entry["calories"]
                            if measurement_type == "steps"
                            and "calories" in entry.keys()
                            else None,
                            heart_rate=entry["heart_rate"]
                            if measurement_type == "heart_rate"
                            else None,
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
                f"Total of {skipped_counter} of of {counter + skipped_counter} entries without heart rate or steps data were found "
            )
    return counter


def request_all_activities_data(
    access_token: str,
    user_id: int,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
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
