"""
Test django_invite importguests command

Created by lmarvaud on 01/01/2019
"""
import tempfile
from datetime import date

from django.core.management import call_command
from django.test import TestCase

from invite.models import Family, Event


class TestCommand(TestCase):
    """
    Test django_invite importguests command
    """
    def tearDown(self):
        family = Family.objects.last()
        if family:
            family.delete()
        super(TestCommand, self).tearDown()

    def test_event(self):
        """
        Test that an event is created if required
        """
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                "Email,Tel,Source,Gender,Qui,Accompagnant"
            )
            csv_file.file.close()

            call_command("importguests", csv_file.name, event_date="2018-12-31", event_name="Test")

            self.assertEqual(Event.objects.count(), 1)
            event = Event.objects.get()
            self.assertEqual(event.name, "Test")
            self.assertEqual(event.date, date(2018, 12, 31))

    def test_no_event(self):
        """
        Test that no event is created if not required
        """
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                "Email,Tel,Source,Gender,Qui,Accompagnant"
            )
            csv_file.file.close()

            call_command("importguests", csv_file.name)

            self.assertEqual(Event.objects.count(), 0)

    def test_event_link(self):
        """
        Test that the created event is linked to created families
        """
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                "Email,Tel,Source,Gender,Qui,Accompagnant\n"
                "valid@example.com,0123456789,Marie,F,Jeanne,"
            )
            csv_file.file.close()

            call_command("importguests", csv_file.name, event_date="2018-12-31", event_name="Test")

            event = Event.objects.get()
            self.assertEqual(event.families.count(), 1)
            family = event.families.get()
            self.assertEqual(family.guests.first().name, "Jeanne")

    def test_simple(self):
        """Test importguests command with a simple case : one family with one guest"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                "Email,Tel,Source,Gender,Qui,Accompagnant\n"
                "valid@example.com,0123456789,Marie,F,Anne,"
            )
            csv_file.file.close()

            call_command("importguests", csv_file.name)

            self.assertEqual(Family.objects.count(), 1)
            family = Family.objects.get()
            self.assertEqual(family.guests.count(), 1)
            guest = family.guests.get()
            self.assertEqual(guest.name, "Anne")
            self.assertEqual(guest.email, "valid@example.com")
            self.assertEqual(guest.phone, "0123456789")
            self.assertEqual(guest.female, True)
            self.assertEqual(family.accompanies.count(), 0)

    def test_double(self):
        """Test importguests command with a complexer family : one family with two guests"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                "Email,Tel,Source,Gender,Qui,Accompagnant\n"
                "\"valid@example.com,correct@example.com\",0123456789,Marie,\"F,M\","
                "\"Jeanne,Pierre\","
            )
            csv_file.file.close()

            call_command("importguests", csv_file.name)

            self.assertEqual(Family.objects.count(), 1)
            family = Family.objects.get()
            self.assertEqual(family.guests.count(), 2)
            guest = family.guests.first()
            self.assertEqual(guest.name, "Jeanne")
            self.assertEqual(guest.email, "valid@example.com")
            self.assertEqual(guest.phone, "0123456789")
            self.assertEqual(guest.female, True)
            second_guest = family.guests.last()
            self.assertEqual(second_guest.name, "Pierre")
            self.assertEqual(second_guest.email, "correct@example.com")
            self.assertEqual(second_guest.phone, "")
            self.assertEqual(second_guest.female, False)
            self.assertEqual(family.accompanies.count(), 0)

    def test_accompany(self):
        """Test importguests command with an accompany"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                "Email,Tel,Source,Gender,Qui,Accompagnant\n"
                "\"valid@example.com\",,Marie,F,Jeanne,Jacques"
            )
            csv_file.file.close()

            call_command("importguests", csv_file.name)

            family = Family.objects.get()
            self.assertEqual(family.accompanies.count(), 1)
            accompany = family.accompanies.first()
            self.assertEqual(accompany.name, "Jacques")
            self.assertEqual(accompany.number, 1)

    def test_accompanies(self):
        """Test importguests command with two accompanies"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                "Email,Tel,Source,Gender,Qui,Accompagnant\n"
                "\"valid@example.com\",,Marie,F,Jeanne,\"Jacques and Paul\""
            )
            csv_file.file.close()

            call_command("importguests", csv_file.name)

            family = Family.objects.get()
            self.assertEqual(family.accompanies.count(), 2)
            accompany = family.accompanies.first()
            self.assertEqual(accompany.name, "Jacques")
            self.assertEqual(accompany.number, 1)

            second_accompany = family.accompanies.last()
            self.assertEqual(second_accompany.name, "Paul")
            self.assertEqual(second_accompany.number, 1)
