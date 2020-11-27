from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("check_sleep", views.check_sleep, name="check_sleep"),
    path("check_measurements", views.check_measurements, name="check_measurements"),
    path("check_activity", views.check_activity, name="check_activity"),
]
