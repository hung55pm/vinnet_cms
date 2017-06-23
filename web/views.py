# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView,ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import *
from .utils import ptu_dec, ptu_enc,\
    strip_account, check_balance, check_warranty, check_map
from django.conf import settings
import re, logging
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import dateparse, timezone

logger = logging.getLogger('django')

# Create your views here.


class HomeView(LoginRequiredMixin, TemplateView):
    #permission_required = 'web.can_view'
    template_name = 'web/home.html'


class AccountView(LoginRequiredMixin, TemplateView):
    #permission_required = 'web.can_view'
    template_name = 'web/account/acc_list.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        (skip, take) = (int(request.POST.get(x, '0')) for x in ('skip', 'take'))
        account = request.POST.get('filter[filters][0][account]', None)
        query = GlobalAccount.objects.order_by('-createtime')
        if account:
            query = query.filter(mobile=account.strip())
        data = {
            "total": query.count(),
            "data": [{
                "accountname": x.accountname,
                "mobile": x.mobile,
                "createtime": x.createtime,
                "lastlogintime": x.lastlogintime,
                "devices": list(  {"ptuid":ptu_enc(y['watch__ptuid']),"type":y['type']} for y in x.Wars.all().values('watch__ptuid','type'))
            } for x in query[skip:skip+take]]
        }
        return JsonResponse(data)


class AccountDetailView(LoginRequiredMixin, TemplateView):
    #permission_required = 'web.can_view'
    template_name = 'web/account/detail.html'

    def get(self, request, msisdn):
        account = None
        try:
            account = GlobalAccount.objects.get(mobile=msisdn)
        except:
            account = None
        return render(request, self.template_name, context={'account': account})


class AccountDevicesView(LoginRequiredMixin, TemplateView):
    def post(self, request, msisdn):
        query = WatchAccountRelation.objects.filter(account__mobile=msisdn).order_by("type")
        data = [{
            "type": x.type,
            "ptuid": ptu_enc(x.watch_id),
            "createtime": x.createtime
        } for x in query]
        return JsonResponse(data, safe=False)


class DeviceView(LoginRequiredMixin, TemplateView):
    #permission_required = 'web.can_view'
    template_name = 'web/device/dev_list.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        (skip, take) = (int(request.POST.get(x, '0')) for x in ('skip', 'take'))
        ptuid = request.POST.get('filter[filters][0][ptuid]', None)
        imei = request.POST.get('filter[filters][0][imei]', None)
        msisdn = request.POST.get('filter[filters][0][msisdn]', None)
        account = request.POST.get('filter[filters][0][account]', None)
        query = GlobalWatch.objects.order_by('producetime')
        if ptuid:
            int_ptuid = ptu_dec(ptuid)
            query = query.filter(ptuid=int_ptuid)
        if imei:
            query = query.filter(imei=imei.strip())
        if msisdn:
            query = query.filter(cdma_tid=msisdn.strip())
        if account:
            query = query.filter(Wars__account__mobile=account.strip())
        print query.query
        data = {
            "total":query.count(),
            "data": [{
                "ptuid": ptu_enc(x.ptuid),
                "akey": ptu_enc(x.akey),
                "imei": x.imei,
                "cdma_tid": x.cdma_tid,
                "firstactivetime": x.firstactivetime,
                "lastuptime": x.lastuptime,
                "producetime": x.producetime,
                "color": x.watchproduct.color if hasattr(x, 'watchproduct') else '',
                "po": x.watchproduct.po if hasattr(x, 'watchproduct') else '',
                "accounts": list(x.Wars.all().values('account__objectid','account__mobile','type'))
            } for x in query[skip:skip+take]]
        }
        return JsonResponse(data)


class DeviceDetailView(LoginRequiredMixin, TemplateView):
    #permission_required = 'web.can_view'
    template_name = 'web/device/detail.html'

    def get(self, request, ptuid):
        int_ptuid = ptu_dec(ptuid)
        if int_ptuid:
            device = None
            try:
                device = GlobalWatch.objects.get(ptuid=int_ptuid)
            except:
                pass
            return render(request, self.template_name, context={'device': device})

        return HttpResponseBadRequest("Bad request")


class DeviceAccountsView(LoginRequiredMixin, TemplateView):
    def post(self, request, ptuid):
        int_ptuid = ptu_dec(ptuid)
        query = WatchAccountRelation.objects.filter(watch_id=int_ptuid).order_by("type")
        data = [{
            "type": x.type,
            "mobile": x.account.mobile,
            "createtime": x.createtime
        } for x in query]
        return JsonResponse(data, safe=False)


class UnbindHistoryView(LoginRequiredMixin, TemplateView):

    def post(self, request, ptuid):
        (skip, take) = (int(request.POST.get(x, '0')) for x in ('skip', 'take'))
        int_ptuid = ptu_dec(ptuid)
        query1 = UnbindHistory.objects.filter(ptuid = int_ptuid).order_by('-createtime')
        query2 = query1[skip:skip+take]
        data = {
            "total": query1.count(),
            "data": [{
                "accountname": strip_account(x.accountname),
                "ptuid": ptu_enc(x.ptuid),
                "createtime": x.createtime
            } for x in query2]
        }
        return JsonResponse(data)


