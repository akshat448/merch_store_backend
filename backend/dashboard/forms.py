from django import forms
from discounts.models import DiscountCode

class DiscountCodeForm(forms.ModelForm):
    class Meta:
        model = DiscountCode
        fields = ['code', 'discount_percentage', 'max_uses', 'expiry_date', 'roles_allowed', 'custom']
