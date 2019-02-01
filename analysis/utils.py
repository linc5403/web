#   https://openload.co/f/wTUMkpPSRVY
from django.http import JsonResponse
import urllib
import os


def get_key_and_url(url):
    url = url.split()[0]
    path = urllib.parse.urlsplit(url).path
    if path[-4:] == '.mp4':
        new_path = os.path.split(path)[0]
        key = new_path[-11:]
    else:
        key = url[-11:]
    return key, url


def my_response(code=0, desc='', data_dict=dict()):
    ret = dict(
        code=code,
        desc=desc,
    )
    ret.update(data_dict)
    return JsonResponse(data=ret)
