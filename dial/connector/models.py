from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import (
    CharField,
    IntegerField,
    BooleanField,
    DateTimeField,
    FloatField, EmailField,
)
from django.utils import timezone
from django.utils.timezone import make_aware
from shortuuidfield import ShortUUIDField


MEAL_TYPES = [
    ("Breakfast", "Breakfast"),
    ("Lunch", "Lunch"),
    ("Dinner", "Dinner"),
    ("Snacks", "Snacks"),
    ("Other", "Other"),
]
MEAL_DATA_SOURCES = [("MyFitnessPal", "MyFitnessPal")]


class APIUser(models.Model):
    id = ShortUUIDField(primary_key=True)
    first_name = CharField(max_length=30)
    last_name = CharField(max_length=30)
    email = EmailField()
    user_id = IntegerField(unique=True)
    demo = BooleanField()
    height = FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(2.5)])
    date_of_birth = DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class WithingsAuthentication(models.Model):
    id = ShortUUIDField(primary_key=True)
    access_token = CharField(max_length=128)
    refresh_token = CharField(max_length=128)
    expires_in = IntegerField()
    valid_from = DateTimeField(default=timezone.now, blank=True)
    valid_to = DateTimeField()
    scope = ArrayField(models.CharField(max_length=32, blank=True), size=16)
    token_type = CharField(max_length=128, default="Bearer")
    user = models.ForeignKey(APIUser, on_delete=models.CASCADE)
    demo = BooleanField()
    expired = BooleanField()


class SleepSummary(models.Model):
    id = ShortUUIDField(primary_key=True)
    reported_at = DateTimeField(default=timezone.now, blank=True)
    start_date = DateTimeField()
    end_date = DateTimeField()
    user = models.ForeignKey(APIUser, on_delete=models.CASCADE)
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
    user = models.ForeignKey(APIUser, on_delete=models.CASCADE)
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
    user = models.ForeignKey(APIUser, on_delete=models.CASCADE)
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
    user = models.ForeignKey(APIUser, on_delete=models.CASCADE)
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
    user = models.ForeignKey(APIUser, on_delete=models.CASCADE)
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


class Nutrition(models.Model):
    id = ShortUUIDField(primary_key=True)
    reported_at = DateTimeField(default=timezone.now, blank=True)
    user = models.ForeignKey(APIUser, on_delete=models.CASCADE)
    start_date = DateTimeField()
    end_date = DateTimeField()
    meal = models.CharField(choices=MEAL_TYPES, max_length=16)
    data_source = models.CharField(
        choices=MEAL_DATA_SOURCES, max_length=16, default="MyFitnessPal"
    )
    calories = FloatField()
    total_fat = FloatField()
    saturated_fat = FloatField()
    trans_fat = FloatField()
    cholesterol = FloatField()
    sodium = FloatField()
    carbohydrates = FloatField()
    sugar = FloatField()
    fiber = FloatField()
    protein = FloatField()
