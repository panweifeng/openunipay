from __future__ import absolute_import
from time import time
import datetime

def utc_now():
    return datetime.datetime.utcnow()

def local_now():
    return datetime.datetime.now()

def now_str():
    return local_now().strftime("%Y-%m-%d %H:%M:%S")

def get_timestamp():
    return int(time())

def get_unix_timestamp():
    return int((utc_now() - datetime.datetime(1970, 1, 1, tzinfo=None)).total_seconds())
