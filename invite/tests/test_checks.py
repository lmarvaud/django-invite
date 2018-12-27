"""
test_checks

Created by lmarvaud on 03/11/2018
"""
from unittest.mock import patch

from django.test.testcases import TestCase

from .. import checks


class TestCheckInviteHostsSettings(TestCase):
    """Test checks on INVITE_HOSTS setting"""
    def test_valid(self):
        """Test checks with a valid INVITE_HOSTS setting"""
        with patch.object(checks.settings, "INVITE_HOSTS", {
                "valid": "valid@example.com",
        }):
            result = checks.check_invite_hosts_settings(None)

            self.assertListEqual(result, [])

    def test_missing(self):
        """Test checks with a missing INVITE_HOSTS setting"""
        with patch.object(checks, "settings"):
            del checks.settings.INVITE_HOSTS
            result = checks.check_invite_hosts_settings(None)

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].id, "INVITE_E001")

    def test_type(self):
        """Test checks with an invalid INVITE_HOSTS setting type"""
        with patch.object(checks.settings, "INVITE_HOSTS", []):
            result = checks.check_invite_hosts_settings(None)

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].id, "INVITE_E002")
