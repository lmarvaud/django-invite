"""
Views for django-invite project
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe

from .models import Family


@login_required
@require_safe
def show_mail_html(request, family_id):
    """Preview to show html email rendering"""
    family = get_object_or_404(Family, id=family_id)
    return render(request, "invite/mail.html", family.context)

@login_required
@require_safe
def show_mail_txt(request, family_id):
    """Preview to show text email rendering"""
    family = get_object_or_404(Family, id=family_id)
    return render(request, "invite/mail.txt", family.context)
