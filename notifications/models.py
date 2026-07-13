from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPE_CHOICES = [
        ('Chat', 'Chat Message'),
        ('OTT', 'OTT Group Update'),
        ('System', 'System Notification'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True, help_text="Redirect path when clicked")
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='System')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title} (Read: {self.is_read})"
