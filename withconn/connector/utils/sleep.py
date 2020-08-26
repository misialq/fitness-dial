import datetime

from withings_api import (
    new_credentials,
    WithingsApi,
    GetSleepSummaryField,
    GetSleepField,
)

from ..models import SleepSummary, SleepRaw

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DATA_FIELDS_RAW = [GetSleepField.HR, GetSleepField.RR, GetSleepField.SNORING]
DATA_FIELDS_SUMMARY = [
    GetSleepSummaryField.BREATHING_DISTURBANCES_INTENSITY,
    GetSleepSummaryField.DEEP_SLEEP_DURATION,
    GetSleepSummaryField.DURATION_TO_SLEEP,
    GetSleepSummaryField.DURATION_TO_WAKEUP,
    GetSleepSummaryField.HR_AVERAGE,
    GetSleepSummaryField.HR_MAX,
    GetSleepSummaryField.HR_MIN,
    GetSleepSummaryField.LIGHT_SLEEP_DURATION,
    GetSleepSummaryField.REM_SLEEP_DURATION,
    GetSleepSummaryField.RR_AVERAGE,
    GetSleepSummaryField.RR_MAX,
    GetSleepSummaryField.RR_MIN,
    GetSleepSummaryField.SLEEP_SCORE,
    GetSleepSummaryField.SNORING,
    GetSleepSummaryField.SNORING_EPISODE_COUNT,
    GetSleepSummaryField.WAKEUP_COUNT,
]


def get_authenticated_api(
    access_token_data: dict, client_id: str, client_secret: str
) -> WithingsApi:
    credentials = new_credentials(client_id, client_secret, access_token_data)
    return WithingsApi(credentials)


def get_sleep_data_raw(
    api: WithingsApi, start_date: datetime.datetime, end_date: datetime.datetime,
) -> int:
    sleep_raw = api.sleep_get(
        startdate=start_date, enddate=end_date, data_fields=DATA_FIELDS_RAW,
    )

    # check whether entries already exist (by start- and end-date)
    counter = 0
    for i, entry in enumerate(sleep_raw.series):
        potential_entry = SleepRaw.objects.filter(
            start_date=entry.startdate.datetime, end_date=entry.enddate.datetime
        )
        if len(potential_entry) == 0:
            # save raw sleep to DB
            new_sleep_raw = SleepRaw(
                device_type=sleep_raw.model.name,
                device_id=sleep_raw.model.value,
                user_id=api._credentials.userid,
                start_date=entry.startdate.datetime,
                end_date=entry.enddate.datetime,
                sleep_phase=entry.state.name,
                sleep_phase_id=entry.state.value,
                hr_series=[
                    {
                        "timestamp": x.timestamp.datetime.strftime(DATETIME_FORMAT),
                        "value": x.value,
                    }
                    for x in entry.hr
                ],
                rr_series=[
                    {
                        "timestamp": x.timestamp.datetime.strftime(DATETIME_FORMAT),
                        "value": x.value,
                    }
                    for x in entry.rr
                ],
                snoring_series=[
                    {
                        "timestamp": x.timestamp.datetime.strftime(DATETIME_FORMAT),
                        "value": x.value,
                    }
                    for x in entry.snoring
                ],
            )
            new_sleep_raw.save()
            counter += 1

    return counter


def get_sleep_data_summary(
    api: WithingsApi, start_date: datetime.datetime, end_date: datetime.datetime,
) -> int:
    sleep_summary = api.sleep_get_summary(
        startdateymd=start_date, enddateymd=end_date, data_fields=DATA_FIELDS_SUMMARY,
    )

    # check whether entries already exist (by start- and end-date)
    counter = 0
    for i, entry in enumerate(sleep_summary.series):
        potential_entry = SleepSummary.objects.filter(
            start_date=entry.startdate.datetime, end_date=entry.enddate.datetime
        )
        if len(potential_entry) == 0:
            # save sleep summary to DB
            new_sleep_summary = SleepSummary(
                start_date=entry.startdate.datetime,
                end_date=entry.enddate.datetime,
                user_id=api._credentials.userid,
                device_type=entry.model.name,
                device_id=entry.model.value,
                breathing_disturbances_intensity=0
                if entry.data.breathing_disturbances_intensity is None
                else entry.data.breathing_disturbances_intensity,
                deep_sleep_duration=entry.data.deepsleepduration,
                duration_to_sleep=0
                if entry.data.durationtosleep is None
                else entry.data.durationtosleep,
                duration_to_wakeup=0
                if entry.data.durationtowakeup is None
                else entry.data.durationtowakeup,
                hr_average=entry.data.hr_average,
                hr_max=entry.data.hr_max,
                hr_min=entry.data.hr_min,
                light_sleep_duration=entry.data.lightsleepduration,
                rem_sleep_duration=entry.data.remsleepduration,
                rr_average=entry.data.rr_average,
                rr_max=entry.data.rr_max,
                rr_min=entry.data.rr_min,
                sleep_score=entry.data.sleep_score,
                snoring=0 if entry.data.snoring is None else entry.data.snoring,
                snoring_episode_count=0
                if entry.data.snoringepisodecount is None
                else entry.data.snoringepisodecount,
                wakeup_count=0
                if entry.data.wakeupcount is None
                else entry.data.wakeupcount,
                wakeup_duration=0
                if entry.data.wakeupduration is None
                else entry.data.wakeupduration,
            )
            new_sleep_summary.save()
            counter += 1

    return counter


def request_all_sleep_data(
    api: WithingsApi, start_date: datetime.datetime, end_date: datetime.datetime,
) -> tuple:
    sleep_raw_counter = get_sleep_data_raw(api, start_date, end_date)
    sleep_summary_counter = get_sleep_data_summary(api, start_date, end_date)
    return sleep_raw_counter, sleep_summary_counter
