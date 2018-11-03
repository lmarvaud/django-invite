"""
test_send_mass_html_mail

Created by lmarvaud on 03/11/2018
"""
from unittest.mock import patch

import django.conf
from django.core import mail
from django.test import TestCase

from invite.send_mass_html_mail import send_mass_html_mail


class TestSendMassHtmlMail(TestCase):
    """Test send_mass_html_mail"""
    def test(self):
        """Test send_mass_html_mail"""
        send_mass_html_mail([
            ("subject%d" % i, "text%d" % i, "html%d" % i, "from_email%d@example.com" % i,
             ["recipient%d@example.com" % i])
            for i in range(3)
        ], reply_to=["reply_to@example.com"])

        self.assertEqual(len(mail.outbox), 3)
        for i in range(3):
            self.assertEqual(mail.outbox[i].subject, "subject%d" % i)
            self.assertEqual(mail.outbox[i].body, "text%d" % i)
            self.assertEqual(mail.outbox[i].from_email, "from_email%d@example.com" % i)
            self.assertListEqual(mail.outbox[i].to, ["recipient%d@example.com" % i])
            self.assertListEqual(mail.outbox[i].alternatives, [("html%d" % i, "text/html")])
            self.assertListEqual(mail.outbox[i].reply_to, ["reply_to@example.com"])

    @patch.object(django.conf.settings, 'DEFAULT_FROM_EMAIL', 'valid@example.com')
    def test_no_from_email(self):
        """Test send_mass_html_mail without from_email"""
        send_mass_html_mail([
            ("subject", "text", "html", None, ["recipient@example.com"])
        ], reply_to=["reply_to@example.com"])

        self.assertEqual(mail.outbox[0].from_email, "valid@example.com")
