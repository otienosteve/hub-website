from django import forms

from .models import CourseApplication, Subscriber


class CourseApplicationForm(forms.ModelForm):
    class Meta:
        model = CourseApplication
        fields = [
            "first_name", "last_name", "email", "phone_number", "county",
            "current_occupation", "institution_company", "python_proficiency",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone_number": forms.TelInput(attrs={"autocomplete": "tel"}),
            "county": forms.TextInput(attrs={"autocomplete": "address-level1"}),
            "current_occupation": forms.TextInput(),
            "institution_company": forms.TextInput(),
            "python_proficiency": forms.Select(),
        }


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["name", "email", "wants_membership"]

    def validate_unique(self):
        # Re-subscribing with the same email should update, not error.
        pass
