"""
horilla_automations/forms.py
"""

from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from base.forms import ModelForm
from employee.filters import EmployeeFilter
from employee.models import Employee
from horilla_automations.methods.methods import generate_choices
from horilla_automations.models import MODEL_CHOICES, MailAutomation
from horilla_widgets.forms import default_select_option_template
from horilla_widgets.widgets.horilla_multi_select_field import HorillaMultiSelectField
from horilla_widgets.widgets.select_widgets import HorillaMultiSelectWidget


class AutomationForm(ModelForm):
    """
    AutomationForm
    """

    condition_html = forms.CharField(widget=forms.HiddenInput())
    condition_querystring = forms.CharField(widget=forms.HiddenInput())

    cols = {"template_attachments": 12}

    class Meta:
        model = MailAutomation
        fields = "__all__"

    def _get_model_choices(self):
        """
        Get model choices, populating them if they're empty
        This method ensures we always return the full MODEL_CHOICES list
        """
        # First, try to get the choices from the global variable
        if MODEL_CHOICES:
            # Remove duplicates while preserving order
            unique_choices = []
            seen = set()
            for choice in MODEL_CHOICES:
                if choice[0] not in seen:
                    unique_choices.append(choice)
                    seen.add(choice[0])
            return unique_choices
        
        # Fallback: If MODEL_CHOICES is empty, populate it manually
        # This should rarely happen as apps.py should populate it on startup
        print("Warning: MODEL_CHOICES is empty, attempting manual population")
        
        choices = []
        try:
            from base.templatetags.horillafilters import app_installed
            from employee.models import Employee
            from horilla_automations.methods.methods import get_related_models

            # Check if recruitment is installed
            recruitment_installed = False
            if app_installed("recruitment"):
                recruitment_installed = True

            models = [Employee]
            if recruitment_installed:
                try:
                    from recruitment.models import Candidate
                    models.append(Candidate)
                except ImportError:
                    pass

            # Get all related models for each main model
            for main_model in models:
                try:
                    related_models = get_related_models(main_model)
                    for model in related_models:
                        path = f"{model.__module__}.{model.__name__}"
                        choices.append((path, model.__name__))
                except Exception as e:
                    print(f"Error getting related models for {main_model}: {e}")
                    
            # Add the standard choices
            choices.append(("employee.models.Employee", "Employee"))
            choices.append(("pms.models.EmployeeKeyResult", "Employee Key Results"))
            
        except Exception as e:
            print(f"Error populating MODEL_CHOICES manually: {e}")
            # Minimal fallback
            choices = [
                ("employee.models.Employee", "Employee"),
                ("pms.models.EmployeeKeyResult", "Employee Key Results"),
            ]
        
        # Remove duplicates and return
        unique_choices = []
        seen = set()
        for choice in choices:
            if choice[0] not in seen:
                unique_choices.append(choice)
                seen.add(choice[0])
        
        return unique_choices

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Field: also_sent_to ---
        self.fields["also_sent_to"] = HorillaMultiSelectField(
            queryset=Employee.objects.all(),
            required=False,
            widget=HorillaMultiSelectWidget(
                filter_route_name="employee-widget-filter",
                filter_class=EmployeeFilter,
                filter_instance_contex_name="f",
                filter_template_path="employee_filters.html",
                instance=self.instance,
            ),
            label="Also Sent to",
            help_text=_("The employees selected here will receive the email as Cc."),
        )

        # --- Determine model for generate_choices ---
        model = getattr(self.instance, "model", None) or self.data.get("model")
        mail_to, mail_details_choice = [], []

        if model:
            choices = generate_choices(model)
            mail_to, mail_details_choice = choices[0], choices[1]

        # --- Field: mail_to ---
        self.fields["mail_to"] = forms.MultipleChoiceField(
            choices=mail_to,
            initial=self.data.get("mail_to"),
            widget=forms.SelectMultiple(attrs={"class": "oh-select oh-select-2 w-100"}),
        )

        # --- Field: mail_details ---
        self.fields["mail_details"] = forms.ChoiceField(
            choices=mail_details_choice,
            help_text=_(
                "Fill mail template details (receiver/instance, `self` will be the person who triggers the automation)"
            ),
        )
        self.fields["mail_details"].widget.attrs = {
            "class": "oh-select oh-select-2 w-100"
        }

        # --- Field: model ---
        # Ensure MODEL_CHOICES is populated
        model_choices = self._get_model_choices()
        
        # Debug logging
        print(f"AutomationForm: Found {len(model_choices)} model choices")
        if len(model_choices) > 0:
            print(f"First few choices: {model_choices[:3]}")
        
        self.fields["model"].choices = [("", "Select model")] + model_choices
        self.fields["model"].widget.attrs["onchange"] = "getToMail($(this))"

        # --- Field: mail_template ---
        self.fields["mail_template"].empty_label = "----------"

        # --- Field: condition fields ---
        self.fields["condition"].initial = getattr(
            self.instance, "condition", None
        ) or self.data.get("condition")
        self.fields["condition_html"].initial = getattr(
            self.instance, "condition_html", None
        ) or self.data.get("condition_html")
        self.fields["condition_querystring"].initial = getattr(
            self.instance, "condition", None
        ) or self.data.get("condition_html")

        # --- Apply option template name for all select fields ---
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.option_template_name = default_select_option_template

        # --- Re-insert is_active field to ensure order ---
        self.fields["is_active"] = self.fields.pop("is_active")

    def clean(self):
        cleaned_data = super().clean()
        if isinstance(self.fields["also_sent_to"], HorillaMultiSelectField):
            self.errors.pop("also_sent_to", None)

            employee_data = self.fields["also_sent_to"].queryset.filter(
                id__in=self.data.getlist("also_sent_to")
            )
            cleaned_data["also_sent_to"] = employee_data

        return cleaned_data

    def save(self, commit: bool = ...) -> Any:
        self.instance: MailAutomation = self.instance
        condition_querystring = self.cleaned_data["condition_querystring"]
        condition_html = self.cleaned_data["condition_html"]
        mail_to = self.data.getlist("mail_to")
        self.instance.mail_to = str(mail_to)
        self.instance.mail_details = self.data["mail_details"]
        self.instance.condition_querystring = condition_querystring
        self.instance.condition_html = condition_html
        return super().save(commit)
