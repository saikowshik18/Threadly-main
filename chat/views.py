from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q
from marketplace.models import Item
from .models import ChatRoom, Message
from notifications.utils import create_notification

@login_required
@require_POST
def chat_start_view(request, item_pk):
    item = get_object_or_404(Item, pk=item_pk)
    if item.owner == request.user:
        messages.error(request, "You cannot start a chat with yourself regarding your own item.")
        return redirect('item_detail', pk=item_pk)

    # Find or create chat room
    room, created = ChatRoom.objects.get_or_create(
        item=item,
        buyer=request.user,
        seller=item.owner
    )
    return redirect('chat_room', pk=room.pk)

@login_required
def inbox_view(request):
    # Fetch rooms where user is buyer or seller
    rooms = ChatRoom.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('item', 'buyer', 'seller').order_by('-created_at')

    # Annotate last message for display
    rooms_data = []
    for r in rooms:
        last_msg = r.messages.order_by('-timestamp').first()
        other_user = r.seller if r.buyer == request.user else r.buyer
        
        # Calculate unread count for this specific room
        unread_count = r.messages.filter(is_read=False).exclude(sender=request.user).count()

        rooms_data.append({
            'room': r,
            'other_user': other_user,
            'last_message': last_msg,
            'unread_count': unread_count
        })

    # Sort rooms by last message timestamp if available
    rooms_data.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else x['room'].created_at,
        reverse=True
    )

    return render(request, 'chat/inbox.html', {'rooms_data': rooms_data})

@login_required
def chat_room_view(request, pk):
    room = get_object_or_404(ChatRoom.objects.select_related('item', 'buyer', 'seller'), pk=pk)
    
    # Check access permission
    if request.user != room.buyer and request.user != room.seller:
        return HttpResponseForbidden("You are not authorized to access this conversation.")

    # Mark incoming messages as read
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    messages_list = room.messages.all().select_related('sender')
    other_user = room.seller if room.buyer == request.user else room.buyer

    # Get sidebar rooms list for inbox style dashboard layout
    sidebar_rooms = ChatRoom.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('item', 'buyer', 'seller')

    sidebar_data = []
    for r in sidebar_rooms:
        last_msg = r.messages.order_by('-timestamp').first()
        oth = r.seller if r.buyer == request.user else r.buyer
        unread = r.messages.filter(is_read=False).exclude(sender=request.user).count()
        sidebar_data.append({
            'room': r,
            'other_user': oth,
            'last_message': last_msg,
            'unread_count': unread
        })
    sidebar_data.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else x['room'].created_at,
        reverse=True
    )

    context = {
        'room': room,
        'other_user': other_user,
        'messages_list': messages_list,
        'sidebar_data': sidebar_data,
        'last_message_id': messages_list.last().id if messages_list.exists() else 0,
    }
    return render(request, 'chat/room.html', context)

@login_required
@require_POST
def send_message_view(request, pk):
    room = get_object_or_404(ChatRoom, pk=pk)
    if request.user != room.buyer and request.user != room.seller:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Save message
    msg = Message.objects.create(
        room=room,
        sender=request.user,
        content=content
    )

    # Create notification for recipient
    recipient = room.seller if room.buyer == request.user else room.buyer
    create_notification(
        user=recipient,
        title=f"New Chat Message",
        message=f"{request.user.username}: {content[:50]}...",
        link=f"/chat/room/{room.id}/",
        notif_type='Chat'
    )

    return JsonResponse({
        'success': True,
        'message': {
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%b %d, %H:%M'),
            'sender_username': msg.sender.username,
        }
    })

@login_required
def poll_messages_view(request, pk):
    room = get_object_or_404(ChatRoom, pk=pk)
    if request.user != room.buyer and request.user != room.seller:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    last_id = request.GET.get('last_id', '0')
    try:
        last_id = int(last_id)
    except ValueError:
        last_id = 0

    new_messages = room.messages.filter(id__gt=last_id).select_related('sender')
    
    # Mark messages from the other user as read
    new_messages.exclude(sender=request.user).update(is_read=True)

    messages_data = []
    for m in new_messages:
        messages_data.append({
            'id': m.id,
            'content': m.content,
            'timestamp': m.timestamp.strftime('%b %d, %H:%M'),
            'sender_username': m.sender.username,
            'is_self': m.sender == request.user
        })

    return JsonResponse({
        'messages': messages_data,
        'last_message_id': new_messages.last().id if new_messages.exists() else last_id
    })
