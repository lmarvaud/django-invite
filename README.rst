=============
django_invite
=============

Django invite is an Application to help managing guest and invitation on django project

Install
========

Install the package ::

    pip install django_invite

In your django project settings, add the "invite" app at the end of the installed app

*settings.py*::

    INSTALLED_APP = [
        ...,
	"<your app>",
        "invite"
    ]

Register your host(s) in your *settings.py*::

    INVITE_HOSTS = {
        "Marie": "marie@example.com",
        "Jean": "jean@example.com"
    }

Then update your database ::

    python manage.py migrate invite

Configuration
=============

Import some guests
------------------

Threw the admin or threw the command line (cf. `importguests command`_) ::

    python manage.py importguests guestlist.csv

Email
-----

To configure the email to be sent, in your project create the files :

- ``/<your app>/templates/invite/mail.html``
- ``/<your app>/templates/invite/mail.txt``
- ``/<your app>/templates/invite/subject.txt``

And fill them with your content.

Existing variables are :

============================== ============================================
Template variables             Description
============================== ============================================
**Event**
---------------------------------------------------------------------------
``{event}``                    An event object containing next arguments
``{event.name}``               The event name (optionnal)
``{event.date}``               The event date (optionnal)
**Family**
---------------------------------------------------------------------------
``{family}``                   A family object containing next arguments
``{family.invited_midday}``    Boolean to invite the members on the 1st part of the event
``{family.invited_afternoon}`` Boolean to invite the members on the 2nd part of the event
``{family.invited_evening}``   Boolean to invite the members on the 3rd part of the event
``{family.host}``              The person that host the family
``{family.guests}``            The guest list
``{family.accompanies}``       The accompany list
**Members**
---------------------------------------------------------------------------
``{all}``                      Names of all the members name
``{count}``                    Number of members
**Guests**
---------------------------------------------------------------------------
``{guests}``                   Names of the guests
``{guests_count}``             Number of guests
``{e}``                        "" or "*e*" or "*s*" or "*es*" if there is one male, one female, many male (and/or female) or many female
**Accompanies**
---------------------------------------------------------------------------
``{accompanies}``              Names of the accompanies
``{accompanies_count}``        Number of accompanies
``{has_accompanies}``          Boolean wether there is many accompanies or not
``{has_accompany}``            Boolean wether there is any accompanies or none
============================== ============================================

### template extra filter

You can add some extra template by adding :

    {% load invite_extras %}

in the template. This give you access to :

=============== =======
filter          example
=============== =======
``attrgetter``  ``{{family.guests | attrgetter:"name" | join:", "}}`` would display : ``Michelle, Jean``
``itemgetter``  ``{{family.guests | attrgetter:"name" | itemgetter:0 | join:","}}`` would display : ``M, J``
``join_and``    ``{{family.guests | attrgetter:"name" | join_and}}`` would display : ``Michelle and Jean``


`importguests` command
----------------------

usage: manage.py importguests [-h] [--version] [-v {0,1,2,3}]
                              [--settings SETTINGS] [--pythonpath PYTHONPATH]
                              [--traceback] [--no-color] [--date EVENT_DATE]
                              [--name EVENT_NAME]
                              csv

Import guests from a csv file

positional arguments::

  csv                   path to the csv file to parse

optional arguments::

  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output,
                        2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g.
                        "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be
                        used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions
  --no-color            Don't colorize the command output.

Event::

  Create an link imported guests to an event

  --date EVENT_DATE     date of the event
  --name EVENT_NAME     name of the event

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
