from django.db import models
from django.conf import settings
from marketplace.models import Item

class ChatRoom(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='chat_rooms')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_chats')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_chats')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('item', 'buyer', 'seller')

    def __str__(self):
        return f"Chat for {self.item.title} (Buyer: {self.buyer.username})"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Msg from {self.sender.username} at {self.timestamp}"
