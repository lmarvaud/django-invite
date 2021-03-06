"""
Django-invite common test mixin

Created by lmarvaud on 01/01/2019
"""
from datetime import date

from os import path

from invite.models import Family, Guest, Accompany, Event, MailTemplate


class TestFamilyMixin:
    """
    Test case mixin creating a family
    """
    family = None

    @staticmethod
    def create_family(name_suffix: str = ""):
        """
        Create a family with 2 guests and 2 accompanies

        Guests are named "Françoise{{name_suffix}}" and "Jean{{name_suffix}}"
        Accompanies : "Michel{{name_suffix}}" and "Michelle{{name_suffix}}

        :param name_suffix:
        :param host:
        :return:
        """
        family = Family.objects.create(host="Marie")
        family.guests.add(
            Guest(name="Françoise%s" % name_suffix, email="valid@example.com", phone="0123456789",
                  female=True),
            Guest(name="Jean%s" % name_suffix, email="valid@example.com", phone="0123456789",
                  female=False),
            bulk=False
        )
        family.accompanies.add(
            Accompany(name="Michel%s" % name_suffix, number=1),
            Accompany(name="Michelle%s" % name_suffix, number=1),
            bulk=False
        )
        return family

    def setUp(self):  # pylint: disable=invalid-name
        """
        Create the family
        """
        super(TestFamilyMixin, self).setUp()
        self.family = self.create_family()

    def tearDown(self):  # pylint: disable=invalid-name
        """
        Delete the family
        """
        self.family.delete()
        super(TestFamilyMixin, self).tearDown()


class TestMailTemplateMixin:  # pylint: disable=too-few-public-methods
    """
    Test case mixin that create a mail template for an event

    Note: the event has te be created before the set up as been created. You may order the subclass
    like :
    ```python
    class TestFamilyAdmin(TestMailTemplateMixin, TestEventMixin, TestCase):
    ```
    """
    event = None

    def setUp(self):  # pylint: disable=invalid-name
        """
        Create a mail template for the event test case event
        """
        super(TestMailTemplateMixin, self).setUp()
        text_template = open(path.join(path.dirname(__file__), "templates", "mail.txt")).read()
        html_template = open(path.join(path.dirname(__file__), "templates", "mail.html")).read()
        subject_template = open(path.join(path.dirname(__file__), "templates",
                                          "subject.txt")).read()
        MailTemplate.objects.create(event=self.event, text=text_template, html=html_template,
                                    subject=subject_template)


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


    @staticmethod
    def create_event(*family, name="test"):
        """Create an event with family"""
        event = Event.objects.create(name=name, date=date(2018, 12, 31))
        event.families.add(*family)
        return event

    def setUp(self):
        """
        Create the event and call TestFamilyMixin to create the family
        """
        super(TestEventMixin, self).setUp()
        self.event = self.create_event(self.family)

    def tearDown(self):
        """
        Delete the event
        """
        self.event.delete()
        super(TestEventMixin, self).tearDown()


class MockSuperUser:  # pylint: disable=too-few-public-methods
    """Fake super user"""
    is_authenticated = True
    is_active = True
    is_staff = True
    is_superuser = True

    @staticmethod
    def has_perm(unused_perm):
        """Return super user permission : always True"""
        return True


class MockRequest:  # pylint: disable=too-few-public-methods
    """Fake request"""
    _instance = None
    method = "GET"

    def __init__(self):
        """Initialize the user"""
        self.user = MockSuperUser()

    @classmethod
    def instance(cls):
        """Gest singleton instance"""
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
