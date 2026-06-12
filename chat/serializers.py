from rest_framework import serializers

class GetConverstaionSerializer(serializers.Serializer):
    id = serializers.UUIDField()