"""
Django-invite common test mixin

Created by lmarvaud on 01/01/2019
"""
from datetime import date

from invite.models import Family, Guest, Accompany, Event


class TestFamilyMixin:
    """
    Test case mixin creating a family
    """
    family = None

    def setUp(self):  # pylint: disable=invalid-name
        """
        Create the family
        """
        super(TestFamilyMixin, self).setUp()
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

    def tearDown(self):  # pylint: disable=invalid-name
        """
        Delete the family
        """
        self.family.delete()
        self.family = None
        super(TestFamilyMixin, self).tearDown()


class TestEventMixin(TestFamilyMixin):
    """
    Test case mixin creating an event with a family
    """
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
    event = None

    def setUp(self):
        """
        Create the event and call TestFamilyMixin to create the family
        """
        super(TestEventMixin, self).setUp()
        self.event = Event.objects.create(name="test", date=date(2018, 12, 31))
        self.event.families.add(self.family)

    def tearDown(self):
        """
        Delete the event
        """
        self.event.delete()
        self.event = None
        super(TestEventMixin, self).tearDown()
