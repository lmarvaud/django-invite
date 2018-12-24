"""
test_admin

Created by lmarvaud on 03/11/2018
"""
from collections import Iterable
from unittest.mock import patch, Mock

from django.test import TestCase

from invite.models import Family, Guest, Accompany
from .. import admin


class TestMail(TestCase):
    """Test admin mail action"""
    def setUp(self):
        self.family = Family.objects.create(host="Marie")
        self.family.guests.add(
            Guest(name="Françoise", email="valid@example.com", phone="0123456789", female=True),
            Guest(name="Jean", email="valid@example.com", phone="0123456789", female=False),
            bulk=False
        )
        self.family.accompanies.add(
            Accompany(name="Michel", number=1),
            Accompany(name="Michelle", number=1),
            bulk=False
        )

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_send_mass_html_mail_reply_to@example.com"})
    def test_send_mass_html_mail_reply_to(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        families = Family.objects.filter(pk=self.family.pk)

        admin.mail(None, None, families)

        self.assertEqual(send_mass_html_mail__mock.call_count, 1)
        self.assertEqual(send_mass_html_mail__mock.call_args[1]['reply_to'],
                         ["Marie <test_send_mass_html_mail_reply_to@example.com>"])

    @patch.object(admin, 'send_mass_html_mail')
    def test_send_mass_html_mail_to_send(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply to_send argument"""
        families = Family.objects.filter(pk=self.family.pk)

        admin.mail(None, None, families)

        self.assertIsInstance(send_mass_html_mail__mock.call_args[0], Iterable)
        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        expected_subject = "Save the date"
        expected_html = ("Salut Françoise and Jean,<br>\n<br>\n<br>\n"
                         "Comment allez vous ?<br>\n<br>\n"
                         "Comme vous le savez déjà, avec Jean, nous allons nous marier !<br>\n"
                         "<br>\n"
                         "Pour fêter ça, vous êtes conviés avec Michel and Michelle, "
                         "<b>samedi 1er Juin</b> à Paris pour\n\n\n"
                         "une soirée d'enfer !<br>\n<br>\n<b>Save the date !</b><br>\n<br>\n<br>\n"
                         "Marie<br>\n")
        expected_text = ("Salut Françoise and Jean,\n\n\n"
                         "Comment allez vous ?\n\n"
                         "Comme vous le savez déjà, avec Jean, nous allons nous marier !\n\n"
                         "Pour fêter ça, vous êtes conviés avec Michel and Michelle, **samedi 1er "
                         "Juin** à Paris pour une soirée d'enfer !\n\n"
                         "**Save the date !**\n\n\n"
                         "Marie\n")
        self.assertEqual(len(to_send), 1)
        to_send = list(to_send[0])
        self.assertEqual(len(to_send), 5)
        subject, text, html, from_email, recipient = to_send
        self.assertEqual(subject, expected_subject)
        self.assertEqual(text, expected_text)
        self.assertEqual(html, expected_html)
        self.assertIsNone(from_email)
        self.assertListEqual(list(recipient),
                             ["Françoise <valid@example.com>", "Jean <valid@example.com>"])

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin, 'settings')
    def test_using_invite_use_host_in_from_email(self, unused__settings__mock,
                                                 send_mass_html_mail__mock: Mock):
        """Test mail using INVITE_USE_HOST_IN_FROM_EMAIL setting"""
        admin.settings.INVITE_HOSTS = {
            "Marie": "test_using_invite_use_host_in_from_email@example.com"
        }
        admin.settings.INVITE_USE_HOST_IN_FROM_EMAIL = True
        families = Family.objects.filter(pk=self.family.pk)

        admin.mail(None, None, families)

        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        from_email = to_send[0][3]
        self.assertEqual(from_email, "Marie <test_using_invite_use_host_in_from_email@example.com>")

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_send_mass_html_mail_reply_to@example.com"})
    def test_send_mass_html_mail_to_send_no_email(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        self.family.guests.add(
            Guest(name="Pierre", email=None, phone="0123456789", female=False, family=self.family),
            bulk=False
        )
        families = Family.objects.filter(pk=self.family.pk)

        admin.mail(None, None, families)

        recipient = list(send_mass_html_mail__mock.call_args[0][0])[0][4]
        self.assertListEqual(list(recipient),
                             ["Françoise <valid@example.com>", "Jean <valid@example.com>"])
