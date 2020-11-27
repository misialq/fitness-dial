import datetime


class APIError(Exception):
    pass


def parse_dates(start_date, end_date):
    if not end_date:
        end_date = datetime.datetime.now()
    else:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(hour=11)

    if not start_date:
        start_date = end_date - datetime.timedelta(hours=24)
    else:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(hour=18)
    return start_date, end_date


def extract_and_parse_dates(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    start_date, end_date = parse_dates(start_date, end_date)
    return start_date, end_date
