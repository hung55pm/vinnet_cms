"""vinnet_cms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from .views import *

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='index'),
    url(r'^account/$', AccountView.as_view(), name='account'),

    url(r'^account/(?P<msisdn>((09|08)[0-9]{8})|(01[0-9]{9}))$', AccountDetailView.as_view(), name='account_detail'),
    url(r'^account/(?P<msisdn>((09|08)[0-9]{8})|(01[0-9]{9}))/devices$', AccountDevicesView.as_view(), name='account_devices'),

    url(r'^device/(?P<ptuid>[a-f0-9]{8})$', DeviceDetailView.as_view(), name='device_detail'),
    url(r'^device/(?P<ptuid>[a-f0-9]{8})/accounts$', DeviceAccountsView.as_view(), name='device_accounts'),
    url(r'^device/(?P<ptuid>[a-f0-9]{8})/unbind_history', UnbindHistoryView.as_view(), name='device_unbind_history'),
    url(r'^device/$', DeviceView.as_view(), name='device'),

    # url(r'^sub/(?P<msisdn>((09|08)[0-9]{8})|(01[0-9]{9}))/charging$', SubChargingView.as_view(), name='sub_charging'),
    # url(r'^sub/(?P<msisdn>((09|08)[0-9]{8})|(01[0-9]{9}))/sms$', SubSMSView.as_view(), name='sub_sms'),
    url(r'^sub/check-balance$', SubCheckBalanceView.as_view(), name='sub_check_balance'),
    url(r'^sub/(?P<msisdn>\d+)/charging$', SubChargingView.as_view(), name='sub_charging'),
    url(r'^sub/(?P<msisdn>\d+)/sms$', SubSMSView.as_view(), name='sub_sms'),
    url(r'^sub/(?P<msisdn>\d+)/topup$', SubTopupView.as_view(), name='sub_topup'),

    url(r'^tools$', ToolsView.as_view(), name="tools"),
    url(r'^tools/(?P<action>[\w-]+)/$', ToolsActionView.as_view(), name="tool_action"),

    url('^log/charging$', LogChargingView.as_view(), name='log_charging'),
    url('^log/position$', LogPositionView.as_view(), name='log_position'),
    url('^log/acount_message', LogAcountMessageView.as_view(), name='log_acount_message'),
    url('^log/device_message', LogDeviceMessageView.as_view(), name='log_device_message'),
    url('^log/recording', LogRecordingView.as_view(), name='log_recording')
]
