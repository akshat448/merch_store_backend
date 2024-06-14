from django.contrib import admin
from .models import DiscountCode

class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'max_uses', 'uses', 'expiry_date', 'custom')
    search_fields = ('code',)
    list_filter = ('expiry_date', 'custom')

admin.site.register(DiscountCode, DiscountCodeAdmin)
