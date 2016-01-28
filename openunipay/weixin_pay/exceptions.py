# -*- coding: utf-8 -*-
from rest_framework.exceptions import APIException

class APIError(APIException):
    status_code = 500
    default_detail = u'微信 API调用失败'