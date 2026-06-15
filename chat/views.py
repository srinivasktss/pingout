from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

# Models
from .models import Conversation

# Serializers
from .serializers import GetConversationSerializer

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
