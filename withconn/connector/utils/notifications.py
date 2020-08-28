import requests


def subscribe_to_notifications(access_token: str, callback_url: str, appli: int):
    req_params = {
        "action": "subscribe",
        "callbackurl": callback_url,
        "appli": appli,
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    notify_response = requests.post(
        "https://wbsapi.withings.net/notify", data=req_params, headers=headers,
    )
    return notify_response


def fetch_all_notifications(access_token: str, appli: int):
    req_params = {
        "action": "list",
        "appli": appli,
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    notify_response = requests.post(
        "https://wbsapi.withings.net/notify", data=req_params, headers=headers
    )
    return notify_response
