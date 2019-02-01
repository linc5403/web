import MySQLdb
import socket
from celery import Celery

from analysis.utils import get_key_and_url
from downloader.utils import select, safety_download, get_path_by_key
import logging


logger = logging.getLogger(__name__)

app = Celery('abc', broker='pyamqp://guest@localhost//')
download_dir = '/data/temp'

db = MySQLdb.connect(host='test2', user='linc', passwd='asdf1234', db='web')


@app.task
def add(x, y):
    return x + y


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
    SQL = select(table='analysis_download_task', **dict(id=task_id))
    count = c.execute(SQL)
    if count != 1:
        logger.error('cannot fetch the download task')
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
        key = get_key_and_url(url)[0],
        path = get_path_by_key(download_dir, key)
        c.execute(
            'update analysis_storage set status = {status}, host = {host}, file_path = {path} where `key` = {key}'.format(
                status=2,
                host=socket.gethostname(),
                file_path=path,
                key=key,
            ))
        db.commit()
