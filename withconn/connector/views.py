import datetime
import logging
import os

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from .utils.authentication import (
    get_valid_token,
    CLIENT_ID,
    CLIENT_SECRET,
    save_access_token,
    request_new_access_token,
    CALLBACK_URL,
    get_authenticated_api,
)
from .utils.measurements import request_all_measurements_data, DATETIME_FORMAT
from .utils.notifications import fetch_all_notifications, subscribe_to_notifications
from .utils.sleep import request_all_sleep_data

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
            return HttpResponse(f"Authorisation request was successful.")
        elif code == "notifupdate":
            appli = request.GET.get("appli")
            # TODO: figure out what the correct ID should be here
            user_id = 123
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
            user_id = json_body["userid"]
            start_date = datetime.datetime.fromtimestamp(int(json_body["startdate"]))
            end_date = datetime.datetime.fromtimestamp(int(json_body["enddate"]))

            # fetch a valid token
            LOGGER.info("Fetching valid token for user: %s", user_id)
            access_token_data = get_valid_token(user_id)

            # make data request
            LOGGER.info("Authenticating Withings API...")
            wapi = get_authenticated_api(
                access_token_data=access_token_data,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
            )
            LOGGER.info(
                "Fetching sleep entries for dates: %s to %s...",
                start_date.strftime(DATETIME_FORMAT),
                end_date.strftime(DATETIME_FORMAT),
            )
            raw_counter, summary_counter = request_all_sleep_data(
                wapi, start_date, end_date
            )
            LOGGER.info(
                "Fetched and updated %s raw sleep entries and %s summary sleep entries",
                raw_counter,
                summary_counter,
            )
            return HttpResponse("OK")
        elif appli and int(appli) == 1:
            LOGGER.info("Received POST request for appli %s.", appli)
            user_id = json_body["userid"]
            start_date = datetime.datetime.fromtimestamp(int(json_body["startdate"]))
            end_date = datetime.datetime.fromtimestamp(int(json_body["enddate"]))

            # fetch a valid token
            LOGGER.info("Fetching valid token for user: %s", user_id)
            access_token_data = get_valid_token(user_id)

            # make data request
            LOGGER.info("Authenticating Withings API...")
            wapi = get_authenticated_api(
                access_token_data=access_token_data,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
            )
            LOGGER.info(
                "Fetching measurements of type 'weight' for dates %s to %s...",
                start_date.strftime(DATETIME_FORMAT),
                end_date.strftime(DATETIME_FORMAT),
            )
            measurements_counter = request_all_measurements_data(
                wapi, "weight", start_date, end_date
            )
            LOGGER.info(
                "Fetched and updated %s weight measurement entries.",
                measurements_counter,
            )
            return HttpResponse("OK")
        else:
            return HttpResponse("Unsupported appli.")


def check_sleep(request):
    LOGGER.info("New sleep request.")
    # extract query params
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    user_id = request.GET.get("user_id")

    if not end_date:
        end_date = datetime.datetime.now()
    else:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(hour=11)

    if not start_date:
        start_date = end_date - datetime.timedelta(hours=24)
    else:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(hour=18)

    # fetch a valid token
    LOGGER.info("Fetching valid token for user: %s", user_id)
    access_token_data = get_valid_token(user_id)

    # make data request
    LOGGER.info("Authenticating Withings API...")
    wapi = get_authenticated_api(
        access_token_data=access_token_data,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    LOGGER.info(
        "Fetching sleep entries for dates: %s to %s...",
        start_date.strftime(DATETIME_FORMAT),
        end_date.strftime(DATETIME_FORMAT),
    )
    raw_counter, summary_counter = request_all_sleep_data(wapi, start_date, end_date)
    return HttpResponse(
        f"Fetched and updated:\n\t{raw_counter} new raw sleep entries\n\t{summary_counter} new summary sleep entries."
    )


def check_measurements(request):
    LOGGER.info("New measurement request.")
    # extract query params
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    user_id = request.GET.get("user_id")
    measurement_types = request.GET.get("measurement_types")

    if not end_date:
        end_date = datetime.datetime.now()
    else:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(hour=11)

    if not start_date:
        start_date = end_date - datetime.timedelta(hours=24)
    else:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(hour=18)

    if not measurement_types:
        # TODO: probably should raise an error here
        LOGGER.warning(
            "No measurement type was provided in the request. The following request to Withings API will likely fail."
        )
        measurement_types = None
    else:
        measurement_types = measurement_types.split(",")

    # fetch a valid token
    LOGGER.info("Fetching valid token for user: %s", user_id)
    access_token_data = get_valid_token(user_id)

    # make data request
    LOGGER.info("Authenticating Withings API...")
    wapi = get_authenticated_api(
        access_token_data=access_token_data,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    counters = []
    for meas in measurement_types:
        LOGGER.info(
            "Fetching measurements of type '%s' for dates %s to %s...",
            meas,
            start_date.strftime(DATETIME_FORMAT),
            end_date.strftime(DATETIME_FORMAT),
        )
        measurements_count = request_all_measurements_data(
            wapi, meas, start_date, end_date
        )
        counters.append(measurements_count)

    return HttpResponse(
        f"Fetched and updated: [{','.join([str(x) for x in counters])}] entries for the following measurement types:"
        f" [{','.join(measurement_types)}]."
    )
