from rest_framework import serializers

class GetConversationSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    conversation_name = serializers.SerializerMethodField()

    def get_conversation_name(self, obj):
        request = self.context.get('request')
        if request is None or not request.user:
            return 'Unknown'

        user = self.context.get('request', {}).user
        for participant in obj.participants.all():
            if participant.id != user.id:
                return participant.username