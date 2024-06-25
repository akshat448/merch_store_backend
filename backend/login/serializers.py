from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """position = serializers.SerializerMethodField()

    def get_position(self, obj):
        return obj.position"""

    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'phone_no', 'position')
