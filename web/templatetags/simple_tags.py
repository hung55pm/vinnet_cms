from datetime import datetime, timedelta
from django import template
from django.http import HttpRequest
from django.conf import settings
from django.utils.translation import to_locale, get_language

register = template.Library()

LOCALES = {
    'en': {
        'locale': 'en-US',
        'long_date_fmt': 'MM/dd/yyyy HH:mm:ss'
    },
    'vi': {
        'locale': 'vi-VN',
        'long_date_fmt': 'dd/MM/yyyy HH:mm:ss'
    }
}

# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.simple_tag
def get_current_culture():
    return  LOCALES[get_language()]['locale']

@register.simple_tag
def get_long_date_fmt():
    return LOCALES[get_language()]['long_date_fmt']
