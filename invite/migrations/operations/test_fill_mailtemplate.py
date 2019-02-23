"""
test_fill_mailtemplate

Created by lmarvaud on 01/02/2019
"""
from unittest import TestCase
from unittest.mock import patch, Mock, call

from django.apps import apps

from invite.models import MailTemplate
from . import fill_mailtemplate
from ...tests.common import TestEventMixin


@patch.object(fill_mailtemplate, "get_template",
              return_value=Mock(template=Mock(source="Template source")))
class TestCode(TestEventMixin, TestCase):
    """
    Test fill_mailtemplate migration operations
    """
    @staticmethod
    def assert_get_template_has_calls(get_template_mock: Mock):
        """
        Assert if the get_template_mock has not been called 3 times with expected templates names

        :param get_template_mock: the get_template function mock
        """
        get_template_mock.assert_has_calls([
            call(("invite/subject.txt")),
            call(("invite/mail.txt")),
            call(("invite/mail.html")),
        ])

    def test_code(self, get_template_mock: Mock):
        """
        Test the migration code

        :param get_template_mock: the get_template function mock
        """
        fill_mailtemplate.code(apps)

        self.assert_get_template_has_calls(get_template_mock)
        self.assertTrue(self.event.has_mailtemplate)
        self.assertEqual(self.event.mailtemplate.subject, "Template source")
        self.assertEqual(self.event.mailtemplate.text, "Template source")
        self.assertEqual(self.event.mailtemplate.html, "Template source")

    def test_reverse_code(self, get_template_mock):
        """
        Test reverse function of the migration

        :param get_template_mock: the get_template function mock
        """
        MailTemplate.objects.create(event=self.event, text="Template source",
                                    html="Template source", subject="Template source")

        fill_mailtemplate.reverse_code(apps)
        self.event.refresh_from_db()

        self.assert_get_template_has_calls(get_template_mock)
        self.assertFalse(self.event.has_mailtemplate)

    def test_reverse_code_modified(self, get_template_mock):
        """
        Test reverse function of the migration on modified templates

        :param get_template_mock: the get_template function mock
        """
        MailTemplate.objects.create(event=self.event, text="Modified source",
                                    html="Modified source", subject="Modified source")

        fill_mailtemplate.reverse_code(apps)
        self.event.refresh_from_db()

        self.assert_get_template_has_calls(get_template_mock)
        self.assertTrue(self.event.has_mailtemplate)
