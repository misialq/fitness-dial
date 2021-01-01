# import json
# from datetime import datetime
# from unittest.mock import patch, MagicMock
#
# import pytz
# from django.test import TestCase
# from testfixtures import Replace, test_datetime
#
# from ..fake_responses import (
#     DATE1,
#     DATE2,
#     FAKE_ACTIVITY_SUMMARY_RESPONSE,
# )
# from ...models import ActivitySummary
# from ..activity import get_activity_summary
#
#
# class ActivitySummaryTestCase(TestCase):
#     def setUp(self):
#         self.fake_token = "token124"
#         self.user_id = 123
#         self.start_date = datetime.strptime("20201208-211000", "%Y%m%d-%H%M%S")
#         self.end_date = datetime.strptime("20201208-221000", "%Y%m%d-%H%M%S")
#
#         ActivitySummary.objects.create(
#             user_id=123,
#             device_type="test_device",
#             device_id=1,
#             measured_at=datetime.strptime(
#                 "20201208-210500", "%Y%m%d-%H%M%S"
#             ).astimezone(pytz.utc),
#             is_tracker=True,
#             steps=6150,
#             distance=5663.541,
#             elevation=0,
#             calories=659.677,
#             soft_activities_duration=7620,
#             moderate_activities_duration=3840,
#             intense_activities_duration=1620,
#             active_duration=5460,
#             total_calories=2352.961,
#             hr_average=85,
#             hr_max=123,
#             hr_min=46,
#             hr_zone_light_duration=18259,
#             hr_zone_moderate_duration=4682,
#             hr_zone_intense_duration=0,
#             hr_zone_max_duration=0,
#             measurement_type="steps",
#         )
#
#     @patch("connector.utils.activity.requests.post")
#     def test_activity_summary(self, patched_post):
#         request_response = MagicMock()
#         request_response.text = json.dumps(FAKE_ACTIVITY_SUMMARY_RESPONSE)
#         patched_post.return_value = request_response
#         with Replace(
#             "connector.utils.activity.datetime", test_datetime(2020, 12, 9, 21, 11, 40)
#         ):
#             obs_counter = get_activity_summary(
#                 access_token=self.fake_token,
#                 user_id=self.user_id,
#                 start_date=self.start_date,
#                 end_date=self.end_date,
#                 offset=None,
#                 from_notification=True,
#             )
#             self.assertEqual(obs_counter, 2)
#
#             expected_activities = FAKE_ACTIVITY_SUMMARY_RESPONSE["body"]["activities"]
#             for i, date in enumerate((DATE1, DATE2)):
#                 activity_result = ActivitySummary.objects.get(measured_at=date)
#                 self.assertEqual(activity_result.user_id, 123)
#                 self.assertEqual(
#                     activity_result.device_type, str(expected_activities[i]["brand"])
#                 )
#                 self.assertEqual(activity_result.device_id, 0)
#                 self.assertEqual(
#                     activity_result.is_tracker, expected_activities[i]["is_tracker"]
#                 )
#                 self.assertEqual(activity_result.steps, expected_activities[i]["steps"])
#                 self.assertEqual(
#                     activity_result.distance, expected_activities[i]["distance"]
#                 )
#                 self.assertEqual(
#                     activity_result.elevation, expected_activities[i]["elevation"]
#                 )
#                 self.assertEqual(
#                     activity_result.calories, expected_activities[i]["calories"]
#                 )
#                 self.assertEqual(
#                     activity_result.soft_activities_duration,
#                     expected_activities[i]["soft"],
#                 )
#                 self.assertEqual(
#                     activity_result.moderate_activities_duration,
#                     expected_activities[i]["moderate"],
#                 )
#                 self.assertEqual(
#                     activity_result.intense_activities_duration,
#                     expected_activities[i]["intense"],
#                 )
#                 self.assertEqual(
#                     activity_result.active_duration, expected_activities[i]["active"]
#                 )
#                 self.assertEqual(
#                     activity_result.total_calories,
#                     expected_activities[i]["totalcalories"],
#                 )
#                 self.assertEqual(
#                     activity_result.hr_min, expected_activities[i]["hr_min"]
#                 )
#                 self.assertEqual(
#                     activity_result.hr_max, expected_activities[i]["hr_max"]
#                 )
#                 self.assertEqual(
#                     activity_result.hr_zone_light_duration,
#                     expected_activities[i]["hr_zone_0"],
#                 )
#                 self.assertEqual(
#                     activity_result.hr_zone_moderate_duration,
#                     expected_activities[i]["hr_zone_1"],
#                 )
#                 self.assertEqual(
#                     activity_result.hr_zone_intense_duration,
#                     expected_activities[i]["hr_zone_2"],
#                 )
#                 self.assertEqual(
#                     activity_result.hr_zone_max_duration,
#                     expected_activities[i]["hr_zone_3"],
#                 )
#                 self.assertEqual(activity_result.measurement_type, "steps")
