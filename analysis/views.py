# from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from analysis.models import STORAGE

import logging

logger = logging.getLogger(__name__)


def test(request):
    logger.info('{}'.format(request))
    return HttpResponse(content=b'abcd')


@csrf_exempt
def analysis(request):
    if request.method == 'POST':
        post = request.POST
        params = request.GET
        logger.info('post {}'.format(post.keys()))
        logger.info('get {}'.format(params))
        url = params.get('url')
        logger.info('url = {}'.format(url))
        return HttpResponse(content=b'url received')
    elif request.method == 'GET':
        return HttpResponse(content=b'this is a get')


@csrf_exempt
def update_local_to_server(request):
    if request.method == 'POST':
        data = request.POST
        logger.info('post is {}'.format(data))
        key = data['key']
        host = data['host']
        file_path = data['file_path']
        cat = data['cat']
        s, created = STORAGE.objects.get_or_create(
            defaults=dict(
                cat=cat,
                file_path=file_path,
                status=STORAGE.IN_LIB,
                host=host,
            ),
            key=key
        )
        if not created:
            logger.error('video has in lib, {}: {}'.format(
                s.host, s.file_path
            ))
        return HttpResponse(content=b'ok')
