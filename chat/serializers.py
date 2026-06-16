from rest_framework import serializers

# Models
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'content', 'is_read', 'created_at']

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
            
class SendMessageSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField()
    content = serializers.CharField()

class GetMessagesRequestSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField()

class GetMessagesResponseSerializer(serializers.Serializer):
    participants = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()

    def get_participants(self, obj):
        return {str(p.id): p.username for p in obj.participants.all()}
    
    def get_messages(self, obj):
        msgs = obj.messages.select_related('sender').all()
        return MessageSerializer(msgs, many=True).data