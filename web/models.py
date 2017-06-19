# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.base import ModelBase
import datetime

# Create your models here.


class GlobalAccount(models.Model):
    objectid = models.BigAutoField(primary_key=True)
    accountname = models.CharField(max_length=50)
    phoneversion = models.CharField(max_length=50, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    lastlogintime = models.DateTimeField(blank=True, null=True)
    resettimes = models.SmallIntegerField(blank=True, null=True)
    createtime = models.DateTimeField(blank=True, null=True)
    modifytime = models.DateTimeField(blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    api_key = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'global_account'


class GlobalWatch(models.Model):
    ptuid = models.IntegerField(primary_key=True)
    io_options = models.IntegerField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    sn = models.IntegerField(blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, null=True)
    firstactivetime = models.DateTimeField(blank=True, null=True)
    producetime = models.DateTimeField(blank=True, null=True)
    akey = models.IntegerField(blank=True, null=True)
    imei = models.CharField(max_length=15, blank=True, null=True, unique=True)
    iccid = models.CharField(max_length=20, blank=True, null=True)
    imsi = models.CharField(max_length=15, blank=True, null=True)
    term_id = models.CharField(max_length=50, blank=True, null=True)
    qr = models.CharField(max_length=50, blank=True, null=True)
    alias = models.CharField(max_length=20, blank=True, null=True)
    tel = models.CharField(max_length=13, blank=True, null=True)
    smac = models.CharField(max_length=6, blank=True, null=True)
    mcc = models.SmallIntegerField(blank=True, null=True)
    mnc = models.IntegerField(blank=True, null=True)
    cdma_tid = models.CharField(max_length=20, blank=True, null=True)
    uimid = models.CharField(max_length=8, blank=True, null=True)
    esn = models.IntegerField(blank=True, null=True)
    meid = models.CharField(max_length=14, blank=True, null=True)
    linkstate = models.IntegerField(blank=True, null=True)
    soundstate = models.IntegerField(blank=True, null=True)
    messagestate = models.IntegerField(blank=True, null=True)
    positionstate = models.IntegerField(blank=True, null=True)
    sosstate = models.IntegerField(blank=True, null=True)
    dotstate = models.IntegerField(blank=True, null=True)
    lastuptime = models.DateTimeField(blank=True, null=True)
    province = models.CharField(max_length=16, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    lastposition = models.CharField(max_length=200, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    modifytime = models.DateTimeField(blank=True, null=True)

    @property
    def hex_ptuid(self):
        return '%8x' % self.ptuid

    @property
    def hex_akey(self):
        return '%8x' % self.akey

    class Meta:
        managed = False
        db_table = 'global_watch'


class WatchProduct(models.Model):
    watch = models.OneToOneField(GlobalWatch,to_field='imei', db_column='imei')
    color = models.CharField(max_length=20)
    po = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = '`cms_product_db`.`watch_product`'

class WatchAccountRelation(models.Model):
    objectid = models.BigAutoField(primary_key=True)
    watch = models.ForeignKey(GlobalWatch, related_name='Wars',db_column='ptuid')
    account = models.ForeignKey(GlobalAccount, related_name='Wars',db_column='accountid')
    type = models.IntegerField(blank=True, null=True)
    flag = models.IntegerField(blank=True, null=True)
    createtime = models.DateTimeField(blank=True, null=True)
    babyname = models.CharField(max_length=50, blank=True, null=True)
    babybirthday = models.DateField(blank=True, null=True)
    babysex = models.IntegerField(blank=True, null=True)
    babygrade = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'watch_account_relation'

class UnbindHistory(models.Model):
    objectid = models.BigAutoField(primary_key=True)
    ptuid = models.IntegerField()
    accountname = models.CharField(max_length=50)
    createtime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'unbind_history'

class FeeCharge(models.Model):
    phone_number = models.CharField(max_length=20)
    begin_charge = models.DateTimeField()
    description = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = '`vinnetgw`.`fee_charge`'


class Topup(models.Model):
    phone_number = models.CharField(max_length=20)
    from_account = models.CharField(max_length=20)
    card_value = models.IntegerField()
    gen_date = models.DateTimeField()
    status = models.IntegerField()
    description = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = '`vinnetgw`.`topup_trans`'


class SmsSendLog(models.Model):
    receiver_number = models.CharField(max_length=20)
    gen_date = models.DateTimeField()
    content = models.CharField(max_length=350)
    code = models.IntegerField()
    message = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = '`vinnetgw`.`sms_send_log`'


def create_position_log_model(for_date):

    class CustomMetaClass(ModelBase):
        def __new__(cls, name, bases, attrs):
            table_name = '`cms_watch_position_db`.`watch_position_%s`'
            if isinstance(for_date, datetime.date):
                table_name = table_name % for_date.strftime('%Y_%m_%d')
            else:
                table_name = table_name % for_date
            model = super(CustomMetaClass, cls).__new__(cls, name, bases, attrs)
            model._meta.db_table = table_name
            return model

    class WatchPosition(models.Model):

        __metaclass__ = CustomMetaClass
        # define your fileds here
        objectid = models.BigAutoField(primary_key=True)
        ptuid = models.IntegerField()
        final_lat = models.FloatField()
        final_log = models.FloatField()
        final_from = models.IntegerField()
        final_range = models.IntegerField()
        uptime = models.DateTimeField()
        bat = models.IntegerField()
        mi1 = models.IntegerField()

    return WatchPosition
