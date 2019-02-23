"""
Test django-invite models

Created by lmarvaud on 01/01/2019
"""
from unittest import TestCase

from datetime import date

from invite.models import Guest, Accompany, Event
from invite.tests.common import TestFamilyMixin, TestEventMixin


class TestFamily(TestFamilyMixin, TestCase):
    """
    Test Family model
    """
    def test_context(self):
        """
        test context return value
        """
        expected_result = {
            "family": self.family,
            "all": "Françoise, Jean, Michel and Michelle",
            "count": 4,
            "accompanies": "Michel and Michelle",
            "accompanies_e": "",
            "accompanies_count": 2,
            "e": "",
            "guests": "Françoise and Jean",
            "guests_count": 2,
            "has_accompanies": True,
            "has_accompany": True,
            "is_female": False,
            "accompanies_are_female": False,
        }

        result = self.family.context

        self.assertDictEqual(expected_result, result)

    def test_str(self):
        """
        test str return value
        """
        self.assertEqual(self.family.__str__(), "Françoise, Jean, Michel and Michelle family")

    def test_format(self):
        """
        test family format method
        """
        self.assertEqual("{family:accompanies}".format(family=self.family),
                         "Michel and Michelle")

    def test_format_error(self):
        """
        test invalid family format
        """
        self.assertRaises(ValueError, "{family:invalid}".format, family=self.family)


class TestGuest(TestCase):
    """
    Test Guest model
    """
    def test_str(self):
        """
        test __str__ return value on Guest object
        """
        guest = Guest(name="Jean", email="valid@example.com")
        expected_result = "Jean <valid@example.com>"

        result = str(guest)

        self.assertEqual(result, expected_result)


class TestAccompany(TestCase):
    """
    Test Accompany model
    """
    def test_str(self):
        """
        test __str__ return value on Accompany object
        """
        accompany = Accompany(name="Jean")
        expected_result = "Jean"

        result = str(accompany)

        self.assertEqual(result, expected_result)


class TestEvent(TestEventMixin, TestCase):
    """
    Test Event model
    """
    def test_context(self):
        """
        test event context return value
        """
        expected_result = {
            "event": self.event,
            "family": self.family,
            "all": "Françoise, Jean, Michel and Michelle",
            "count": 4,
            "accompanies": "Michel and Michelle",
            "accompanies_e": "",
            "accompanies_count": 2,
            "e": "",
            "guests": "Françoise and Jean",
            "guests_count": 2,
            "has_accompanies": True,
            "has_accompany": True,
            "is_female": False,
            "accompanies_are_female": False,
        }

        result = self.event.context(self.family)

        self.assertDictEqual(expected_result, result)

    def test_str_empty(self):
        """
        test __str__ return value on Event object  without name nor date
        """
        expected_result = "1"
        event = Event(pk=1, name="", date=None)

        self.assertEqual(str(event), expected_result)

    def test_str_without_date(self):
        """
        test __str__ return value on Event object without date
        """
        expected_result = "Test"
        event = Event(pk=1, name="Test", date=None)

        self.assertEqual(str(event), expected_result)

    def test_str_without_name(self):
        """
        test __str__ return value on Event object without name
        """
        expected_result = "event of the 2018-12-31"
        event = Event(pk=1, name="", date=date(2018, 12, 31))

        self.assertEqual(str(event), expected_result)

    def test_str(self):
        """
        test __str__ return value on Event object
        """
        expected_result = "Test of the 2018-12-31"
        event = Event(pk=1, name="Test", date=date(2018, 12, 31))

        self.assertEqual(str(event), expected_result)
