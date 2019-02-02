import MySQLdb
import socket
from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger

from analysis.utils import get_key_and_url
from downloader.utils import safety_download, get_path_by_key
import logging

download_dir = '/data/temp'

db = MySQLdb.connect(host='test2', user='linc', passwd='asdf1234', db='web', charset='utf8mb4')

logger = logging.getLogger('root')

app = Celery('abc', broker='pyamqp://guest@localhost//')
app.conf.timezone = 'Asia/Shanghai'
app.conf.beat_schedule = {
    'retry every 3 hours': {
        'task': 'downloader.tasks.retry_failed_download',
        'schedule': crontab(minute=0, hour='*/3'),
    },
}


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter(
        '%(levelname)s %(asctime)s %(module)s %(message)s [' + socket.gethostname() + ']'
    )
    # SysLogHandler
    slh = logging.handlers.SysLogHandler(address=('172.16.11.4', 514))
    slh.setFormatter(formatter)
    slh.setLevel(logging.INFO)
    logger.addHandler(slh)
    # printHandler
    plh = logging.StreamHandler()
    plh.setFormatter(formatter)
    plh.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(plh)


@app.task
def add(x, y):
    logger.info('****************receive task***************')
    return x + y


@app.task
def retry_failed_download():
    c = db.cursor()
    SQL = 'select `id` from analysis_download_task where status = 3'
    c.execute(SQL)
    for item in c.fetchall():
        download.delay(item[0])
        print('send task {}'.format(item[0]))


"""
+-------------+-------------+------+-----+---------+----------------+
| Field       | Type        | Null | Key | Default | Extra          |
+-------------+-------------+------+-----+---------+----------------+
| id          | int(11)     | NO   | PRI | NULL    | auto_increment |
| url         | longtext    | NO   |     | NULL    |                |
| started_at  | datetime(6) | NO   |     | NULL    |                |
| finished_at | datetime(6) | YES  |     | NULL    |                |
| status      | smallint(6) | NO   |     | NULL    |                |
+-------------+-------------+------+-----+---------+----------------+
"""


@app.task
def download(task_id):
    c = db.cursor()
    SQL = 'select `id`, url from analysis_download_task where `id` = {id} and status = 3'.format(
        id=task_id)
    count = c.execute(SQL)
    if count != 1:
        logger.error('cannot fetch the download task {}'.format(task_id))
        return
    task = c.fetchone()
    url = task[1]
    c.execute('update analysis_download_task set status = 1 where `id` = {}'.format(task_id))
    db.commit()
    ret = safety_download(url, download_dir)
    if ret != 0:
        c.execute('update analysis_download_task set status = 3 where `id` = {}'.format(task_id))
        db.commit()
    else:
        c.execute('update analysis_download_task set status = 2 where `id` = {}'.format(task_id))
        db.commit()
        # 找到storage更新状态
        key = get_key_and_url(url)[0]
        try:
            path = get_path_by_key(download_dir, key)
        except Exception as e:
            logger.error('key is {} e is {}'.format(key, e))
            return
        SQL = 'update analysis_storage set status = {status}, host = "{host}", file_path = "{path}" where `key` = "{key}"'.format(
            status=2,
            host=socket.gethostname(),
            path=path,
            key=key,
        )
        c.execute(SQL)
        db.commit()


def fix_finished_record():
    c = db.cursor()
    c.execute('select `key` from analysis_storage t1 INNER JOIN analysis_download_task t2 on t1.download_task_id = t2.id where t2.status = 2 and t1.status = 1')
    for x in c.fetchall():
        path = get_path_by_key(download_dir, x[0])
        SQL = 'update analysis_storage set status = {status}, host = "{host}", file_path = "{path}" where `key` = "{key}"'.format(
            status=2,
            host=socket.gethostname(),
            path=path,
            key=x[0],
        )
        c.execute(SQL)
        db.commit()
