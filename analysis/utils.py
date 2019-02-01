#   https://openload.co/f/wTUMkpPSRVY
from django.http import JsonResponse


def get_key_and_url(url):
    url = url.split()[0]
    return url[-11:], url


def my_response(code=0, desc='', data_dict=dict()):
    ret = dict(
        code=code,
        desc=desc,
    )
    ret.update(data_dict)
    return JsonResponse(data=ret)
