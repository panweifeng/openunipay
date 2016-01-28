from __future__ import absolute_import
from django.utils import timezone
from time import time
import datetime

def utc_now():
    return timezone.now()

def local_now():
    return timezone.localtime(utc_now())

def now_str():
    return local_now().strftime("%Y-%m-%d %H:%M:%S")

def get_timestamp():
    return int(time())

def get_unix_timestamp():
    return int((utc_now() - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds())
