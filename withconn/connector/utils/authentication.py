import datetime
import json
import logging
import os

import requests
from django.db.models import Q
from django.utils import timezone

from ..models import WithingsAuthentication

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CALLBACK_URL = os.environ.get("CALLBACK_URL")
LOGGER = logging.getLogger(__name__)


class AuthenticationError(Exception):
    pass


def get_valid_token(user_id):
    LOGGER.debug("Filtering DB for a valid token...")
    valid_tokens = WithingsAuthentication.objects.filter(expired=False)
    # if none available -> make a refresh request and insert into table
    if len(valid_tokens) == 0:
        LOGGER.debug(
            "No valid token could be found. Attempting to refresh the last token."
        )
        if len(WithingsAuthentication.objects.all()) == 0:
            raise AuthenticationError("No available access tokens.")
        sorted_access_tokens = WithingsAuthentication.objects.filter(
            valid_to__isnull=False
        ).order_by("valid_to")

        # refresh with retries since there could be more than one token with a similar timestamp
        # and we don't know which is the correct one to be refreshed
        refresh_response = refresh_token_with_retries(
            sorted_access_tokens, max_refresh_attempts=3
        )
        access_token_data = save_access_token(refresh_response, user_id=user_id)
    elif len(valid_tokens) == 1:
        LOGGER.debug("Found one valid token. Checking expiration time.")
        current_token = valid_tokens[0]

        # TODO: move this whole check to a periodic celery task
        if current_token.valid_to < timezone.now():
            LOGGER.debug("Token has expired. Refreshing.")
            current_token.expired = True
            current_token.save()
            refresh_response = refresh_access_token(current_token.refresh_token)
            access_token_data = save_access_token(refresh_response, user_id=user_id)
        else:
            LOGGER.debug("Token is valid and has not yet expired.")
            access_token_data = construct_api_data_from_token(current_token)
    else:
        LOGGER.debug(
            "Found more than one valid token. Invalidating all but the last one."
        )
        # mark all but one as invalid and refresh that one
        last_valid_token = valid_tokens.latest("valid_to")
        valid_tokens.filter(~Q(id=last_valid_token.id)).update(expired=True)

        # re-query to get the last and only valid token
        access_token_data = construct_api_data_from_token(last_valid_token)
    return access_token_data


def construct_api_data_from_token(token: WithingsAuthentication) -> dict:
    token_data = {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "expires_in": token.expires_in,
        "userid": token.user_id,
        "token_type": token.token_type,
    }
    return token_data


def refresh_token_with_retries(tokens_sorted_byt_time, max_refresh_attempts):
    refresh_attempts = 0
    tokens_count = tokens_sorted_byt_time.count()
    while refresh_attempts < max_refresh_attempts:
        try:
            token_index = tokens_count - (1 + refresh_attempts)
            current_refresh_token = tokens_sorted_byt_time[token_index]
            LOGGER.debug(f"Attempting to refresh {current_refresh_token.id} token...")
            refresh_response = refresh_access_token(current_refresh_token.refresh_token)
            break
        except AuthenticationError as e:
            LOGGER.debug(
                f"Refresh token attempt {refresh_attempts+1} failed. Retrying..."
            )
            if refresh_attempts + 1 == max_refresh_attempts:
                raise e
            refresh_attempts += 1
            continue
        # maybe we need an IndexError handler, just in case...
    return refresh_response


def request_new_access_token(code: str):
    req_params = {
        "action": "requesttoken",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": CALLBACK_URL,
    }
    token_response = requests.post(
        "https://wbsapi.withings.net/v2/oauth2", data=req_params
    )

    json_response = json.loads(token_response.text)
    if json_response["status"] >= 500:
        raise AuthenticationError(
            "Error while requesting a new token: %s", json_response["error"]
        )
    else:
        LOGGER.debug(
            "Token request response: %s, status: %s",
            token_response.text,
            token_response.status_code,
        )

    return token_response


def save_access_token(token_response, user_id: int):
    response_body = json.loads(token_response.text)
    access_token = response_body["body"].get("access_token")
    refresh_token = response_body["body"].get("refresh_token")
    expires_in = response_body["body"].get("expires_in")
    scope = response_body["body"].get("scope")
    token_type = response_body["body"].get("token_type")

    new_token = WithingsAuthentication(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        valid_to=timezone.now() + datetime.timedelta(seconds=expires_in),
        scope=scope.split(","),
        token_type=token_type,
        user_id=user_id,
        demo=False,
        expired=False,
    )
    new_token.save()

    response_body["body"]["userid"] = user_id
    return response_body["body"]


def refresh_access_token(valid_refresh_token):
    LOGGER.info("Refreshing access token...")
    req_params = {
        "action": "requesttoken",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": valid_refresh_token,
    }
    token_response = requests.post(
        "https://wbsapi.withings.net/v2/oauth2", data=req_params
    )

    json_response = json.loads(token_response.text)
    if json_response["status"] >= 500:
        raise AuthenticationError(
            "Error while refreshing the token: %s", json_response["error"]
        )
    else:
        LOGGER.debug(
            "Token refresh response: %s, status: %s",
            token_response.text,
            token_response.status_code,
        )
    return token_response
