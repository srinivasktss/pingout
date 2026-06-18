from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Count, Q

# Models
from .models import (
    Conversation, Message
)
from users.models import (
    User
)

# Serializers
from .serializers import (
    GetConversationSerializer, SendMessageSerializer, GetMessagesRequestSerializer,
    GetMessagesResponseSerializer
)

# Utils
from .utils import (
    mark_as_read
)

# Sockets
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class GetConversationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        other_user_id = data.get('user_id', '')

        if not other_user_id:
            return JsonResponse({'detail': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id

        # Check if both have already conversation
        conversation = Conversation.objects.prefetch_related('participants').filter(
            participants=user_id
        ).filter(
            participants=other_user_id
        ).first()

        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(user_id, other_user_id)

        serializers_data = GetConversationSerializer(
            conversation,
            context={'request': request}
        )

        return JsonResponse(serializers_data.data, status=status.HTTP_200_OK)
    

class GetConversationsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        conversations = Conversation.objects.prefetch_related(
            'participants'
        ).annotate(
            unread_msg_count=Count(
                'messages', 
                filter=Q(messages__is_read=False) & ~Q(messages__sender=user)
            )
        ).filter(
            participants=user
        )

        serialized_convs = GetConversationSerializer(
            conversations, 
            context={'request': request}, 
            many=True
        )

        return JsonResponse(serialized_convs.data, safe=False, status=status.HTTP_200_OK)
    
class SendMessageView(APIView):

    permission_classes = [IsAuthenticated]

    channel_layer = get_channel_layer()

    def post(self, request):
        data = request.data
        req_data_serializer = SendMessageSerializer(data=data)

        if not req_data_serializer.is_valid():
            return JsonResponse({'detail': req_data_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        sender = request.user
        validated_data = req_data_serializer.validated_data
        try:
            conversation = Conversation.objects.get(
                id=validated_data['conversation_id'],
                participants=sender
            )
        except Conversation.DoesNotExist:
            return JsonResponse({'detail': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            recipient = conversation.participants.exclude(id=sender.id).get()
        except User.DoesNotExist:
            return JsonResponse({'details': 'Recipient not exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Save to DB first
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=validated_data['content']
        )

        # Send Socket message
        # Send to recipient
        async_to_sync(self.channel_layer.group_send)(
            f'user_{recipient.id}',
            {
                'type': 'new_message',
                'conversation_id': str(conversation.id),
                'from_user': sender.username,
                'to_user': recipient.username,
                'message': message.content
            }
        )

        # Echo to sender
        async_to_sync(self.channel_layer.group_send)(
            f'user_{sender.id}',
            {
                'type': 'new_message',
                'conversation_id': str(conversation.id),
                'from_user': sender.username,
                'to_user': recipient.username,
                'message': message.content
            }
        )


        return JsonResponse({'detail': 'Message sent with'}, status=status.HTTP_200_OK)

class GetMessagesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        req_serializer = GetMessagesRequestSerializer(data=request.query_params)
        if not req_serializer.is_valid():
            return JsonResponse({'details': req_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = req_serializer.validated_data

        try:
            conversation = Conversation.objects.get(
                id=validated_data['conversation_id'],
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return JsonResponse({'details': 'Invalid Conversation'}, status=status.HTTP_400_BAD_REQUEST)

        serialized_res = GetMessagesResponseSerializer(conversation)
        return JsonResponse(serialized_res.data, status=status.HTTP_200_OK)
    

class MarkAsReadView(APIView):

    permission_classes = [IsAuthenticated]
    channel_layer = get_channel_layer()

    def patch(self, request, conversation_id):
        req_serializer = GetMessagesRequestSerializer(data={'conversation_id': conversation_id})
        if not req_serializer.is_valid():
            return JsonResponse({'details': req_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        mark_as_read(conversation_id, request.user)

        recipient_user = request.user
        validated_data = req_serializer.validated_data
        try:
            # Now Send Socket message which tell as read
            conversation = Conversation.objects.prefetch_related(
                'participants'
            ).get(
                id=validated_data['conversation_id'],
                participants=recipient_user
            )
        except Conversation.DoesNotExist:
            return JsonResponse({'details': 'Invalid Conversation'}, status=status.HTTP_400_BAD_REQUEST)

        # Send read in linve
        sender_user = conversation.participants.exclude(id=recipient_user.id).get()
        async_to_sync(self.channel_layer.group_send)(
            f'user_{sender_user.id}',
            {
                'type': 'mark_as_read',
                'conversation_id': str(conversation.id),
            }
        )


        return JsonResponse({'detail': 'Updated Successfully'}, status=status.HTTP_200_OK)
