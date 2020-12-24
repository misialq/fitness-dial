from flask import Flask, json, request, abort

from datetime import datetime

import pytz

DATETIME_FORMAT = "%Y-%m-%d"
DATE1_STR = "2020-12-08"
DATE2_STR = "2020-12-09"
DATE1 = datetime.strptime(DATE1_STR, DATETIME_FORMAT).astimezone(pytz.utc)
DATE2 = datetime.strptime(DATE2_STR, DATETIME_FORMAT).astimezone(pytz.utc)

FAKE_ACTIVITY_SUMMARY_RESPONSE = {
    "status": 0,
    "body": {
        "activities": [
            {
                "steps": 6150,
                "distance": 5663.541,
                "elevation": 0,
                "soft": 7620,
                "moderate": 3840,
                "intense": 1620,
                "active": 5460,
                "calories": 659.677,
                "totalcalories": 2352.961,
                "hr_average": 85,
                "hr_min": 46,
                "hr_max": 123,
                "hr_zone_0": 18259,
                "hr_zone_1": 4682,
                "hr_zone_2": 0,
                "hr_zone_3": 0,
                "deviceid": None,
                "timezone": "Europe/Zurich",
                "date": DATE1_STR,
                "brand": 18,
                "is_tracker": True,
            },
            {
                "steps": 4478,
                "distance": 3866.991,
                "elevation": 0,
                "soft": 11340,
                "moderate": 960,
                "intense": 780,
                "active": 1740,
                "calories": 214.041,
                "totalcalories": 1920.355,
                "hr_average": 81,
                "hr_min": 37,
                "hr_max": 182,
                "hr_zone_0": 38561,
                "hr_zone_1": 2400,
                "hr_zone_2": 510,
                "hr_zone_3": 188,
                "deviceid": None,
                "timezone": "Europe/Zurich",
                "date": DATE2_STR,
                "brand": 18,
                "is_tracker": True,
            },
        ],
        "more": False,
        "offset": 0,
    },
}

FAKE_ACTIVITY_RAW_RESPONSE = {
    "status": 0,
    "body": {
        "series": {
            "1608915169": {
                "heart_rate": 68,
                "duration": 54,
                "model": "Activite Steel HR",
                "model_id": 55,
                "deviceid": "1e8df52d866090062f9b67b7eece26488222a215",
            },
            "1608915300": {
                "steps": 7,
                "duration": 60,
                "elevation": 0,
                "distance": 4.74,
                "calories": 0.17,
                "model": "Activite Steel HR",
                "model_id": 55,
                "deviceid": "1e8df52d866090062f9b67b7eece26488222a215",
            },
            "1608915420": {
                "steps": 0,
                "duration": 60,
                "elevation": 0,
                "distance": 0,
                "calories": 0,
                "model": "Activite Steel HR",
                "model_id": 55,
                "deviceid": "1e8df52d866090062f9b67b7eece26488222a215",
            },
        }
    },
}

FAKE_SLEEP_SUMMARY_RESPONSE = {
    "status": 0,
    "body": {
        "series": [
            {
                "id": 1745353993,
                "timezone": "Europe/Zurich",
                "model": 32,
                "model_id": 63,
                "startdate": 1607379840,
                "enddate": 1607407260,
                "date": "2020-12-08",
                "data": {
                    "wakeupduration": 2520,
                    "lightsleepduration": 13380,
                    "deepsleepduration": 4440,
                    "wakeupcount": 2,
                    "durationtosleep": 1380,
                    "remsleepduration": 6120,
                    "durationtowakeup": 0,
                    "hr_average": 54,
                    "hr_min": 47,
                    "hr_max": 67,
                    "rr_average": 12,
                    "rr_min": 9,
                    "rr_max": 21,
                    "breathing_disturbances_intensity": 11,
                    "snoring": 3000,
                    "snoringepisodecount": 9,
                    "sleep_score": 75,
                },
                "created": 1607404049,
                "modified": 1607414646,
            },
            {
                "id": 1745568899,
                "timezone": "Europe/Zurich",
                "model": 16,
                "model_id": 55,
                "startdate": 1607381580,
                "enddate": 1607407380,
                "date": "2020-12-08",
                "data": {
                    "wakeupduration": 780,
                    "lightsleepduration": 13860,
                    "deepsleepduration": 11160,
                    "wakeupcount": 3,
                    "durationtosleep": 120,
                    "durationtowakeup": 60,
                    "hr_average": 0,
                    "hr_min": 0,
                    "hr_max": 0,
                },
                "created": 1607410769,
                "modified": 1607410769,
            },
            {
                "id": 1747254173,
                "timezone": "Europe/Zurich",
                "model": 32,
                "model_id": 63,
                "startdate": 1607466660,
                "enddate": 1607493600,
                "date": "2020-12-09",
                "data": {
                    "wakeupduration": 1200,
                    "lightsleepduration": 10020,
                    "deepsleepduration": 6180,
                    "wakeupcount": 3,
                    "durationtosleep": 600,
                    "remsleepduration": 9180,
                    "durationtowakeup": 0,
                    "hr_average": 57,
                    "hr_min": 50,
                    "hr_max": 70,
                    "rr_average": 12,
                    "rr_min": 9,
                    "rr_max": 17,
                    "breathing_disturbances_intensity": 11,
                    "snoring": 1800,
                    "snoringepisodecount": 2,
                    "sleep_score": 92,
                },
                "created": 1607467986,
                "modified": 1607500989,
            },
            {
                "id": 1747466534,
                "timezone": "Europe\/Zurich",
                "model": 16,
                "model_id": 55,
                "startdate": 1607466240,
                "enddate": 1607493720,
                "date": "2020-12-09",
                "data": {
                    "wakeupduration": 720,
                    "lightsleepduration": 12720,
                    "deepsleepduration": 14040,
                    "wakeupcount": 1,
                    "durationtosleep": 120,
                    "durationtowakeup": 120,
                    "hr_average": 60,
                    "hr_min": 51,
                    "hr_max": 79,
                    "sleep_score": 85,
                },
                "created": 1607482150,
                "modified": 1607494754,
            },
        ],
        "more": False,
        "offset": 0,
    },
}

