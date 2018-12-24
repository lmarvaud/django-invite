"""
importguests command

Parse a guest list csv file to store them in the guest list
"""
import csv
import itertools
import logging
import operator
from argparse import RawDescriptionHelpFormatter

from django.conf import settings
from django.core.management import BaseCommand, CommandParser
from django.utils.translation import ugettext_lazy as _

from ...join_and import join_and
from ...models import Family, Guest, Accompany

MANY_LIST = ['children', 'girls', 'boys', 'colleges']


def strip(listed):
    """Strip a list of string"""
    return map(operator.methodcaller("strip"), listed)


def multi_split(string, *seps):
    """split a list of separators"""
    split = [string]
    for sep in seps:
        split = itertools.chain.from_iterable(map(operator.methodcaller('split', sep), split))
    return split


def _create_guests(line):
    """Create the guests list from the csv line"""
    emails = list(strip(line["Email"].split(',')))
    phones = list(strip(line["Tel"].split(',')))
    gender = list(strip(line["Gender"].split(',')))
    names = list(strip(multi_split(line["Qui"], ',', ' et ', '&')))
    for i, name in enumerate(names):
        if i > len(gender):
            logging.warning("missing gender to %s : SKIPPED", name)
        else:
            yield Guest(name=name,
                        email=emails[i] if len(emails) > i else None,
                        phone=phones[i] if len(phones) > i else "",
                        female=gender[i].upper() == 'F')


def _create_accompagnies(line):
    """Create the accompagnies list from the csv line"""
    if line["Accompagnant"]:
        names = list(strip(multi_split(line["Accompagnant"], ',', ' ' + str(_('and')) + ' ', '&')))
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

+ Lines without "email" are ignored

    "","ignored", "", "", "", ""
    """
    help = "Import guests from a csv"

    def create_parser(self, prog_name, subcommand):
        parser = super(Command, self).create_parser(prog_name=prog_name, subcommand=subcommand)
        parser.epilog = self.__doc__
        parser.formatter_class = RawDescriptionHelpFormatter
        return parser

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("csv", help="path to the csv file to parse")

    def handle(self, *args, **options):
        """Process to the parsing of the csv"""
        with open(options["csv"], 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, [
                "Email", "Tel", "Source", "Gender", "Qui", "Accompagnant"
            ])
            next(csv_reader)  # skip 1st line
            midday = True
            afternoon = True
            evening = True
            for line in csv_reader:
                if line["Qui"] == "Sous-total":
                    if midday:
                        midday = False
                    else:
                        afternoon = False
                if line["Email"]:
                    if line["Source"] and line["Source"] not in settings.INVITE_HOSTS:
                        logging.warning("%s source not referenced in the setting INVITE_HOST",
                                        line["Source"])
                    host = line["Source"] if line["Source"] in settings.INVITE_HOSTS else \
                        join_and(list(settings.INVITE_HOSTS.keys()))
                    guests = _create_guests(line)
                    accompagies = _create_accompagnies(line)
                    family = Family.objects.create(invited_midday=midday,
                                                   invited_afternoon=afternoon,
                                                   invited_evening=evening,
                                                   host=host)
                    family.guests.add(*guests, bulk=False)
                    family.accompanies.add(*accompagies, bulk=False)
