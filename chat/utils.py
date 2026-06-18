
from .models import Conversation

def mark_as_read(conversation_id, recipient_user):

    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            participants=recipient_user
        )
    except Conversation.DoesNotExist:
        print('No conversation exits')
        return
    
    # Update this conversation messages are read by the recipient
    conversation.messages.exclude(
        sender=recipient_user
    ).filter(
        is_read=False
    ).update(
        is_read=True
    )