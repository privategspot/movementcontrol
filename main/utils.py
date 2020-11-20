from django.http.request import QueryDict


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
