from __future__ import unicode_literals

from django.db import models
from django.conf import settings
import os
from time import strftime


def get_file_path(instance, filename):
    base_dir = os.path.join(settings.MEDIA_ROOT, strftime('%Y/%m/%d'))
    base_dir = os.path.join(base_dir, str(instance.uuid))
    file_path = os.path.join(base_dir, filename)
    return file_path


class Submission(models.Model):
    DM = 0
    SINGLE = 1
    NUMERIC = 2
    TYPES_CHOICES = (
        (DM, "decision-making"),
        (SINGLE, "single label"),
        (NUMERIC, "numeric"),
    )
    created_time = models.DateTimeField(auto_now_add=True)
    uuid = models.CharField(max_length=60)
    answer = models.FileField(upload_to=get_file_path, max_length=1024)
    truth = models.FileField(upload_to=get_file_path, max_length=1024)
    generated_k_folder = models.BooleanField(default=False)
    kfold = models.IntegerField(null=True)
    type = models.SmallIntegerField(choices=TYPES_CHOICES, default=DM)
    redundancy = models.TextField(null=True)
    quality = models.TextField(null=True)


class Method(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    # bit to store different types. e.g 5 = 0b101 = 1 << NUMERIC |  1 << DM; 4 = 0b100 = 1 << NUMERIC
    type = models.SmallIntegerField()


class Execution(models.Model):
    RUNNING = 0
    DONE = 1
    STATUS_CHOICES = (
        (RUNNING, 'running'),
        (DONE, 'complete'),
    )
    submission = models.ForeignKey(Submission)
    method = models.ForeignKey(Method)
    result = models.TextField(null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, null=True)
