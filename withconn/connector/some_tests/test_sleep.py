# from datetime import datetime
# from unittest.mock import patch
#
# import pytz
# from django.test import TestCase
# from ..models import SleepSummary, SleepRaw
# from ..utils.sleep import DATETIME_FORMAT
#
# START_DATE = datetime.strptime("20201210-211000", "%Y%m%d-%H%M%S").astimezone(pytz.utc)
# END_DATE = datetime.strptime("20201210-211140", "%Y%m%d-%H%M%S").astimezone(pytz.utc)
#
#
# def generate_series(series_values):
#     time_and_values = []
#     for i, val in enumerate(series_values):
#         date = (
#             datetime.strptime(f"20201209-220{i}00", "%Y%m%d-%H%M%S")
#             .astimezone(pytz.utc)
#             .strftime(DATETIME_FORMAT)
#         )
#         time_and_values.append({"timestamp": date, "value": val})
#     return time_and_values
#
#
# def my_time():
#     return datetime.strptime("20201210-211000", "%Y%m%d-%H%M%S")
#
#
# class SleepSummaryTestCase(TestCase):
#     def setUp(self):
#         SleepSummary.objects.create(
#             start_date=START_DATE,
#             end_date=END_DATE,
#             user_id=123,
#             device_type="test_device",
#             device_id=1,
#             breathing_disturbances_intensity=4,
#             deep_sleep_duration=100,
#             duration_to_sleep=200,
#             duration_to_wakeup=10,
#             hr_average=123,
#             hr_max=220,
#             hr_min=55,
#             light_sleep_duration=2000,
#             rem_sleep_duration=120,
#             rr_average=11,
#             rr_max=15,
#             rr_min=5,
#             sleep_score=90,
#             snoring=0,
#             snoring_episode_count=1,
#             wakeup_count=1,
#             wakeup_duration=20,
#         )
#
#         SleepRaw.objects.create(
#             start_date=START_DATE,
#             end_date=END_DATE,
#             user_id=123,
#             device_type="test_device",
#             device_id=1,
#             sleep_phase="deep",
#             sleep_phase_id=1,
#             hr_series=generate_series([50, 55, 60]),
#             rr_series=generate_series([15, 16, 17]),
#             snoring_series=generate_series([0, 1, 2]),
#         )
#
#     # def test_sleep_summary(self):
#     #     sleep = SleepSummary.objects.get(start_date=START_DATE)
#     #     self.assertEqual(sleep.end_date, END_DATE)
#     #     self.assertEqual(sleep.user_id, 123)
#     #     self.assertEqual(sleep.device_type, "test_device")
#     #     self.assertEqual(sleep.wakeup_duration, 20)
#     #     self.assertEqual(sleep.deep_sleep_duration, 100)
#     #
#     # def test_sleep_raw(self):
#     #     sleep = SleepRaw.objects.get(start_date=START_DATE)
#     #     self.assertEqual(sleep.end_date, END_DATE)
#     #     self.assertEqual(sleep.user_id, 123)
#     #     self.assertEqual(sleep.device_type, "test_device")
#     #     for obs, exp in zip(sleep.hr_series, generate_series([50, 55, 60])):
#     #         self.assertEqual(obs, exp)
#     #     for obs, exp in zip(sleep.rr_series, generate_series([15, 16, 17])):
#     #         self.assertEqual(obs, exp)
#     #     for obs, exp in zip(sleep.snoring_series, generate_series([0, 1, 2])):
#     #         self.assertEqual(obs, exp)
