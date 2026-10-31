from datetime import date
from django import forms
from .models import ExtraCharge, Lead


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


class ExtraChargeForm(forms.ModelForm):
    class Meta:
        model = ExtraCharge
        fields = [
            "wedding_vendor",
            "description",
            "quantity",
            "client_unit_price",
            "vendor_unit_cost",
        ]

    def __init__(self, *args, wedding=None, **kwargs):
        super().__init__(*args, **kwargs)
        if wedding is not None:
            self.fields["wedding_vendor"].queryset = wedding.vendors.all()
        self.fields["wedding_vendor"].required = False
        self.fields["vendor_unit_cost"].required = False



class ExtraChargeForm(forms.ModelForm):
    class Meta:
        model = ExtraCharge
        fields = [
            "wedding_vendor",
            "description",
            "quantity",
            "client_unit_price",
            "vendor_unit_cost",
        ]

    def __init__(self, *args, wedding=None, **kwargs):
        super().__init__(*args, **kwargs)
        if wedding is not None:
            self.fields["wedding_vendor"].queryset = wedding.vendors.all()
        self.fields["wedding_vendor"].required = False
        self.fields["vendor_unit_cost"].required = False