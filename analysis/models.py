from django.db import models

# Create your models here.


class STORAGE(models.Model):
    INIT = 0
    DOWNLOADING = 1
    IN_LIB = 2
    key = models.CharField(max_length=64, db_index=True, null=False, blank=False)
    file_path = models.TextField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(default=INIT)
    host = models.CharField(max_length=64, null=True, blank=True, default=None)
    cat = models.CharField(max_length=64, null=True, blank=True, default=None)
    download_task = models.ForeignKey('DOWNLOAD_TASK', on_delete=models.SET_NULL, null=True, default=None)


class DOWNLOAD_TASK(models.Model):
    INIT = 0
    DOWNLODING = 1
    FAILED = 2
    FINISHED = 3
    url = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, default=None)
    status = models.SmallIntegerField(default=INIT)
