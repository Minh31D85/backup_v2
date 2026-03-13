from rest_framework import serializers
from .models import PasswordItem

class PasswordItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordItem
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at"
        ]
    
    def validate_group(self, group):
        user = self.context["request"].user

        if group.application.user != user:
            raise serializers.ValidationError("Invalid group")
        
        return group