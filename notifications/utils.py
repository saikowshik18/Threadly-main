from .models import Notification

def create_notification(user, title, message, link=None, notif_type='System'):
    """
    Creates and saves a notification for a user.
    """
    try:
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            link=link,
            notification_type=notif_type
        )
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None
