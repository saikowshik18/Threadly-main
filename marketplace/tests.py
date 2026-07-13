from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import StudentProfile
from .models import Item

class MarketplaceDealTests(TestCase):
    def setUp(self):
        # Create seller
        self.seller = User.objects.create_user(
            username="seller_user",
            email="seller@univ.edu",
            password="password123"
        )
        StudentProfile.objects.create(
            user=self.seller,
            campus="Main Campus",
            is_verified=True
        )

        # Create buyer
        self.buyer = User.objects.create_user(
            username="buyer_user",
            email="buyer@univ.edu",
            password="password123"
        )
        StudentProfile.objects.create(
            user=self.buyer,
            campus="West Campus",
            is_verified=True
        )

        # Create available item
        self.item = Item.objects.create(
            owner=self.seller,
            title="Calculus Textbook",
            description="Good condition",
            category="Books",
            listing_type="Sell",
            price=20.00,
            condition="Good",
            status="Available"
        )

    def test_complete_deal_success(self):
        self.client.login(username="seller_user", password="password123")
        url = reverse('item_complete', kwargs={'pk': self.item.pk})
        
        response = self.client.post(url, {
            'buyer_id': self.buyer.id,
            'final_price': '18.50'
        })
        
        # Verify redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify database changes
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, 'Sold')
        self.assertEqual(self.item.buyer, self.buyer)
        self.assertEqual(float(self.item.price), 18.50)

    def test_complete_deal_not_owner(self):
        self.client.login(username="buyer_user", password="password123")
        url = reverse('item_complete', kwargs={'pk': self.item.pk})
        
        response = self.client.post(url, {
            'buyer_id': self.buyer.id,
            'final_price': '18.50'
        })
        
        # Verify redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify no database changes
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, 'Available')
        self.assertIsNone(self.item.buyer)
        self.assertEqual(float(self.item.price), 20.00)

    def test_item_detail_displays_sold_info(self):
        # Set item as sold
        self.item.status = 'Sold'
        self.item.buyer = self.buyer
        self.item.price = 15.00
        self.item.save()

        # Request item detail page
        response = self.client.get(reverse('item_detail', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sold to")
        self.assertContains(response, "buyer_user")
        self.assertContains(response, "$15.00")
