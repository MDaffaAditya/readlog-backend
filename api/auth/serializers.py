from rest_framework import serializers
from member.models import User


class UserDetailsSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
        )
        read_only_fields = ("id", "username", "email", "full_name")