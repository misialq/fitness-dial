from datetime import datetime

import pytz
from django.test import TestCase

from ..models import APIUser


class DialTestBase(TestCase):
    def setUp(self):
        self.fake_token = "token124"
        self.user = APIUser.objects.get_or_create(
            first_name='Test',
            last_name='User',
            email='test@user.com',
            user_id=123,
            demo=False,
            height=1.55
        )[0]
        self.start_date = datetime(2020, 12, 30, 9, 48, 0, tzinfo=pytz.UTC)
