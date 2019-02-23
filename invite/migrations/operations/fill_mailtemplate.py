"""
Migrations operations

Created by lmarvaud on 31/01/2019
"""
from django.apps.registry import Apps
from django.template.loader import get_template


def _get_template(path: str) -> str:
    """Retrieve a template source for a path"""
    template = get_template(path)
    return template.template.source


def _get_mail_templates() -> tuple:
    """Retrieve the default template"""
    subject = _get_template("invite/subject.txt")
    text = _get_template("invite/mail.txt")
    html = _get_template("invite/mail.html")
    return subject, text, html


def code(apps: Apps, unused_schema_editor=None):
    """Create the mail templates for all existing events"""
    mailtemplate_class = apps.get_model("invite", "MailTemplate")
    event_class = apps.get_model("invite", "Event")
    subject, text, html = _get_mail_templates()
    for event in event_class.objects.all():
        mailtemplate_class.objects.create(
            event=event,
            subject=subject,
            text=text,
            html=html,
        )


def reverse_code(apps: Apps, unused_schema_editor=None):
    """Create the mail templates for all existing events"""
    mailtemplate_class = apps.get_model("invite", "MailTemplate")
    subject, text, html = _get_mail_templates()
    mailtemplate_class.objects.filter(
        subject=subject,
        text=text,
        html=html
    ).delete()
