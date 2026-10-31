from datetime import date
from django import forms
from .models import Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["couple_name", "phone", "email", "source", "tentative_date",
                  "guest_count", "theme", "max_budget", "package", "notes"]
        widgets = {"tentative_date": forms.DateInput(attrs={"type": "date"})}

    def clean_tentative_date(self):
        d = self.cleaned_data["tentative_date"]
        if d < date.today():
            raise forms.ValidationError("The wedding date cannot be in the past.")
        return d

    def clean_phone(self):
        p = self.cleaned_data["phone"].replace(" ", "")
        if not p.lstrip("+").isdigit() or len(p) < 10:
            raise forms.ValidationError("Enter a valid phone number (at least 10 digits).")
        return p