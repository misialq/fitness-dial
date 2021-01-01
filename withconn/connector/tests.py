from datetime import datetime

import pytz
from django.test import TestCase

from connector.models import ActivitySummary
from connector.utils.common import prepare_date_pairs
from testfixtures import Replace, test_datetime


class UtilsTestCase(TestCase):
    def setUp(self):
        self.fake_token = "token124"
        self.user_id = 123
        self.start_date = datetime.strptime("20201208-211000", "%Y%m%d-%H%M%S")
        self.end_date = datetime.strptime("20201208-221000", "%Y%m%d-%H%M%S")

        ActivitySummary.objects.create(
            user_id=123,
            device_type="test_device",
            device_id=1,
            measured_at=datetime.strptime(
                "20201208-210500", "%Y%m%d-%H%M%S"
            ).astimezone(pytz.utc),
            is_tracker=True,
            steps=6150,
            distance=5663.541,
            elevation=0,
            calories=659.677,
            soft_activities_duration=7620,
            moderate_activities_duration=3840,
            intense_activities_duration=1620,
            active_duration=5460,
            total_calories=2352.961,
            hr_average=85,
            hr_max=123,
            hr_min=46,
            hr_zone_light_duration=18259,
            hr_zone_moderate_duration=4682,
            hr_zone_intense_duration=0,
            hr_zone_max_duration=0,
            measurement_type="steps",
        )

    def test_date_pairs_notif_same_day(self):
        with Replace(
            "connector.utils.common.datetime", test_datetime(2020, 12, 8, 21, 5, 30)
        ):
            start_date = datetime.strptime("2020-12-30T09:48:00", "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime("2020-12-31T08:59:37", "%Y-%m-%dT%H:%M:%S")
            date_pairs_obs = prepare_date_pairs(
                ActivitySummary, start_date, end_date, True
            )
            date_pairs_exp = [
                (
                    datetime(2020, 12, 8, 21, 5, tzinfo=pytz.UTC),
                    datetime(2020, 12, 9, 21, 5, tzinfo=pytz.UTC),
                )
            ]
            self.assertEqual(len(date_pairs_obs), len(date_pairs_exp))
            for i, j in zip(date_pairs_obs, date_pairs_exp):
                self.assertEqual(i, j)

    def test_date_pairs_notif_next_day(self):
        with Replace(
            "connector.utils.common.datetime", test_datetime(2020, 12, 9, 21, 5, 30)
        ):
            start_date = datetime.strptime("2020-12-30T09:48:00", "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime("2020-12-31T08:59:37", "%Y-%m-%dT%H:%M:%S")
            date_pairs_obs = prepare_date_pairs(
                ActivitySummary, start_date, end_date, True
            )
            date_pairs_exp = [
                (
                    datetime(2020, 12, 8, 21, 5, tzinfo=pytz.UTC),
                    datetime(2020, 12, 9, 21, 5, tzinfo=pytz.UTC),
                )
            ]
            self.assertEqual(len(date_pairs_obs), len(date_pairs_exp))
            for i, j in zip(date_pairs_obs, date_pairs_exp):
                self.assertEqual(i, j)

    def test_date_pairs_notif_more_days(self):
        with Replace(
            "connector.utils.common.datetime", test_datetime(2020, 12, 11, 21, 5, 30)
        ):
            start_date = datetime.strptime("2020-12-30T09:48:00", "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime("2020-12-31T08:59:37", "%Y-%m-%dT%H:%M:%S")
            date_pairs_obs = prepare_date_pairs(
                ActivitySummary, start_date, end_date, True
            )
            date_pairs_exp = [
                (
                    datetime(2020, 12, 8, 21, 5, tzinfo=pytz.UTC),
                    datetime(2020, 12, 9, 21, 5, tzinfo=pytz.UTC),
                ),
                (
                    datetime(2020, 12, 9, 21, 5, tzinfo=pytz.UTC),
                    datetime(2020, 12, 10, 21, 5, tzinfo=pytz.UTC),
                ),
                (
                    datetime(2020, 12, 10, 21, 5, tzinfo=pytz.UTC),
                    datetime(2020, 12, 11, 21, 5, tzinfo=pytz.UTC),
                ),
            ]
            self.assertEqual(len(date_pairs_obs), len(date_pairs_exp))
            for i, j in zip(date_pairs_obs, date_pairs_exp):
                self.assertEqual(i, j)

    def test_date_pairs_nonotif_same_day(self):
        start_date = datetime(2020, 12, 30, 9, 48, 0, tzinfo=pytz.UTC)
        end_date = datetime(2020, 12, 30, 9, 48, 37, tzinfo=pytz.UTC)
        date_pairs_obs = prepare_date_pairs(
            ActivitySummary, start_date, end_date, False
        )
        date_pairs_exp = [
            (
                datetime(2020, 12, 30, 9, 48, tzinfo=pytz.UTC),
                datetime(2020, 12, 31, 9, 48, tzinfo=pytz.UTC),
            )
        ]
        self.assertEqual(len(date_pairs_obs), len(date_pairs_exp))
        for i, j in zip(date_pairs_obs, date_pairs_exp):
            self.assertEqual(i, j)

    def test_date_pairs_nonotif_next_day(self):
        start_date = datetime(2020, 12, 30, 9, 48, 0, tzinfo=pytz.UTC)
        end_date = datetime(2020, 12, 31, 9, 48, 37, tzinfo=pytz.UTC)
        date_pairs_obs = prepare_date_pairs(
            ActivitySummary, start_date, end_date, False
        )
        date_pairs_exp = [
            (
                datetime(2020, 12, 30, 9, 48, tzinfo=pytz.UTC),
                datetime(2020, 12, 31, 9, 48, tzinfo=pytz.UTC),
            )
        ]
        self.assertEqual(len(date_pairs_obs), len(date_pairs_exp))
        for i, j in zip(date_pairs_obs, date_pairs_exp):
            self.assertEqual(i, j)

    def test_date_pairs_nonotif_more_days(self):
        start_date = datetime(2020, 12, 30, 9, 48, 0, tzinfo=pytz.UTC)
        end_date = datetime(2021, 1, 2, 9, 48, 37, tzinfo=pytz.UTC)
        date_pairs_obs = prepare_date_pairs(
            ActivitySummary, start_date, end_date, False
        )
        date_pairs_exp = [
            (
                datetime(2020, 12, 30, 9, 48, tzinfo=pytz.UTC),
                datetime(2020, 12, 31, 9, 48, tzinfo=pytz.UTC),
            ),
            (
                datetime(2020, 12, 31, 9, 48, tzinfo=pytz.UTC),
                datetime(2021, 1, 1, 9, 48, tzinfo=pytz.UTC),
            ),
            (
                datetime(2021, 1, 1, 9, 48, tzinfo=pytz.UTC),
                datetime(2021, 1, 2, 9, 48, tzinfo=pytz.UTC),
            ),
        ]
        self.assertEqual(len(date_pairs_obs), len(date_pairs_exp))
        for i, j in zip(date_pairs_obs, date_pairs_exp):
            self.assertEqual(i, j)
