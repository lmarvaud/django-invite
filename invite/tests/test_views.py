"""
Test django-admin views

Created by lmarvaud on 01/01/2019
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from invite.models import MailTemplate
from invite.tests.common import TestEventMixin, TestMailTemplateMixin, MockRequest
from invite.views import show_mail_txt, show_mail_html


class TestShowMailTxt(TestMailTemplateMixin, TestEventMixin, TestCase):  # pylint: disable=too-many-ancestors
    """test show_mail_txt view"""

    def test_show_mail_txt(self):
        """test with success"""
        result = show_mail_txt(MockRequest.instance(), self.event.pk, self.family.pk)

        self.assertEqual(result.content.decode('utf-8'), self.expected_text)

    def test_url_unlogged(self):
        """Test url acces to show the email, with unlogged user"""
        result = self.client.get('/invite/show_mail/event/%d/family/%d.txt' % (self.family.pk,
                                                                               self.event.pk))

        self.assertEqual(result.status_code, 302)

    def test_url_logged(self):
        """Test url acces to show the email, with logged user"""
        get_user_model().objects.create_superuser('superuser', '', 'password')
        self.client.login(username='superuser', password='password')

        result = self.client.get('/invite/show_mail/event/%d/family/%d.txt' % (self.family.pk,
                                                                               self.event.pk))

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content.decode('utf-8'), self.expected_text)

    def test_show_mail_without_template(self):
        """Test without template"""
        event = self.create_event(self.family)
        get_user_model().objects.create_superuser('superuser', '', 'password')
        self.client.login(username='superuser', password='password')

        result = self.client.get('/invite/show_mail/event/%d/family/%d.txt' % (
            event.pk,
            self.family.pk,
        ))

        self.assertEqual(result.status_code, 400)


class TestShowMailHtml(TestMailTemplateMixin, TestEventMixin, TestCase):  # pylint: disable=too-many-ancestors
    """test show_mail_txt view"""
    expected_html = TestMailTemplateMixin.expected_html.replace('cid:', 'cid-')

    def test_show_mail_html(self):
        """test with success"""
        result = show_mail_html(MockRequest.instance(), self.event.pk, self.family.pk)

        self.assertHTMLEqual(result.content.decode('utf-8'), self.expected_html)

    def test_url_unlogged(self):
        """Test url acces to show the email, with unlogged user"""
        result = self.client.get(reverse('show_mail', kwargs={'family_id': self.family.pk,
                                                              'event_id': self.event.pk}))

        self.assertEqual(result.status_code, 302)

    def test_url_logged(self):
        """Test url acces to show the email, with logged user"""
        get_user_model().objects.create_superuser('superuser', '', 'password')
        self.client.login(username='superuser', password='password')

        result = self.client.get(reverse('show_mail', kwargs={'family_id': self.family.pk,
                                                              'event_id': self.event.pk}))

        self.assertEqual(result.status_code, 200)
        self.assertHTMLEqual(result.content.decode('utf-8'), self.expected_html)

    def test_show_mail_without_template(self):
        """Test without template"""
        event = self.create_event(self.family)
        get_user_model().objects.create_superuser('superuser', '', 'password')
        self.client.login(username='superuser', password='password')

        result = self.client.get('/invite/show_mail/event/%d/family/%d.html' % (
            event.pk,
            self.family.pk,
        ))

        self.assertEqual(result.status_code, 400)

    def test_show_image(self):
        """Test get_joined_document view"""
        get_user_model().objects.create_superuser('superuser', '', 'password')
        self.client.login(username='superuser', password='password')

        result = self.client.get(reverse('get_joined_document', kwargs={'image_name': 'happy.png',
                                                                        'event_id': self.event.pk}))
        self.assertEqual(result.status_code, 200)

    def test_show_image_invalid_name(self):
        """Test get_joined_document view with invalid image name"""
        get_user_model().objects.create_superuser('superuser', '', 'password')
        self.client.login(username='superuser', password='password')

        result = self.client.get(reverse('get_joined_document',
                                         kwargs={'image_name': 'invalid_name',
                                                 'event_id': self.event.pk}))
        self.assertEqual(result.status_code, 404)

    def test_show_image_without_event(self):
        """Test get_joined_document view with an document not referenced in an event"""
        event = self.create_event(self.family)
        MailTemplate.objects.create(event=event, text='', html='', subject='')
        get_user_model().objects.create_superuser('superuser', '', 'password')
        self.client.login(username='superuser', password='password')

        result = self.client.get(reverse('get_joined_document',
                                         kwargs={'image_name': 'happy.png',
                                                 'event_id': event.pk}))
        self.assertEqual(result.status_code, 404)

    def test_show_image_invalid_event(self):
        """Test get_joined_document view with event without mail template"""
        event = self.create_event(self.family)
        get_user_model().objects.create_superuser('superuser', '', 'password')
        self.client.login(username='superuser', password='password')

        result = self.client.get(reverse('get_joined_document',
                                         kwargs={'image_name': 'happy.png',
                                                 'event_id': event.pk}))
        self.assertEqual(result.status_code, 400)
