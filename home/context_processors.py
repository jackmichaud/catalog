from home.models import Message

def unread_messages(request):
    """
    Context processor to provide unread message count globally in templates.
    """
    if request.user.is_authenticated:
        # Count messages where user is a participant but hasn't read them and isn't the sender
        unread_count = Message.objects.filter(
            conversation__participants=request.user
        ).exclude(
            sender=request.user
        ).exclude(
            read_by=request.user
        ).count()
        
        return {'unread_message_count': unread_count}
    return {'unread_message_count': 0}
