import datetime
import logging

import numpy as np
from withings_api import (
    WithingsApi,
    MeasureType,
    MeasureGetMeasGroupCategory,
    MeasureGetMeasResponse,
)

from ..models import Weight


class MeasurementTypeError(Exception):
    pass


class InconsistentEntries(Exception):
    pass


LOGGER = logging.getLogger(__name__)
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
MEASUREMENTS = {
    1: MeasureType.WEIGHT,
    5: MeasureType.FAT_FREE_MASS,
    6: MeasureType.FAT_RATIO,
    8: MeasureType.FAT_MASS_WEIGHT,
    11: MeasureType.HEART_RATE,
    54: MeasureType.SP02,
    76: MeasureType.MUSCLE_MASS,
    77: MeasureType.HYDRATION,
    88: MeasureType.BONE_MASS,
    91: MeasureType.PULSE_WAVE_VELOCITY,
}

MEASUREMENT_TYPES = {"weight": [1, 5, 6, 8, 11, 54, 76, 77, 88, 91]}


def get_measurements(
    api: WithingsApi,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    meas_type: MeasureType,
    offset: int = None,
) -> MeasureGetMeasResponse:
    meas = api.measure_get_meas(
        startdate=start_date,
        enddate=end_date,
        meastype=meas_type,
        offset=offset,
        category=MeasureGetMeasGroupCategory.REAL,
    )

    return meas


def process_weight_measurements(measurements: list, user_id: int) -> int:
    counter = 0
    data_for_db = {}
    for meas in measurements:
        for (
            single_measurement
        ) in meas.measuregrps:  # measurements of a single type for all the days
            source = single_measurement.attrib.name
            measured_at = single_measurement.date.datetime
            measured_at_ts = int(datetime.datetime.timestamp(measured_at) * 1000)
            device_id = single_measurement.deviceid

            if measured_at_ts not in data_for_db:
                data_for_db[measured_at_ts] = {
                    "device_id": None,
                    "measured_at": None,
                    "source": None,
                }

            for single_day_measurement in single_measurement.measures:
                measure_type = single_day_measurement.type.name
                measure_unit = single_day_measurement.unit
                measure_value = single_day_measurement.value
                measure_value_converted = np.round(
                    measure_value * (10 ** measure_unit), 4
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

                data_for_db[measured_at_ts][
                    measure_type.lower()
                ] = measure_value_converted

    for meas_ts in data_for_db.keys():
        potential_entry = Weight.objects.filter(
            measured_at=data_for_db[meas_ts]["measured_at"]
        )
        if len(potential_entry) == 0:
            try:
                new_weight_measurement = Weight(
                    device_id=data_for_db[meas_ts]["device_id"]
                    if data_for_db[meas_ts]["device_id"]
                    else "unknown",
                    user_id=user_id,
                    source=data_for_db[meas_ts]["source"],
                    measured_at=data_for_db[meas_ts]["measured_at"],
                    weight=data_for_db[meas_ts]["weight"]
                    if "weight" in data_for_db[meas_ts]
                    else None,
                    fat_free_mass=data_for_db[meas_ts]["fat_free_mass"]
                    if "fat_free_mass" in data_for_db[meas_ts]
                    else None,
                    fat_ratio=data_for_db[meas_ts]["fat_ratio"]
                    if "fat_ratio" in data_for_db[meas_ts]
                    else None,
                    fat_mass_weight=data_for_db[meas_ts]["fat_mass_weight"]
                    if "fat_mass_weight" in data_for_db[meas_ts]
                    else None,
                    muscle_mass=data_for_db[meas_ts]["muscle_mass"]
                    if "muscle_mass" in data_for_db[meas_ts]
                    else None,
                    hydration=data_for_db[meas_ts]["hydration"]
                    if "hydration" in data_for_db[meas_ts]
                    else None,
                    bone_mass=data_for_db[meas_ts]["bone_mass"]
                    if "bone_mass" in data_for_db[meas_ts]
                    else None,
                    pulse_wave_velocity=data_for_db[meas_ts]["pulse_wave_velocity"]
                    if "pulse_wave_velocity" in data_for_db[meas_ts]
                    else None,
                    heart_rate=data_for_db[meas_ts]["heart_rate"]
                    if "heart_rate" in data_for_db[meas_ts]
                    else None,
                )
                new_weight_measurement.save()
                counter += 1
            except KeyError as e:
                LOGGER.error(
                    f"Error while saving to DB. Current measurement: {data_for_db}\n{e}"
                )
    return counter


def request_all_measurements_data(
    api: WithingsApi,
    meas_type: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    offset: int = None,
) -> int:
    if meas_type not in MEASUREMENT_TYPES.keys():
        raise MeasurementTypeError(f"Measurement type '{meas_type}' is not supported.")
    required_measurements = MEASUREMENT_TYPES[meas_type]
    all_measurements = []
    for meas in required_measurements:
        measurement_data = get_measurements(
            api, start_date, end_date, MEASUREMENTS[meas], offset
        )
        all_measurements.append(measurement_data)
    if meas_type == "weight":
        measurements_count = process_weight_measurements(
            all_measurements, api._credentials.userid
        )
        return measurements_count
    else:
        raise MeasurementTypeError(f"Measurement type '{meas_type}' is not supported.")
