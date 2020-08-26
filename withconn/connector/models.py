from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import CharField, IntegerField, BooleanField, DateTimeField
from django.utils import timezone
from shortuuidfield import ShortUUIDField


class WithingsAuthentication(models.Model):
    id = ShortUUIDField(primary_key=True)
    access_token = CharField(max_length=128)
    refresh_token = CharField(max_length=128)
    expires_in = IntegerField()
    valid_from = DateTimeField(default=timezone.now, blank=True)
    valid_to = DateTimeField()
    scope = ArrayField(models.CharField(max_length=32, blank=True), size=16)
    token_type = CharField(max_length=128, default="Bearer")
    user_id = IntegerField()
    demo = BooleanField()
    expired = BooleanField()


class SleepSummary(models.Model):
    id = ShortUUIDField(primary_key=True)
    reported_at = DateTimeField(default=timezone.now, blank=True)
    start_date = DateTimeField()
    end_date = DateTimeField()
    user_id = IntegerField()
    device_type = CharField(max_length=128)
    device_id = IntegerField()
    breathing_disturbances_intensity = IntegerField()
    deep_sleep_duration = IntegerField()
    duration_to_sleep = IntegerField()
    duration_to_wakeup = IntegerField()
    hr_average = IntegerField()
    hr_max = IntegerField()
    hr_min = IntegerField()
    light_sleep_duration = IntegerField()
    rem_sleep_duration = IntegerField()
    rr_average = IntegerField()
    rr_max = IntegerField()
    rr_min = IntegerField()
    sleep_score = IntegerField()
    snoring = IntegerField()
    snoring_episode_count = IntegerField()
    wakeup_count = IntegerField()
    wakeup_duration = IntegerField()


class SleepRaw(models.Model):
    id = ShortUUIDField(primary_key=True)
    reported_at = DateTimeField(default=timezone.now, blank=True)
    device_type = CharField(max_length=128)
    device_id = IntegerField()
    user_id = IntegerField()
    start_date = DateTimeField()
    end_date = DateTimeField()
    sleep_phase = CharField(max_length=32)
    sleep_phase_id = IntegerField()
    hr_series = ArrayField(models.JSONField())
    rr_series = ArrayField(models.JSONField())
    snoring_series = ArrayField(models.JSONField())
