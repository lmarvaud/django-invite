"""
importguests command

Parse a guest list csv file to store them in the guest list

Created by lmarvaud on 03/11/2019
"""
import csv
import itertools
import logging
import operator
from argparse import RawDescriptionHelpFormatter
try:
    from typing import Optional, Dict
except ImportError:
    pass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandParser
from django.utils.dateparse import parse_date
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from ...join_and import join_and
from ...models import Family, Guest, Accompany, Event

MANY_LIST = ['children', 'girls', 'boys', 'colleges']
EMAIL_KEY = 'Email'
PHONE_KEY = 'Phone'
HOST_KEY = 'Host'
GENDER_KEY = 'Gender'
SURNAME_KEY = 'Surname'
ACCOMPANY_KEY = 'Accompany surname'


def strip(listed):
    """Strip a list of string"""
    return map(operator.methodcaller('strip'), listed)


def multi_split(string, *seps):
    """split a list of separators"""
    split = [string]
    for sep in seps:
        split = itertools.chain.from_iterable(map(operator.methodcaller('split', sep), split))
    return split


def _create_guests(line):
    """Create the guests list from the csv line"""
    emails = list(strip(line[EMAIL_KEY].split(',')))
    phones = list(strip(line[PHONE_KEY].split(',')))
    gender = list(strip(line[GENDER_KEY].split(',')))
    names = list(strip(multi_split(line[SURNAME_KEY], ',', ' et ', '&')))
    for i, name in enumerate(names):
        if i >= len(gender):
            logging.warning('missing gender to %s : SKIPPED', name)
        else:
            yield Guest(name=name,
                        email=emails[i] if len(emails) > i else None,
                        phone=phones[i] if len(phones) > i else '',
                        female=gender[i].upper() == 'F')


def _create_accompagnies(line):
    """Create the accompagnies list from the csv line"""
    if line[ACCOMPANY_KEY]:
        names = list(strip(multi_split(line[ACCOMPANY_KEY], ',', ' ' + str(_('and')) + ' ', '&')))
        for name in names:
            yield Accompany(name=name,
                            number=1 if all(str(_(many)) not in name for many in MANY_LIST) else 2)


class Command(BaseCommand):
    """
csv format is like::

    "Email","Phone","Host","Gender","Surname","Accompany surname"
    "family@email.com","0123456789","Pierre","F","Marie","Jean"

+ *First line* is ignored (title)
+ Each line represent a Family
+ Rows are : "Email","Phone","Host","Gender","Surname","Accompany surname"
+ *Email*, *Phone*, *Gender* and *Surname* will be split by coma : ',', 'and' and '&' to
  retrieve the guest list. Phone is optional but gender and surname must have the same number of
  value (or more) ::

    "marie@example.com,jean@example","0123456789","Pierre","F,M","Marie,Jean"

+ *Host* must be empty or one of the settings.INVITE_HOSTS key. Empty will host will join all
  hosts (Pierre and Jeanne) ::

    INVITE_HOSTS = {
        "Pierre": "pierre@example.com",
        "Jeanne": "jeanne@example.com"
    }

+ *Gender* can be M or F ::

    "","", "", "", "M", ""
    "","", "", "", "F", ""

+ Lines without "email" are ignored ::

    "","ignored", "", "", "", ""
    """
    help = _('Import guests from a csv file')

    def create_parser(self, prog_name, subcommand):
        parser = super(Command, self).create_parser(prog_name=prog_name, subcommand=subcommand)
        parser.epilog = self.__doc__
        parser.formatter_class = RawDescriptionHelpFormatter
        return parser

    def add_arguments(self, parser: CommandParser):
        invitation = parser.add_argument_group(_('Event'),
                                               _('Create an link imported guests to an event'))
        invitation.add_argument('--date', dest='event_date', type=parse_date,
                                help=_('date of the event'))
        invitation.add_argument('--name', dest='event_name', type=str,
                                help=_('name of the event'))
        parser.add_argument('csv', help=_('path to the csv file to parse'))

    def handle(self, *args, **options):
        """Process to the parsing of the csv"""
        owner = get_user_model().objects.filter(is_superuser=True).first()
        if not owner:
            return 'You have to create a superuser first'
        event = self.create_event(owner=owner, **options)
        count = 0
        with open(options['csv'], 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, [
                EMAIL_KEY, PHONE_KEY, HOST_KEY, GENDER_KEY, SURNAME_KEY, ACCOMPANY_KEY
            ])
            next(csv_reader)  # skip 1st line
            midday = True
            afternoon = True
            evening = True
            for line in csv_reader:
                if line[SURNAME_KEY] == 'Sous-total':
                    if midday:
                        midday = False
                    else:
                        afternoon = False
                family = self._create_family(event, line, owner=owner, invited_midday=midday,
                                             invited_afternoon=afternoon, invited_evening=evening)
                if family:
                    count += 1
        return ungettext_lazy('%d family created', '%d families create') % count

    @staticmethod
    def _create_family(event, line, owner, **kwargs):
        # type: (Optional[Event], Dict[str, str]) -> Optional[Family]
        """
        Parse csv line to create a family object
        """
        if line[EMAIL_KEY]:
            if line[HOST_KEY] and line[HOST_KEY] not in settings.INVITE_HOSTS:
                logging.warning('%s source not referenced in the setting INVITE_HOSTS',
                                line[HOST_KEY])
            host = line[HOST_KEY] if line[HOST_KEY] in settings.INVITE_HOSTS else \
                join_and(list(settings.INVITE_HOSTS.keys()))
            guests = _create_guests(line)
            accompagies = _create_accompagnies(line)
            family = Family.objects.create(host=host, **kwargs)
            family.owners.add(owner)
            family.guests.add(*guests, bulk=False)
            family.accompanies.add(*accompagies, bulk=False)
            if event:
                family.invitations.add(event)
            return family
        return None

    @staticmethod
    def create_event(event_date, event_name, owner, **unused_options):
        """
        Potentially create an invitation with the name and date from the option if one of those is
        specified

        :param options: the options
        :return: The invitation or None
        """
        invitation = None
        if event_date or event_name:
            params = {}
            if event_date:
                params['date'] = event_date
            if event_name:
                params['name'] = event_name
            invitation = Event.objects.create(**params)  # type: Event
            invitation.owners.add(owner)
        return invitation
