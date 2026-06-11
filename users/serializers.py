from rest_framework import serializers

class UserSearchSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)