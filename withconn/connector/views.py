import datetime
import os

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect

from .utils.authentication import (
    get_valid_token,
    CLIENT_ID,
    CLIENT_SECRET,
    save_access_token,
    request_new_access_token,
    CALLBACK_URL,
)
from .utils.notifications import fetch_all_notifications, subscribe_to_notifications
from .utils.sleep import (
    get_authenticated_api,
    request_all_sleep_data,
)

HASS_CALLBACK_URL = os.environ.get("HASS_CALLBACK_URL")


def index(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    if code is not None and state == "token_request":
        token_response = request_new_access_token(code)
        if token_response.status_code != 200:
            return HttpResponseBadRequest("Token retrieval was unsuccessful.")
        save_access_token(token_response, user_id=123)
        return HttpResponse(f"Authorisation request was successful.")
    elif code == "notifupdate":
        # TODO: figure out what the correct ID should be here
        user_id = 123
        valid_token_data = get_valid_token(user_id)
        notify_list_response = fetch_all_notifications(
            valid_token_data["access_token"], 44
        )
        subscribe_response = subscribe_to_notifications(
            valid_token_data["access_token"], CALLBACK_URL, 44,
        )
        return HttpResponse("OK")
    else:
        appli = request.GET.get("appli")
        response_type = request.GET.get("response_type")
        if appli and int(appli) == 44:
            user_id = request.GET.get("userid")
            start_date = request.GET.get("startdate")
            end_date = request.GET.get("enddate")

            # fetch a valid token
            access_token_data = get_valid_token(user_id)

            # make data request
            wapi = get_authenticated_api(
                access_token_data=access_token_data,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
            )
            raw_counter, summary_counter = request_all_sleep_data(
                wapi, start_date, end_date
            )
            return HttpResponse("OK")
        elif response_type and response_type == "token_request":
            return HttpResponse("OK")
        else:
            # re-direct to Home Assistant (for IFTTT integration)
            return redirect(HASS_CALLBACK_URL)


def check_sleep(request):
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
    access_token_data = get_valid_token(user_id)

    # make data request
    wapi = get_authenticated_api(
        access_token_data=access_token_data,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    raw_counter, summary_counter = request_all_sleep_data(wapi, start_date, end_date)
    return HttpResponse(
        f"Fetched and updated:\n\t{raw_counter} new raw sleep entries\n\t{summary_counter} new summary sleep entries."
    )