class SubChargingView(LoginRequiredMixin, TemplateView):
    def post(self, request, msisdn):
        phone_pattern = getattr(settings, 'PHONE_RE')
        data = {}
        if re.match(phone_pattern, msisdn):
            (skip, take) = (int(request.POST.get(x, '0')) for x in ('skip', 'take'))
            query1 = FeeCharge.objects.filter(phone_number=msisdn).order_by('-begin_charge')
            query2 = query1[skip:skip+take]
            data = {
                "total": query1.count(),
                "data" : [{
                    "msisdn": x.phone_number,
                    "begin_charge": x.begin_charge,
                    "description": x.description
                } for x in query2]
            }
        return JsonResponse(data)


class SubSMSView(LoginRequiredMixin, TemplateView):
    def post(self, request, msisdn):
        phone_pattern = getattr(settings, 'PHONE_RE')
        data = {}
        if re.match(phone_pattern, msisdn):
            (skip, take) = (int(request.POST.get(x, '0')) for x in ('skip', 'take'))
            query1 = SmsSendLog.objects.filter(receiver_number=msisdn).order_by('-gen_date')
            query2 = query1[skip:skip+take]
            data = {
                "total": query1.count(),
                "data" : [{
                    "msisdn": x.receiver_number,
                    "gen_date": x.gen_date,
                    "content": x.content,
                    "code": x.code,
                    "message": x.message
                } for x in query2]
            }
        return JsonResponse(data)


class SubTopupView(LoginRequiredMixin, TemplateView):
    def post(self, request, msisdn):
        phone_pattern = getattr(settings, 'PHONE_RE')
        data = {}
        if re.match(phone_pattern, msisdn):
            (skip, take) = (int(request.POST.get(x, '0')) for x in ('skip', 'take'))
            query1 = Topup.objects.filter(phone_number=msisdn).order_by('-gen_date')
            query2 = query1[skip:skip+take]
            data = {
                "total": query1.count(),
                "data" : [{
                    "msisdn": x.phone_number,
                    "gen_date": x.gen_date,
                    "from_account": x.from_account,
                    "card_value": x.card_value,
                    "status": x.status,
                    "description": x.description
                } for x in query2]
            }
        return JsonResponse(data)


class SubCheckBalanceView(LoginRequiredMixin, TemplateView):
    template_name = "web/subscriber/check_balance.html"


class ToolsView(LoginRequiredMixin, TemplateView):
    template_name = "web/tools/tools.html"


class ToolsActionView(LoginRequiredMixin, TemplateView):

    def post(self, request, action):
        if action=='check-balance':
            phone = request.POST.get('phone', '').strip()
            phone_re = getattr(settings, 'PHONE_RE')
            if phone and re.match(phone_re, phone):
                object = check_balance(phone)
                logger.info('CHECK BALANCE RESULT: %s', object)
                return render(request, 'web/tools/check_balance.html', context={'object': object})
        elif action=='check-warranty':
            imei=request.POST.get('imei','').strip()
            imei_re = getattr(settings, 'IMEI_RE')
            if imei and re.match(imei_re, imei):
                object = check_warranty(imei)
                logger.info('CHECK WARRANTY RESULT: %s', object)
                return render(request, 'web/tools/check_warranty.html', context={'object': object})
        elif action=='check-map':
            ptuid = request.POST.get('ptuid', '').strip()
            value = request.POST.get('value','').strip()
            command = request.POST.get('command').strip()
            ptuid_re = getattr(settings, "PTUID_RE")
            if ptuid and re.match(ptuid_re, ptuid):
                object = check_map(ptuid,value, command)
                logger.info('CHECK MAP RESULT: %s', object)
                return render(request, 'web/tools/check_map.html', context={'object': object})
        return HttpResponseBadRequest()


class LogChargingView(LoginRequiredMixin, TemplateView):
    template_name = 'web/log/charging.html'

    def post(self, request):
        (skip, take,) = (int(request.POST.get(x,'0')) for x in ('skip', 'take'))
        msisdn = request.POST.get('filter[filters][0][msisdn]', None)
        fr = request.POST.get('filter[filters][0][fr]', None)
        to = request.POST.get('filter[filters][0][to]', None)
        desc = request.POST.get('filter[filters][0][desc]', None)

        query = FeeCharge.objects.order_by('-begin_charge')
        if msisdn:
            query = query.filter(phone_number=msisdn)
        if desc:
            query = query.filter(description=desc)
        if fr:
            query = query.filter(begin_charge__gt=fr)
        if to:
            query = query.filter(begin_charge__lt=to)
        data = {
            "total": query.count(),
            "data": [{
                "phone_number": x.phone_number,
                "begin_charge": x.begin_charge,
                "description": x.description
            } for x in query[skip:skip+take]]
        }
        return JsonResponse(data)


