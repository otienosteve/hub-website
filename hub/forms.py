from django import forms

from .models import Subscriber


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["name", "email", "wants_membership"]

    def validate_unique(self):
        # Re-subscribing with the same email should update, not error.
        pass
