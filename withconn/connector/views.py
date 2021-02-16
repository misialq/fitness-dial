import json
import logging
import os
from datetime import datetime

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import Nutrition, ActivitySummary, Weight, SleepSummary, SleepRaw
from .tasks import (
    celery_request_all_activity_data,
    celery_request_all_measurement_data,
    celery_request_all_sleep_data,
    celery_appli_44_sleep,
    celery_appli_1_measurements,
    celery_appli_16_activities,
)

from .utils.authentication import (
    get_valid_token,
    save_access_token,
    request_new_access_token,
    CALLBACK_URL,
)
from .utils.common import extract_and_parse_dates
from .utils.notifications import fetch_all_notifications, subscribe_to_notifications

LOGGER = logging.getLogger(__name__)
HASS_CALLBACK_URL = os.environ.get("HASS_CALLBACK_URL")


@csrf_exempt
def index(request):
    if request.method == "GET":
        code = request.GET.get("code")
        state = request.GET.get("state")
        response_type = request.GET.get("response_type")

        if code is not None and state == "token_request":
            token_response = request_new_access_token(code)
            if token_response.status_code != 200:
                return HttpResponseBadRequest("Token retrieval was unsuccessful.")
            save_access_token(token_response, user_id=123)
            return HttpResponse("Authorisation request was successful.")
        elif code == "notifupdate":
            appli = request.GET.get("appli")
            # TODO: figure out what the correct ID should be here
            user_id = 22336123
            valid_token_data = get_valid_token(user_id)

            notify_list_response = fetch_all_notifications(
                valid_token_data["access_token"], appli
            )
            LOGGER.debug(notify_list_response.text)
            subscribe_response = subscribe_to_notifications(
                valid_token_data["access_token"], CALLBACK_URL, appli,
            )
            LOGGER.debug(subscribe_response.text)

            return HttpResponse("OK")
        else:
            if response_type and response_type == "token_request":
                return HttpResponse("OK")
            else:
                # re-direct to Home Assistant (for IFTTT integration)
                return redirect(HASS_CALLBACK_URL)
    elif request.method == "POST":
        if request.body == b"":
            return HttpResponse("Empty request body.")

        body_list = request.body.decode("utf-8").split("&")
        json_body = {}
        for elem in body_list:
            elem_split = elem.split("=")
            json_body[elem_split[0]] = elem_split[1]
        appli = json_body["appli"]
        LOGGER.debug(json_body)

        if appli and int(appli) == 44:
            LOGGER.info("Received POST request for appli %s.", appli)
            celery_appli_44_sleep.delay(json_body)
            return HttpResponse("OK")
        elif appli and int(appli) == 1:
            LOGGER.info("Received POST request for appli %s.", appli)
            celery_appli_1_measurements.delay(json_body)
            return HttpResponse("OK")
        elif appli and int(appli) == 16:
            LOGGER.info("Received POST request for appli %s.", appli)
            celery_appli_16_activities.delay(json_body)
            return HttpResponse("OK")
        else:
            return HttpResponse("Unsupported appli.")


def check_sleep(request):
    LOGGER.info("New sleep request.")
    # extract query params
    start_date, end_date = extract_and_parse_dates(request)
    user_id = request.GET.get("user_id")

    # fetch a valid token
    LOGGER.info("Fetching valid token for user: %s", user_id)
    access_token_data = get_valid_token(user_id)

    # make data request
    LOGGER.debug("Executing celery sleep task.")
    celery_request_all_sleep_data.delay(
        access_token_data, user_id, start_date, end_date
    )
    return HttpResponse("OK")


def check_measurements(request):
    LOGGER.info("New measurement request.")
    # extract query params
    start_date, end_date = extract_and_parse_dates(request)
    user_id = request.GET.get("user_id")
    measurement_type = request.GET.get("measurement_types")

    if not measurement_type:
        # TODO: probably should raise an error here
        LOGGER.warning(
            "No measurement type was provided in the request. The following request to Withings API will likely fail."
        )

    # fetch a valid token
    LOGGER.info("Fetching valid token for user: %s", user_id)
    access_token_data = get_valid_token(user_id)

    # make data request
    LOGGER.debug("Executing celery measurements task.")
    celery_request_all_measurement_data.delay(
        access_token_data, user_id, start_date, end_date, measurement_type
    )
    return HttpResponse("OK")


def check_activity(request):
    LOGGER.info("New activity request.")
    # extract query params
    start_date, end_date = extract_and_parse_dates(request)
    user_id = request.GET.get("user_id")

    # fetch a valid token
    LOGGER.info("Fetching valid token for user: %s", user_id)
    access_token_data = get_valid_token(user_id)

    # make data request
    celery_request_all_activity_data.delay(
        access_token_data, user_id, start_date, end_date
    )
    return HttpResponse("OK")


def home(request):
    last_weight = Weight.objects.latest("measured_at")
    last_sleep_summary = SleepSummary.objects.latest("end_date")
    last_sleep_raw = SleepRaw.objects.latest("end_date")

    test_data = Weight.objects.all().order_by("-measured_at")[:10][::-1]
    dates = json.dumps([x.measured_at.strftime("%Y-%m-%d") for x in test_data])
    weights = [x.weight for x in test_data]

    context = {
        "dates": dates,
        "weights": weights,
        "last_weight": last_weight,
        "last_sleep_summary": last_sleep_summary,
        "last_sleep_raw": last_sleep_raw,
        "sleep_reported_at": datetime.timestamp(last_sleep_raw.reported_at),
        "sleep_summary_reported_at": datetime.timestamp(last_sleep_summary.reported_at),
        "weight_reported_at": datetime.timestamp(last_weight.reported_at),
    }
    return render(request, "dashboard.html", context)
