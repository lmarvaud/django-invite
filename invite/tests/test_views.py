"""
Test django-admin views

Created by lmarvaud on 01/01/2019
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from django.urls import reverse

from invite.tests.common import TestEventMixin
from invite.tests.test_admin import MockRequest
from invite.views import show_mail_txt, show_mail_html


class TestShowMailTxt(TestEventMixin, TestCase):
    """test show_mail_txt view"""
    def test_show_mail_txt(self):
        """test with success"""
        result = show_mail_txt(MockRequest.instance(), self.family.pk)

        self.assertEqual(result.content.decode("utf-8"), self.expected_text)

    def test_url_unlogged(self):
        """Test url acces to show the email, with unlogged user"""
        result = self.client.get('/invite/show_mail/%d.txt' % self.family.pk)

        self.assertEqual(result.status_code, 302)

    def test_url_logged(self):
        """Test url acces to show the email, with logged user"""
        get_user_model().objects.create_superuser("superuser", "", "password")
        self.client.login(username="superuser", password="password")

        result = self.client.get('/invite/show_mail/%d.txt' % self.family.pk)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content.decode("utf-8"), self.expected_text)


class TestShowMailHtml(TestEventMixin, TestCase):
    """test show_mail_txt view"""
    def test_show_mail_html(self):
        """test with success"""
        result = show_mail_html(MockRequest.instance(), self.family.pk)

        self.assertHTMLEqual(result.content.decode("utf-8"), self.expected_html)

    def test_url_unlogged(self):
        """Test url acces to show the email, with unlogged user"""
        result = self.client.get(reverse("show_mail", kwargs={"family_id": self.family.pk}))

        self.assertEqual(result.status_code, 302)

    def test_url_logged(self):
        """Test url acces to show the email, with logged user"""
        get_user_model().objects.create_superuser("superuser", "", "password")
        self.client.login(username="superuser", password="password")

        result = self.client.get(reverse("show_mail", kwargs={"family_id": self.family.pk}))

        self.assertEqual(result.status_code, 200)
        self.assertHTMLEqual(result.content.decode("utf-8"), self.expected_html)
