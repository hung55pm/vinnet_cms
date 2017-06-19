from django.core.serializers.json import Serializer as JsonSerializer
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.base import Serializer as BaseSerializer
from StringIO import StringIO
from django.core.serializers.json import Serializer
from .crypto import sign_md5
from urllib2 import urlopen, Request
import requests


def ptu_enc(ptuid):
    try:
        return "%08x" % ptuid
    except:
        return None


def ptu_dec(ptuid):
    try:
        return int(ptuid, 16)
    except:
        return 0


def strip_account(accountname):
    try:
        return accountname.split('@')[0]
    except:
        return None


def check_balance(msisdn):
    url = """http://css.vinnet.vn:12289/VinnetGWTEST/ws/restful/checkbalance?client_id=%s&phone_number=%s&sign=%s"""
    params = ['kiddycms', msisdn, 'MtApIUkvxplA62']
    params[-1] = sign_md5(params)
    try:
        resp = requests.get(url % tuple(params))
        return resp.json()
    except:
        return None


def check_warranty(ptuid):
    url="http://baohanh.vinnet.vn:8088/services/warranty.ashx?client_id=%s&imei=%s&sign=%s"
    params = ['kiddywatch.vn',ptuid,'(kiddywatch.vn)']
    params[-1] = sign_md5(params)
    try:
        resp = requests.get(url % tuple(params))
        return resp.json()
    except:
        return None

def check_map(ptuid, value, command):
    pass;