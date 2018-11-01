"""
Admin configurations for django-invite project
"""
from django.contrib import admin
from .models import Family, Guest, Accompany


class InviteInline(admin.TabularInline):
    """
    Family guest admin view
    """
    model = Guest


class AccompanyInline(admin.TabularInline):
    """
    Family accompanies admin view
    """
    model = Accompany


@admin.register(Family, site=admin.site)
class FamilyAdmin(admin.ModelAdmin):
    """
    Family admin view
    """
    inlines = [InviteInline, AccompanyInline]
