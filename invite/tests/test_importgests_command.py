"""
Test django_invite importguests command
"""
import tempfile

from django.test import TestCase

from invite.management.commands import importguests
from invite.models import Family


class TestCommand(TestCase):
    """
    Test django_invite importguests command
    """
    def tearDown(self):
        family = Family.objects.last()
        if family:
            family.delete()
        super(TestCommand, self).tearDown()

    def test_simple(self):
        """Test importguests command with a simple case : one family with one guest"""
        with tempfile.NamedTemporaryFile('w+') as csv_file:
            csv_file.write(
                "Email,Tel,Source,Gender,Qui,Accompagnant\n"
                "valid@example.com,0123456789,Marie,F,Anne,"
            )
            csv_file.file.close()

            importguests.Command().handle(csv=csv_file.name)

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

            importguests.Command().handle(csv=csv_file.name)

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

            importguests.Command().handle(csv=csv_file.name)

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

            importguests.Command().handle(csv=csv_file.name)

            family = Family.objects.get()
            self.assertEqual(family.accompanies.count(), 2)
            accompany = family.accompanies.first()
            self.assertEqual(accompany.name, "Jacques")
            self.assertEqual(accompany.number, 1)

            second_accompany = family.accompanies.last()
            self.assertEqual(second_accompany.name, "Paul")
            self.assertEqual(second_accompany.number, 1)