class LogPositionView(LoginRequiredMixin, TemplateView):
    template_name = 'web/log/position.html'

    def post(self, request):
        (skip, take,) = (int(request.POST.get(x, '0')) for x in ('skip', 'take'))
        ptuid = request.POST.get('filter[filters][0][ptuid]', None)
        loc_date = request.POST.get('filter[filters][0][loc_date]', None)
        if loc_date:
            # parse from string to datetime
            loc_date = dateparse.parse_datetime(loc_date)
            # and convert to current timezone
            loc_date = timezone.localtime(loc_date, timezone.get_current_timezone())
        else:
            loc_date = datetime.datetime.now()

        WatchPosition = create_position_log_model(loc_date)
        query = WatchPosition.objects.all()
        print query.query
        if ptuid:
            query = query.filter(ptuid = ptu_dec(ptuid))
        data = {}
        try:
            data = {
                "total": query.count(),
                "data": [{
                    "ptuid": ptu_enc(x.ptuid),
                    "lat": x.final_lat,
                    "long": x.final_log,
                    "from": (x.final_from & 0xf),
                    "radius": x.final_range,
                    "uptime": x.uptime,
                    "bat": x.bat,
                    "mi1": x.mi1
                 } for x in query[skip:skip + take]]
            }
        except Exception as e:
            logger.error('query error: %s', e)

        return JsonResponse(data)



class LogTopupView(LoginRequiredMixin, TemplateView):
    template_name = 'web/log/topup.html'

class LogRecordingView(LoginRequiredMixin, TemplateView):
    template_name = 'web/log/recording.html'


    def post(self, request):
        (skip, take,) = (int(request.POST.get(x, '0')) for x in ('skip', 'take'))
        ptuid = request.POST.get('filter[filters][0][ptuid]', None)
        loc_date = request.POST.get('filter[filters][0][loc_date]', None)
        if loc_date:
            # parse from string to datetime
            loc_date = dateparse.parse_datetime(loc_date)
            # and convert to current timezone
            loc_date = timezone.localtime(loc_date, timezone.get_current_timezone())
        else:
            loc_date = datetime.datetime.now()
        WatchSound = create_recording_log_model(loc_date)
        query = WatchSound.objects.filter(uptime__date=loc_date.date())

        if ptuid:
            query = query.filter(ptuid=ptu_dec(ptuid))
        print query.query
        data = {}
        try:
            data = {
                "total": query.count(),
                "data": [{
                    "ptuid": ptu_enc(x.ptuid),
                    "uptime": x.uptime,
                    "reason": x.reason,
                    "user_cmd": x.user_cmd,
                    "rec_tot": x.rec_tot,
                    "rec_ts": x.rec_ts,
                } for x in query[skip:skip + take]]
            }
        except Exception as e:
            logger.error('query error: %s', e)

        return JsonResponse(data)

class LogAcountMessageView(LoginRequiredMixin, TemplateView):
    template_name = 'web/log/acount_message.html'


    def post(self, request):
        (skip, take,) = (int(request.POST.get(x, '0')) for x in ('skip', 'take'))
        mobile = request.POST.get('filter[filters][0][mobile]', None)
        loc_date = request.POST.get('filter[filters][0][loc_date]', None)
        if loc_date:
            # parse from string to datetime
            loc_date = dateparse.parse_datetime(loc_date)
            # and convert to current timezone
            loc_date = timezone.localtime(loc_date, timezone.get_current_timezone())
        else:
            loc_date = datetime.datetime.now()
        AcountMessage = create_acount_message_log_model(loc_date)
        query = AcountMessage.objects.filter(uptime__date=loc_date.date())
        if mobile:
            query = query.filter(mobile=mobile)

        print query.query
        #print query.count()
        data = {}
        try:
            data = {
                "total": query.count(),
                "data": [{
                    "mobile": x.mobile,
                    "uptime": x.uptime,
                    "type": x.type,
                } for x in query[skip:skip + take]]
            }
        except Exception as e:
            logger.error('query error: %s', e)

        return JsonResponse(data)


class LogDeviceMessageView(LoginRequiredMixin, TemplateView):
    template_name = 'web/log/device_message.html'

    def post(self, request):
        (skip, take,) = (int(request.POST.get(x, '0')) for x in ('skip', 'take'))
        ptuid = request.POST.get('filter[filters][0][ptuid]', None)
        loc_date = request.POST.get('filter[filters][0][loc_date]', None)
        if loc_date:
            # parse from string to datetime
            loc_date = dateparse.parse_datetime(loc_date)
            # and convert to current timezone
            loc_date = timezone.localtime(loc_date, timezone.get_current_timezone())
        else:
            loc_date = datetime.datetime.now()
        DeviceMessage = create_device_message_log_model(loc_date)
        query = DeviceMessage.objects.filter(uptime__date=loc_date.date())
        if ptuid:
            query = query.filter(ptuid=ptu_dec(ptuid))
        print query.query
        data = {}
        try:
            data = {
                "total": query.count(),
                "data": [{
                    "ptuid": ptu_enc(x.ptuid),
                    "mobile": x.cdma_tid,
                    "content": x.sms_uid,
                    "uptime": x.uptime,
                } for x in query[skip:skip + take]]
            }
        except Exception as e:
            logger.error('query error: %s', e)

        return JsonResponse(data)