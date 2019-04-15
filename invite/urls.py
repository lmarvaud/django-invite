"""
urls

Created by lmarvaud on 31/10/2018
"""
from django.conf.urls import url

from .views import show_mail_html, show_mail_txt, get_joined_document

urlpatterns = [
    url(r'^show_mail/event/(?P<event_id>[0-9]+)/family/(?P<family_id>[0-9]+).html$', show_mail_html,
        name="show_mail"),
    url(r'^show_mail/event/(?P<event_id>[0-9]+)/family/cid-(?P<image_name>[a-zA-Z0-9._-]+)$',
        get_joined_document, name="get_joined_document"),
    url(r'^show_mail/event/(?P<event_id>[0-9]+)/family/(?P<family_id>[0-9]+).txt', show_mail_txt),
]
