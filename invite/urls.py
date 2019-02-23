"""
urls

Created by lmarvaud on 31/10/2018
"""
from django.conf.urls import url

from .views import show_mail_html, show_mail_txt

urlpatterns = [
    url(r'^show_mail/event/(?P<event_id>[0-9]+)/family/(?P<family_id>[0-9]+).html$', show_mail_html,
        name="show_mail"),
    url(r'^show_mail/event/(?P<event_id>[0-9]+)/family/(?P<family_id>[0-9]+).txt', show_mail_txt),
]