FAKE_SLEEP_RAW_RESPONSE = {
    "status": 0,
    "body": {
        "series": [
            {
                "startdate": 1607385600,
                "state": 1,
                "enddate": 1607385720,
                "model": "Aura Sensor V2",
                "hr": {"1607385600": 52, "1607385660": 51},
                "rr": {"1607385600": 11, "1607385660": 12},
                "snoring": {"1607385600": 0, "1607385660": 100},
                "model_id": 63,
            },
            {
                "startdate": 1607386200,
                "state": 1,
                "enddate": 1607386260,
                "model": "Aura Sensor V2",
                "hr": {"1607386200": 51},
                "rr": {"1607386200": 12},
                "snoring": {"1607386200": 100},
                "model_id": 63,
            },
            {
                "startdate": 1607391600,
                "state": 0,
                "enddate": 1607392200,
                "model": "Aura Sensor V2",
                "hr": {
                    "1607391600": 64,
                    "1607391660": 66,
                    "1607391720": 66,
                    "1607391780": 53,
                    "1607391840": 58,
                    "1607391900": 57,
                    "1607391960": 52,
                    "1607392020": 54,
                    "1607392080": 55,
                    "1607392140": 57,
                },
                "rr": {
                    "1607391600": 13,
                    "1607391660": 13,
                    "1607391720": 13,
                    "1607391780": 11,
                    "1607391840": 9,
                    "1607391900": 11,
                    "1607391960": 11,
                    "1607392020": 12,
                    "1607392080": 12,
                    "1607392140": 13,
                },
                "snoring": {
                    "1607391600": 0,
                    "1607391660": 0,
                    "1607391720": 0,
                    "1607391780": 0,
                    "1607391840": 0,
                    "1607391900": 0,
                    "1607391960": 0,
                    "1607392020": 0,
                    "1607392080": 0,
                    "1607392140": 0,
                },
                "model_id": 63,
            },
        ],
        "model": 32,
    },
}

