from django.db import models
from django.conf import settings

class Item(models.Model):
    CATEGORY_CHOICES = [
        ('Books', 'Books & Study Material'),
        ('Electronics', 'Electronics & Gadgets'),
        ('Bicycles', 'Bicycles & Transport'),
        ('Lab Equipment', 'Lab Equipment & Tools'),
        ('Furniture', 'Furniture & Decor'),
        ('Essentials', 'Other Essentials'),
    ]

    LISTING_TYPE_CHOICES = [
        ('Sell', 'For Sale'),
        ('Rent', 'For Rent'),
        ('Exchange', 'For Exchange'),
        ('Share', 'Free / Share'),
    ]

    CONDITION_CHOICES = [
        ('New', 'Brand New'),
        ('Like New', 'Like New / Mint'),
        ('Good', 'Good / Gently Used'),
        ('Fair', 'Fair / Shows Wear'),
        ('Poor', 'Poor / Heavy Wear'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Sold', 'Sold'),
        ('Rented', 'Rented'),
        ('Inactive', 'Inactive'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases')
    title = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Leave blank if Exchange or Share")
    condition = models.CharField(max_length=15, choices=CONDITION_CHOICES)
    image = models.ImageField(upload_to='listings/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Optional external image URL for demo seeding")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        # Default category illustrations/photos
        defaults = {
            'Books': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80',
            'Electronics': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?auto=format&fit=crop&w=600&q=80',
            'Bicycles': 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80',
            'Lab Equipment': 'https://images.unsplash.com/photo-1576086213369-97a306d36557?auto=format&fit=crop&w=600&q=80',
            'Furniture': 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=600&q=80',
            'Essentials': 'https://images.unsplash.com/photo-1517502884422-41eaaced0168?auto=format&fit=crop&w=600&q=80',
        }
        return defaults.get(self.category, 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80')

    def __str__(self):
        return f"{self.title} - {self.listing_type} ({self.status})"

class SavedItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item')

    def __str__(self):
        return f"{self.user.username} saved {self.item.title}"
