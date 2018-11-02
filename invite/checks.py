"""
checks

Created by lmarvaud on 02/11/2018
"""
import os

from django.conf import settings, ENVIRONMENT_VARIABLE
from django.core.checks import register, Tags, Error


@register(Tags.compatibility)
def check_invite_hosts_settings(app_configs):  # pylint: disable=unused-argument
    """
    Check the if the INVITE_HOSTS settings is set and valid
    """
    errors = []
    if not hasattr(settings, "INVITE_HOSTS"):
        errors.append(Error(
            "INVITE_HOSTS setting is not define",
            hint="Add INVITE_HOSTS dict in your settings {}\n"
                 "Example:\n"
                 "INVITE_HOSTS = {{\n"
                 "    \"Your surname\": \"Your email\"\n"
                 "}}".format(os.environ.get(ENVIRONMENT_VARIABLE)),
            obj="settings",
            id="INVITE_E001"))
    elif not isinstance(settings.INVITE_HOSTS, dict):
        errors.append(Error(
            "INVITE_HOSTS setting is not a valid type",
            hint="Use a dict",
            obj="settings",
            id="INVITE_E002"
        ))
    return errors
