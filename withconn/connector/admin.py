from django.contrib import admin

# Register your models here.
from .models import WithingsAuthentication, SleepSummary, SleepRaw, Weight

admin.site.register(WithingsAuthentication)
admin.site.register(SleepSummary)
admin.site.register(SleepRaw)
admin.site.register(Weight)
