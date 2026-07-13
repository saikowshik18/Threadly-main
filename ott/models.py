from django.db import models
from django.conf import settings

class OTTSubscription(models.Model):
    PLATFORM_CHOICES = [
        ('Netflix', 'Netflix'),
        ('Spotify', 'Spotify'),
        ('YouTube Premium', 'YouTube Premium'),
        ('Prime Video', 'Amazon Prime Video'),
        ('Disney+', 'Disney+'),
        ('HBO Max', 'Max / HBO Max'),
        ('Other', 'Other Service'),
    ]

    BILLING_CYCLE_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly'),
        ('One-time', 'One-time'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active (Slots Available)'),
        ('Full', 'Full (No Slots)'),
        ('Closed', 'Closed'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ott_subscriptions')
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES)
    plan_name = models.CharField(max_length=100, help_text="e.g. Premium Ultra HD, Family Plan")
    total_slots = models.PositiveIntegerField(help_text="Total number of members allowed in the group (excluding owner)")
    price_per_slot = models.DecimalField(max_digits=8, decimal_places=2, help_text="Price in USD or local currency per slot")
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='Monthly')
    description = models.TextField(blank=True, help_text="Describe expectations, payment terms, etc.")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_available_slots(self):
        approved_count = self.members.filter(status='Approved').count()
        return max(0, self.total_slots - approved_count)

    def __str__(self):
        return f"{self.platform} ({self.plan_name}) by {self.owner.username}"

class OTTMember(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Approval'),
        ('Approved', 'Approved / Joined'),
        ('Rejected', 'Rejected'),
    ]

    subscription = models.ForeignKey(OTTSubscription, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ott_memberships')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscription', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.subscription.platform} ({self.status})"
