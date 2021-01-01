import os
from datetime import datetime
import logging

from django.utils.timezone import make_aware

import numpy as np

from connector.utils.common import prepare_date_pairs, send_data_request
from connector.models import Weight


class MeasurementTypeError(Exception):
    pass


class InconsistentEntries(Exception):
    pass


LOGGER = logging.getLogger(__name__)
WITHINGS_API_URL = os.environ.get("WITHINGS_API_URL", "https://wbsapi.withings.net/v2")
DATETIME_FORMAT_MEASUREMENT = "%Y-%m-%d"

MEASUREMENT_TYPES = {"weight": [1, 5, 6, 8, 11, 54, 76, 77, 88, 91]}
MEASUREMENT_TYPE_MAPPING = {
    1: "WEIGHT",
    4: "HEIGHT",
    5: "FAT_FREE_MASS",
    6: "FAT_RATIO",
    8: "FAT_MASS_WEIGHT",
    9: "DIASTOLIC_BLOOD_PRESSURE",
    10: "SYSTOLIC_BLOOD_PRESSURE",
    11: "HEART_RATE",
    12: "TEMPERATURE",
    54: "SP02",
    71: "BODY_TEMPERATURE",
    73: "SKIN_TEMPERATURE",
    76: "MUSCLE_MASS",
    77: "HYDRATION",
    88: "BONE_MASS",
    91: "PULSE_WAVE_VELOCITY",
    123: "VO2",
}
SOURCE_MAPPING = {
    -1: "UNKNOWN",
    0: "DEVICE_ENTRY_FOR_USER",
    1: "DEVICE_ENTRY_FOR_USER_AMBIGUOUS",
    2: "MANUAL_USER_ENTRY",
    4: "MANUAL_USER_DURING_ACCOUNT_CREATION",
    5: "MEASURE_AUTO",
    7: "MEASURE_USER_CONFIRMED",
    8: "SAME_AS_DEVICE_ENTRY_FOR_USER",
}


def get_measurements(
    access_token: str,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    meas_type: str,
    offset: int = None,
    from_notification: bool = False,
) -> int:

    date_pairs = prepare_date_pairs(Weight, start_date, end_date, from_notification)

    if meas_type not in MEASUREMENT_TYPES.keys():
        raise MeasurementTypeError(f"Measurement type '{meas_type}' is not supported.")
    required_measurements = [str(x) for x in MEASUREMENT_TYPES[meas_type]]

    counter = 0
    for sub_start_date, sub_end_date in date_pairs:
        req_params = {
            "action": "getmeas",
            "startdate": int(sub_start_date.timestamp()),
            "enddate": int(sub_end_date.timestamp()),
            "meastypes": ",".join(required_measurements),
            "category": 1,
            "offset": offset,
        }
        data = send_data_request(
            os.path.join(WITHINGS_API_URL, "measure"), req_params, access_token
        )

        if meas_type == "weight":
            weight_counter = process_weight_measurements(data["measuregrps"], user_id)
            counter += weight_counter
        else:
            raise MeasurementTypeError(
                f"Measurement type '{meas_type}' is not supported."
            )

    return counter


def process_weight_measurements(measuregrps: list, user_id: int) -> int:
    counter = 0
    data_for_db = {}
    # measurements of a single type for all the days
    for measurement in measuregrps:
        source = SOURCE_MAPPING[measurement.get("attrib")]
        measured_at = make_aware(datetime.fromtimestamp(int(measurement.get("date"))))
        measured_at_ts = int(datetime.timestamp(measured_at) * 1000)
        device_id = measurement.get("deviceid")

        if measured_at_ts not in data_for_db:
            data_for_db[measured_at_ts] = {
                "device_id": None,
                "measured_at": None,
                "source": None,
            }

        for single_day_measurement in measurement["measures"]:
            measure_type = MEASUREMENT_TYPE_MAPPING[
                single_day_measurement.get("type", "UNKNOWN")
            ]
            measure_unit = single_day_measurement.get("unit")
            measure_value = single_day_measurement.get("value")
            measure_value_converted = np.round(measure_value * (10 ** measure_unit), 4)

            # TODO: change it later when fitness level is introduced properly
            if measure_type in ["VO2", "UNKNOWN"]:
                LOGGER.warning(
                    "An unexpected measurement was found: %s. Value: %s, unit: %s",
                    measure_type,
                    measure_value,
                    measure_unit,
                )

            if not data_for_db[measured_at_ts]["source"]:
                data_for_db[measured_at_ts]["source"] = source
            # elif data_for_db["source"] != source:
            #     raise InconsistentEntries(
            #         f"Measurement sources differ: {data_for_db[measured_at_ts]['source']} != {source}"
            #     )

            if not data_for_db[measured_at_ts]["device_id"]:
                data_for_db[measured_at_ts]["device_id"] = device_id
            elif data_for_db[measured_at_ts]["device_id"] != device_id:
                raise InconsistentEntries(
                    f"Device id differ: {data_for_db[measured_at_ts]['device_id']} != {device_id}"
                )

            if not data_for_db[measured_at_ts]["measured_at"]:
                data_for_db[measured_at_ts]["measured_at"] = measured_at
            elif data_for_db[measured_at_ts]["measured_at"] != measured_at:
                raise InconsistentEntries(
                    f"Measurement dates differ: {data_for_db[measured_at_ts]['measured_at']} != {measured_at}"
                )

            data_for_db[measured_at_ts][measure_type.lower()] = measure_value_converted

    for meas_ts in data_for_db.keys():
        potential_entry = Weight.objects.filter(
            measured_at=data_for_db[meas_ts]["measured_at"]
        )
        if len(potential_entry) == 0:
            try:
                new_weight_measurement = Weight(
                    device_id=data_for_db[meas_ts].get("device_id", "unknown"),
                    user_id=user_id,
                    source=data_for_db[meas_ts].get("source"),
                    measured_at=data_for_db[meas_ts].get("measured_at"),
                    weight=data_for_db[meas_ts].get("weight"),
                    fat_free_mass=data_for_db[meas_ts].get("fat_free_mass"),
                    fat_ratio=data_for_db[meas_ts].get("fat_ratio"),
                    fat_mass_weight=data_for_db[meas_ts].get("fat_mass_weight"),
                    muscle_mass=data_for_db[meas_ts].get("muscle_mass"),
                    hydration=data_for_db[meas_ts].get("hydration"),
                    bone_mass=data_for_db[meas_ts].get("bone_mass"),
                    pulse_wave_velocity=data_for_db[meas_ts].get("pulse_wave_velocity"),
                    heart_rate=data_for_db[meas_ts].get("heart_rate"),
                )
                new_weight_measurement.save()
                counter += 1
            except KeyError as e:
                LOGGER.error(
                    f"Error while saving to DB. Current measurement: {data_for_db}\n{e}"
                )
    return counter


def request_all_measurements_data(
    access_token: str,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    meas_type: str,
    offset: int = None,
    from_notification: bool = False,
) -> int:

    measurements_counter = get_measurements(
        access_token=access_token,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        meas_type=meas_type,
        offset=offset,
        from_notification=from_notification,
    )

    return measurements_counter
