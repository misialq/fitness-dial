from django.contrib import admin

# Register your models here.
from .models import (
    WithingsAuthentication,
    SleepSummary,
    SleepRaw,
    Weight,
    ActivityRaw,
    ActivitySummary,
)

admin.site.register(WithingsAuthentication)
admin.site.register(SleepSummary)
admin.site.register(SleepRaw)
admin.site.register(Weight)
admin.site.register(ActivityRaw)
admin.site.register(ActivitySummary)
