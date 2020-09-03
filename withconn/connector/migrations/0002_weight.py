# Generated by Django 3.1 on 2020-08-30 16:44

from django.db import migrations, models
import django.utils.timezone
import shortuuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ("connector", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Weight",
            fields=[
                (
                    "id",
                    shortuuidfield.fields.ShortUUIDField(
                        blank=True,
                        editable=False,
                        max_length=22,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "reported_at",
                    models.DateTimeField(blank=True, default=django.utils.timezone.now),
                ),
                ("device_id", models.CharField(max_length=128)),
                ("user_id", models.IntegerField()),
                ("measured_at", models.DateTimeField()),
                ("source", models.CharField(max_length=64)),
                ("weight", models.FloatField()),
                ("fat_free_mass", models.FloatField(null=True)),
                ("fat_ratio", models.FloatField(null=True)),
                ("fat_mass_weight", models.FloatField(null=True)),
                ("muscle_mass", models.FloatField(null=True)),
                ("hydration", models.FloatField(null=True)),
                ("bone_mass", models.FloatField(null=True)),
                ("pulse_wave_velocity", models.FloatField(null=True)),
                ("heart_rate", models.IntegerField(null=True)),
            ],
        ),
    ]
