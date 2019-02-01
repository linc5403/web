# from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from analysis.models import STORAGE, DOWNLOAD_TASK
from analysis.utils import get_key_and_url, my_response

from downloader.tasks import download

import logging

logger = logging.getLogger(__name__)


def test(request):
    logger.info('{}'.format(request))
    return my_response(desc='this is for test')


@csrf_exempt
def analysis(request):
    if request.method == 'POST':
        post = request.POST
        params = request.GET
        logger.info('post {}'.format(post.keys()))
        logger.info('get {}'.format(params))
        url = params.get('url')
        logger.info('url = {}'.format(url))
        return my_response(
            desc='thi is a POST test, and your post data are {}, post params are {}'.format(
                post, params)
        )
    elif request.method == 'GET':
        return my_response(desc='this is a get test')


@csrf_exempt
def update_local_to_server(request):
    if request.method == 'POST':
        data = request.POST
        logger.info('post is {}'.format(data))
        key = data['key']
        host = data['host']
        file_path = data['file_path']
        cat = data.get('cat', None)
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
            return my_response(code=1, desc='already in lib', data_dict=dict(
                host=s.host,
                path=s.file_path
            ))
        return my_response(code=0, desc='update sucess')


"""
class DOWNLOAD_TASK(models.Model):
    INIT = 0
    DOWNLODING = 1
    FAILED = 2
    FINISHED = 3
    url = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, default=None)
    status = models.SmallIntegerField(default=INIT)
"""


@csrf_exempt
def request_download(request):
    if request.method == 'POST':
        data = request.POST
        logger.info('receive download task: {}'.format(data))
        url = data['url']
        key, url = get_key_and_url(url)
        try:
            item = STORAGE.objects.get(key=key)
        except STORAGE.DoesNotExist:
            # start download_task
            new_item = STORAGE.objects.create(
                key=key,
                status=STORAGE.INIT,
            )
            downloader = DOWNLOAD_TASK.objects.create(
                url=url,
                status=DOWNLOAD_TASK.INIT
            )
            download.delay(task_id=downloader.id)
            new_item.download_task = downloader
            new_item.status = STORAGE.TASK_SEND
            new_item.save()
            return my_response(code=0, desc='new task added')
        else:
            # already in lib
            logger.info(
                'duplicated download request {}'.format(dict(
                    url=url, host=item.host, path=item.file_path)
                )
            )
            return my_response(code=1, desc='has_in', data_dict=dict(
                host=item.host,
                path=item.file_path,
                desc='request already exist'
            ))
    else:
        return my_response(code=-1, desc='only support POST')
