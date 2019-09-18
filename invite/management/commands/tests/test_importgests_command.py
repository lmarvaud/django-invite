"""
Test django_invite importguests command

Created by lmarvaud on 01/01/2019
"""
import tempfile
from datetime import date
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from invite.models import Family, Event
from .. import importguests


class TestCommand(TestCase):
    """
    Test django_invite importguests command
    """

    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(
            'test_superuser', 'valid@example.com', 'qpGsfN@cP0L})cW#kq')
        super(TestCommand, self).setUp()

    def tearDown(self):
        family = Family.objects.last()
        if family:
            family.delete()
        self.superuser.delete()
        super(TestCommand, self).tearDown()

    def test_event(self):
        """
        Test that an event is created if required
        """
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant'
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name, event_date='2018-12-31', event_name='Test')

            self.assertEqual(Event.objects.count(), 1)
            event = Event.objects.get()
            self.assertEqual(event.name, 'Test')
            self.assertEqual(event.date, date(2018, 12, 31))

    def test_no_event(self):
        """
        Test that no event is created if not required
        """
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant'
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name)

            self.assertEqual(Event.objects.count(), 0)

    def test_partial_event(self):
        """
        Test event creation without all information
        """
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant'
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name, event_date='2018-12-31')

            self.assertEqual(Event.objects.count(), 1)

            event = Event.objects.get()
            self.assertIsNone(event.name)
            self.assertEqual(event.date, date(2018, 12, 31))

            call_command('importguests', csv_file.name, event_name='Test')

            self.assertEqual(Event.objects.count(), 2)

            event = Event.objects.last()
            self.assertEqual(event.name, 'Test')
            self.assertIsNone(event.date)

    def test_event_link(self):
        """
        Test that the created event is linked to created families
        """
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant\n'
                'valid@example.com,0123456789,Marie,F,Jeanne,'
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name, event_date='2018-12-31', event_name='Test')

            event = Event.objects.get()
            self.assertEqual(event.families.count(), 1)
            family = event.families.get()
            self.assertEqual(family.guests.first().name, 'Jeanne')

    def test_simple(self):
        """Test importguests command with a simple case : one family with one guest"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant\n'
                'valid@example.com,0123456789,Marie,F,Anne,'
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name)

            self.assertEqual(Family.objects.count(), 1)
            family = Family.objects.get()
            self.assertEqual(family.host, 'Marie')
            self.assertEqual(family.guests.count(), 1)
            guest = family.guests.get()
            self.assertEqual(guest.name, 'Anne')
            self.assertEqual(guest.email, 'valid@example.com')
            self.assertEqual(guest.phone, '0123456789')
            self.assertEqual(guest.female, True)
            self.assertEqual(family.accompanies.count(), 0)

    def test_double(self):
        """Test importguests command with a complexer family : one family with two guests"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant\n'
                "\"valid@example.com,correct@example.com\",0123456789,Marie,\"F,M\","
                "\"Jeanne,Pierre\","
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name)

            self.assertEqual(Family.objects.count(), 1)
            family = Family.objects.get()
            self.assertEqual(family.guests.count(), 2)
            guest = family.guests.first()
            self.assertEqual(guest.name, 'Jeanne')
            self.assertEqual(guest.email, 'valid@example.com')
            self.assertEqual(guest.phone, '0123456789')
            self.assertEqual(guest.female, True)
            second_guest = family.guests.last()
            self.assertEqual(second_guest.name, 'Pierre')
            self.assertEqual(second_guest.email, 'correct@example.com')
            self.assertEqual(second_guest.phone, '')
            self.assertEqual(second_guest.female, False)
            self.assertEqual(family.accompanies.count(), 0)

    def test_accompany(self):
        """Test importguests command with an accompany"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant\n'
                "\"valid@example.com\",,Marie,F,Jeanne,Jacques"
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name)

            self.assertEqual(Family.objects.count(), 1)
            family = Family.objects.get()
            self.assertEqual(family.accompanies.count(), 1)
            accompany = family.accompanies.first()
            self.assertEqual(accompany.name, 'Jacques')
            self.assertEqual(accompany.number, 1)

    def test_accompanies(self):
        """Test importguests command with two accompanies"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant\n'
                "\"valid@example.com\",,Marie,F,Jeanne,\"Jacques and Paul\""
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name)

            self.assertEqual(Family.objects.count(), 1)
            family = Family.objects.get()
            self.assertEqual(family.accompanies.count(), 2)
            accompany = family.accompanies.first()
            self.assertEqual(accompany.name, 'Jacques')
            self.assertEqual(accompany.number, 1)

            second_accompany = family.accompanies.last()
            self.assertEqual(second_accompany.name, 'Paul')
            self.assertEqual(second_accompany.number, 1)

    @staticmethod
    @override_settings(INVITE_HOSTS={'Jean': 'jean@example.com'})
    @patch.object(importguests.logging, 'warning')
    def test_unknown_host(warning__mock):  # type: (Mock) -> None
        """Test importguests command with unknown host"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant\n'
                "\"valid@example.com\",,Unknown,F,Jeanne,Jacques"
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name)

            family = Family.objects.last()
            family.host = 'Jean'
            warning__mock.assert_any_call('%s source not referenced in the setting INVITE_HOSTS',
                                          'Unknown')

    @override_settings(INVITE_HOSTS={'Jean': 'jean@example.com'})
    @patch.object(importguests.logging, 'warning')
    def test_invalid_gender_number(self, warning__mock):  # type: (Mock) -> None
        """Test importguests command with invalid number of guest gender"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant\n'
                "\"valid@example.com,correct@example.com\",0123456789,Marie,\"F\","
                "\"Jeanne,Pierre\",\n"
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name)

            self.assertEqual(Family.objects.count(), 1)
            family = Family.objects.get()
            self.assertEqual(family.guests.count(), 1)
            warning__mock.assert_any_call('missing gender to %s : SKIPPED', 'Pierre')

    @override_settings(INVITE_HOSTS={'Jean': 'jean@example.com'})
    def test_invalid_name_number(self):  # type: () -> None
        """Test importguests command with invalid number of guest name"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant\n'
                "\"valid@example.com,correct@example.com\",0123456789,Marie,\"F,M\","
                "\"Jeanne\",\n"
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name)

            self.assertEqual(Family.objects.count(), 1)
            family = Family.objects.get()
            self.assertEqual(family.guests.count(), 1)

    @override_settings(INVITE_HOSTS={'Jean': 'jean@example.com'})
    def test_invalid_email_number(self):  # type: (Mock) -> None
        """Test importguests command with invalid number of guest name"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant\n'
                "\"valid@example.com\",0123456789,Marie,\"F,M\","
                "\"Jeanne,Pierre\",\n"
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name)

            self.assertEqual(Family.objects.count(), 1)
            family = Family.objects.get()
            self.assertEqual(family.guests.count(), 2)
            self.assertIsNone(family.guests.last().email)

    def test_comment_lines(self):
        """Test importguests command with comment lines"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                'Email,Tel,Source,Gender,Qui,Accompagnant\n'
                ',comment\n'  # no mail == comment
                '\n'  # empty lines
            )
            csv_file.file.close()

            call_command('importguests', csv_file.name)

            self.assertEqual(Family.objects.count(), 0)

    def test_without_superuser(self):  # type: () -> None
        """Test importguests command in the case where no super user has been created yet"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write('Email,Tel,Source,Gender,Qui,Accompagnant\n')
            csv_file.file.close()

            self.superuser.is_superuser = False
            self.superuser.save()

            response = call_command('importguests', csv_file.name)

            self.assertEqual(response, 'You have to create a superuser first')
