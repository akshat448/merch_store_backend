from rest_framework import serializers
from .models import CustomUser

USER_POSITION_CHOICES = [
    ('MB', 'Member'),
    ('CR', 'Core'),
    ('JS', 'Joint Secretary'),
    ('FS', 'Finance Secretary'),
    ('GS', 'General Secretary'),
]


class UserSerializer(serializers.ModelSerializer):
    position_text = serializers.SerializerMethodField()

    def get_position_text(self, obj):
        for position_code, position_name in USER_POSITION_CHOICES:
            if obj.position == position_code:
                return position_name
        return "Member"
    
    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'phone_no', 'position', 'position_text')
