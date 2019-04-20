"""
Django app configurations for invite application
"""
import importlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InviteConfig(AppConfig):
    """Default config for the invite application"""
    name = 'invite'
    verbose_name = _('invite')

    def ready(self):
        importlib.import_module('invite.checks')
