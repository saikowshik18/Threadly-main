from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Render view first, then mark as read
    context = {
        'notifications': notifications,
    }
    
    # Mark all notifications for this user as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'notifications/notification_list.html', context)
