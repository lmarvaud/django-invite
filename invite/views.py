"""
Views for django-invite project
"""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe
from django.utils.translation import gettext as _

from .models import Family, Event


@login_required
@require_safe
def show_mail_html(request, event_id, family_id):
    """Preview to show html email rendering"""
    event = get_object_or_404(Event, id=event_id)
    if not event.has_mailtemplate:
        return HttpResponse(_("The event has no email template set"), status=400)
    family = get_object_or_404(Family, id=family_id)
    response = event.mailtemplate.render_html(context=event.context(family), request=request)
    return HttpResponse(response)

@login_required
@require_safe
def show_mail_txt(request, event_id, family_id):
    """Preview to show text email rendering"""
    event = get_object_or_404(Event, id=event_id)
    if not event.has_mailtemplate:
        return HttpResponse(_("The event has no email template set"), status=400)
    family = get_object_or_404(Family, id=family_id)
    response = event.mailtemplate.render_text(context=event.context(family), request=request)
    return HttpResponse(response)
