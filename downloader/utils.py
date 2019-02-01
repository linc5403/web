import os
import logging
import time
import threading
import subprocess
from queue import Queue, Empty

logger = logging.getLogger(__name__)


def select(table, **kwargs):
    SQL = 'SELECT * FROM {table}'.format(table=table)
    limit = kwargs.pop('limit', None)
    order = kwargs.pop('order', None)
    for k, v in kwargs.items():
        if len(kwargs) == 1:
            SQL += ' WHERE {} = {}'.format(k, v)
        else:
            SQL += ' AND WHERE {} = {}'.format(k, v)
    if order:
        if order == 'id':
            SQL += ' ORDER BY `id`'
        else:
            SQL += ' ORDER BY {}'.format(order)
    if limit:
        SQL += ' LIMIT {}'.format(limit)
    return SQL


def output_reader(proc, q):
    for line in iter(proc.stdout.readline, b''):
        logger.debug(line)
        if (b'ERROR: giving up after 100 retries' in line):
            logger.error(line)
            q.put('stop')
            return


def safety_download(url, path):
    """
    Returns:
        0: success
        other: ffmpeg exit abnormally
    """
    # -R, --retries RETRIES            Number of retries (default is 10), or "infinite".
    command = ['youtube-dl', '-R', '100', url]
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=path)

    queue = Queue()
    t = threading.Thread(target=output_reader, args=(proc, queue))
    t.daemon = True
    t.start()
    status = 0
    duration = 0
    while True:
        time.sleep(1)
        try:
            queue.get(block=False)
        except Empty:
            pass
        else:
            logger.error('youtube-dl {} retries failed '.format(url))
            status = 1
            break
        a = proc.poll()
        if a is None:
            continue
        elif a != 0:
            logger.error('youtube-dl {} exit with code {}'.format(url, a))
            status = a
            break
        else:
            logger.info('exit normally')
            break
        duration += 1
    if status != 0:
        proc.terminate()
        proc.wait()
    else:
        logger.info('youtube-dl download {} sucess.'.format(url))
    return status


def get_path_by_key(path, key):
    for i, j, k in os.walk(path):
        for _ in k:
            if key in _:
                return os.path.join(i, _)
    return None
