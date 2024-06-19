from django.db import models
from login.models import CustomUser as User
from django.utils import timezone
import string
import random
class DiscountCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.FloatField()
    max_uses = models.IntegerField()
    expiry_date = models.DateTimeField()
    roles_allowed = models.ManyToManyField(User, related_name='discount_codes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    custom = models.BooleanField(default=False) # when True, code is entered by admin
    uses = models.IntegerField(default=0)

    def is_valid(self):
        if self.uses >= self.max_uses:
            return False
        if self.expiry_date < timezone.now():
            return False
        return True

    def save(self, *args, **kwargs):
        if not self.custom:
            self.code = self.generate_random_code()
        super().save(*args, **kwargs)

    def generate_random_code(self):
        length = 10 # length of the code
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def __str__(self):
        return self.code
