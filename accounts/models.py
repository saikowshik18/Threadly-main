from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    campus = models.CharField(max_length=100, default='Main Campus')
    avatar_url = models.URLField(blank=True, default='')
    rating = models.FloatField(default=5.0)

    @property
    def unread_notifications_count(self):
        return self.user.notifications.filter(is_read=False).count()

    @property
    def unread_messages_count(self):
        from chat.models import Message
        # Messages sent to rooms where user is participant, which are unread and not sent by user themselves
        return Message.objects.filter(room__buyer=self.user, is_read=False).exclude(sender=self.user).count() + \
               Message.objects.filter(room__seller=self.user, is_read=False).exclude(sender=self.user).count()

    def __str__(self):
        return f"Profile of {self.user.username}"


# Inject rating property to built-in User model for easy template access
def get_user_rating(self):
    try:
        return self.profile.rating
    except Exception:
        return 5.0

User.add_to_class('rating', property(get_user_rating))