FAKE_WEIGHT_RESPONSE = {
    "status": 0,
    "body": {
        "updatetime": 1608914981,
        "timezone": "Europe\/Zurich",
        "measuregrps": [
            {
                "grpid": 2366547394,
                "attrib": 8,
                "date": 1607580148,
                "created": 1607580186,
                "category": 1,
                "deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "hash_deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "measures": [
                    {"value": 5895, "type": 91, "unit": -3, "algo": 0, "fm": 3}
                ],
                "comment": None,
            },
            {
                "grpid": 2366547375,
                "attrib": 0,
                "date": 1607580148,
                "created": 1607580186,
                "category": 1,
                "deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "hash_deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "measures": [{"value": 84, "type": 11, "unit": 0, "algo": 0, "fm": 3}],
                "comment": None,
            },
            {
                "grpid": 2366547364,
                "attrib": 0,
                "date": 1607580148,
                "created": 1607580186,
                "category": 1,
                "deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "hash_deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "measures": [
                    {"value": 75880, "type": 1, "unit": -3, "algo": 3, "fm": 3},
                    {"value": 1207, "type": 8, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 6062, "type": 76, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 4434, "type": 77, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 317, "type": 88, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 15907, "type": 6, "unit": -3},
                    {"value": 63810, "type": 5, "unit": -3},
                ],
                "comment": None,
            },
            {
                "grpid": 2364739343,
                "attrib": 8,
                "date": 1607493827,
                "created": 1607493865,
                "category": 1,
                "deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "hash_deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "measures": [
                    {"value": 5953, "type": 91, "unit": -3, "algo": 0, "fm": 3}
                ],
                "comment": None,
            },
            {
                "grpid": 2364739328,
                "attrib": 0,
                "date": 1607493827,
                "created": 1607493865,
                "category": 1,
                "deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "hash_deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "measures": [{"value": 87, "type": 11, "unit": 0, "algo": 0, "fm": 3}],
                "comment": None,
            },
            {
                "grpid": 2364739318,
                "attrib": 0,
                "date": 1607493827,
                "created": 1607493864,
                "category": 1,
                "deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "hash_deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "measures": [
                    {"value": 75155, "type": 1, "unit": -3, "algo": 3, "fm": 3},
                    {"value": 1157, "type": 8, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 6040, "type": 76, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 4424, "type": 77, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 316, "type": 88, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 15395, "type": 6, "unit": -3},
                    {"value": 63585, "type": 5, "unit": -3},
                ],
                "comment": None,
            },
            {
                "grpid": 2362807719,
                "attrib": 0,
                "date": 1607407486,
                "created": 1607407517,
                "category": 1,
                "deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "hash_deviceid": "5e082fe27928d76863341de5cb19051695abb6e6",
                "measures": [
                    {"value": 75566, "type": 1, "unit": -3, "algo": 3, "fm": 3},
                    {"value": 1185, "type": 8, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 6053, "type": 76, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 4430, "type": 77, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 317, "type": 88, "unit": -2, "algo": 3, "fm": 3},
                    {"value": 15682, "type": 6, "unit": -3},
                    {"value": 63716, "type": 5, "unit": -3},
                ],
                "comment": None,
            },
        ],
    },
}


app = Flask(__name__)


def get_summary_response(response_to_return):
    startdateymd = request.form.get("startdateymd", type=str)
    enddateymd = request.form.get("enddateymd", type=str)
    data_fields = request.form.get("data_fields")

    if not all((startdateymd, enddateymd, data_fields)):
        print(startdateymd, enddateymd, data_fields)
        abort(400, "Invalid params")

    return app.response_class(
        response=json.dumps(response_to_return),
        status=200,
        mimetype="application/json",
    )


def get_raw_response(response_to_return):
    startdate = request.form.get("startdate", type=int)
    enddate = request.form.get("enddate", type=int)
    data_fields = request.form.get("data_fields")

    if not all((startdate, enddate, data_fields)):
        print(startdate, enddate, data_fields)
        abort(400, "Invalid params")

    return app.response_class(
        response=json.dumps(response_to_return),
        status=200,
        mimetype="application/json",
    )


@app.route("/measure", methods=["POST"])
def measurememnt_response():
    auth = request.headers.get("Authorization")
    if not auth == "Bearer faketoken":
        abort(400, "Authentication failed")

    action = request.form.get("action", type=str)
    if action == "getmeas":
        meastypes = request.form.getlist("meastypes")
        category = request.form.get("category", type=int)
        startdate = request.form.get("startdate", type=int)
        enddate = request.form.get("enddate", type=int)

        if not all((meastypes, category, startdate, enddate)):
            print(meastypes, category, startdate, enddate)
            abort(400, "Invalid params")

        response = app.response_class(
            response=json.dumps(FAKE_WEIGHT_RESPONSE),
            status=200,
            mimetype="application/json",
        )
    elif action == "getactivity":
        response = get_summary_response(FAKE_ACTIVITY_SUMMARY_RESPONSE)
    elif action == "getintradayactivity":
        response = get_raw_response(FAKE_ACTIVITY_RAW_RESPONSE)
    else:
        abort(400, "Unknown error")

    return response


@app.route("/sleep", methods=["POST"])
def sleep_response():
    auth = request.headers.get("Authorization")
    if not auth == "Bearer faketoken":
        abort(400, "Authentication failed")

    action = request.form.get("action", type=str)
    if action == "getsummary":
        response = get_summary_response(FAKE_SLEEP_SUMMARY_RESPONSE)
    elif action == "get":
        response = get_raw_response(FAKE_SLEEP_RAW_RESPONSE)
    else:
        abort(400)

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0")
