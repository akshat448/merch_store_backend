from django.db import models
from login.models import CustomUser as User
from django.utils import timezone

class DiscountCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.FloatField()
    max_uses = models.IntegerField()
    expiry_date = models.DateTimeField()
    roles_allowed = models.ManyToManyField(User, related_name='discount_codes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    custom = models.BooleanField(default=False)
    uses = models.IntegerField(default=0)

    def is_valid(self):
        if self.uses >= self.max_uses:
            return False
        if self.expiry_date < timezone.now():
            return False
        return True

    def __str__(self):
        return self.code
