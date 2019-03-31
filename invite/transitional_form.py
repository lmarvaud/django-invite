"""
Django admin decorator to add a transitional form to admin actions


*How it works*

When calling the action the decorator render the admin/transitional_action.html template which
display the form TransitionalForm.

When validate, the action is call again (thanks to the TransitionalForm) and the form is now
validated. If the form is valid the function is call, otherwise the form is re-render with the
errors displayed


*Usage*

1.  Create a django form which inherit from TransitionalForm, with field to retrieve in the action

        class ActionForm(TransitionalForm):
            \"""
            Transitional Form to add families to an event
            \"""
            model = ModelChoiceField(queryset=Event.objects.all(), required=True)
            boolean = BooleanField()

2. Create and register an action in your ModelAdmin

        @transitional_form(form_class=ActionForm)
        def action(self: ModelAdmin, request: WSGIRequest, selection: QuerySet, form: ActionForm):
            \"""
            Action to apply

            :param request: the request (after the form was send)
            :param selection: the selection from the admin list view
            :param form: the validated form
            \"""
            model = form.cleaned_data["model"]
            boolean = form.cleaned_data["boolean"]

            initial_selection.update(model=model, boolean=boolean)
            messages.success(request, _('The selection has been updated'))


Created by leni on 14/03/2019
"""
from functools import wraps, partial

from django.forms import Form, CharField, HiddenInput
from django.shortcuts import render


class TransitionalForm(Form):
    """
    Form for transition_form decorator

    - action: the action from/for django admin views
    - _selected_action: is as for the django admin actions, the selected fields on admin list
    - _confirm: is use by the transition_form decorator to validate or not the form.
    """
    action = CharField(widget=HiddenInput)
    _confirm = CharField(widget=HiddenInput, required=False, initial="1")
    _selected_action = CharField(widget=HiddenInput)


def transitional_form(func=None, form_class: type = None):
    """
    Decorator to add a transitional form to an action

    The transitional form should inherit TransitionalForm to retrieve selected fields lines
    from django admin view
    :param func: action with the additional validated form
    :type func: Callable[[ModelAdmin, Request, QuerySet, TransitionalForm], Optional[Response]]
    :param form_class: Form class to be transitioned retrieve
    :return: rendered admin/transitional_action.html template or func response
    """
    assert issubclass(form_class, TransitionalForm), "The form_class must inherit from " \
                                                     "TransitionalForm"
    if not func:
        return partial(transitional_form, form_class=form_class)

    @wraps(func)
    def wrapper(self, request, queryset):
        form = form_class(request.POST)
        if "_confirm" not in request.POST:
            form.errors["event"] = {}
        elif form.is_valid():
            return func(self, request, queryset, form)
        return render(
            request, 'admin/transitional_action.html',
            {
                'form': form, "queryset": queryset, "opts": self.opts,
                "action_short_description":
                    getattr(wrapper, "short_description", func.__name__),
                "action_name": func.__name__,
            })
    return wrapper
