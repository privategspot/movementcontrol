import pytz
from django.http.request import QueryDict
from django.conf import settings


def get_paginator_baseurl(request):
    query = ""
    cur_get = request.GET.copy()
    cur_get_len = len(cur_get.dict())
    if not cur_get:
        query = "?page="
    elif cur_get_len == 1 and "page" in cur_get:
        query = "?page="
    elif cur_get_len > 1 and "page" in cur_get:
        cur_get.pop("page")
        cur_get = QueryDict(cur_get.urlencode())
        query = "?" + cur_get.urlencode() + "&page="
    elif cur_get_len >= 1:
        cur_get = QueryDict(cur_get.urlencode())
        query = "?" + cur_get.urlencode() + "&page="
    return request.path + query


def datetime_to_current_tz(datetime):
    settings_tz = pytz.timezone(settings.TIME_ZONE)
    return datetime.astimezone(settings_tz)
