# Register your models here.
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportActionModelAdmin
from import_export.widgets import DateTimeWidget

from .models import (
    WithingsAuthentication,
    SleepSummary,
    SleepRaw,
    Weight,
    ActivityRaw,
    ActivitySummary,
    Nutrition,
)


class NutritionResource(resources.ModelResource):
    start_date = fields.Field(
        column_name="Date",
        attribute="start_date",
        widget=DateTimeWidget(format="%d.%m.%y"),
    )
    meal = fields.Field(column_name="Meal", attribute="meal")
    calories = fields.Field(column_name="Calories", attribute="calories")
    total_fat = fields.Field(column_name="Fat (g)", attribute="total_fat")
    saturated_fat = fields.Field(column_name="Saturated Fat", attribute="saturated_fat")
    trans_fat = fields.Field(column_name="Trans Fat", attribute="trans_fat")
    cholesterol = fields.Field(column_name="Cholesterol", attribute="cholesterol")
    sodium = fields.Field(column_name="Sodium (mg)", attribute="sodium")
    carbohydrates = fields.Field(
        column_name="Carbohydrates (g)", attribute="carbohydrates"
    )
    sugar = fields.Field(column_name="Sugar", attribute="sugar")
    fiber = fields.Field(column_name="Fiber", attribute="fiber")
    protein = fields.Field(column_name="Protein (g)", attribute="protein")

    class Meta:
        model = Nutrition
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "reported_at", "start_date", "end_date")
        import_id_fields = ("start_date", "meal")

    def before_save_instance(self, instance, using_transactions, dry_run):
        instance.end_date = instance.start_date.replace(hour=23, minute=59, second=59)
        return instance


class NutritionAdmin(ImportExportActionModelAdmin):
    resource_class = NutritionResource


admin.site.register(WithingsAuthentication)
admin.site.register(SleepSummary)
admin.site.register(SleepRaw)
admin.site.register(Weight)
admin.site.register(ActivityRaw)
admin.site.register(ActivitySummary)
admin.site.register(Nutrition, NutritionAdmin)
