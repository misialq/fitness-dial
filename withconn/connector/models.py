from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import (
    CharField,
    IntegerField,
    BooleanField,
    DateTimeField,
    FloatField,
)
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
    deep_sleep_duration = IntegerField(null=True)
    duration_to_sleep = IntegerField()
    duration_to_wakeup = IntegerField()
    hr_average = IntegerField(null=True)
    hr_max = IntegerField(null=True)
    hr_min = IntegerField(null=True)
    light_sleep_duration = IntegerField(null=True)
    rem_sleep_duration = IntegerField(null=True)
    rr_average = IntegerField(null=True)
    rr_max = IntegerField(null=True)
    rr_min = IntegerField(null=True)
    sleep_score = IntegerField(null=True)
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


class Weight(models.Model):
    id = ShortUUIDField(primary_key=True)
    reported_at = DateTimeField(default=timezone.now, blank=True)
    device_id = CharField(max_length=128)
    user_id = IntegerField()
    measured_at = DateTimeField()
    source = CharField(max_length=64)
    weight = FloatField(null=True)
    fat_free_mass = FloatField(null=True)
    fat_ratio = FloatField(null=True)
    fat_mass_weight = FloatField(null=True)
    muscle_mass = FloatField(null=True)
    hydration = FloatField(null=True)
    bone_mass = FloatField(null=True)
    pulse_wave_velocity = FloatField(null=True)
    heart_rate = IntegerField(null=True)


class ActivityRaw(models.Model):
    id = ShortUUIDField(primary_key=True)
    reported_at = DateTimeField(default=timezone.now, blank=True)
    device_type = CharField(max_length=128)
    device_id = IntegerField()
    user_id = IntegerField()
    measured_at = DateTimeField()
    steps = IntegerField(null=True)
    duration = IntegerField()
    distance = FloatField(null=True)
    elevation = IntegerField(null=True)
    calories = FloatField(null=True)
    heart_rate = IntegerField(null=True)
    measurement_type = CharField(max_length=32)


class ActivitySummary(models.Model):
    id = ShortUUIDField(primary_key=True)
    reported_at = DateTimeField(default=timezone.now, blank=True)
    device_type = CharField(max_length=128)
    device_id = IntegerField()
    user_id = IntegerField()
    measured_at = DateTimeField()
    is_tracker = BooleanField()
    steps = IntegerField(null=True)
    distance = FloatField(null=True)
    elevation = FloatField(null=True)
    calories = FloatField(null=True)
    soft_activities_duration = IntegerField(null=True)
    moderate_activities_duration = IntegerField(null=True)
    intense_activities_duration = IntegerField(null=True)
    active_duration = IntegerField(null=True)
    total_calories = FloatField(null=True)
    hr_average = IntegerField(null=True)
    hr_min = IntegerField(null=True)
    hr_max = IntegerField(null=True)
    hr_zone_light_duration = IntegerField(null=True)
    hr_zone_moderate_duration = IntegerField(null=True)
    hr_zone_intense_duration = IntegerField(null=True)
    hr_zone_max_duration = IntegerField(null=True)
    measurement_type = CharField(max_length=32)
