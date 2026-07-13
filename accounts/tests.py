from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import StudentProfile

class StudentAuthTests(TestCase):
    def test_create_user_with_profile(self):
        user = User.objects.create_user(
            username="test_student",
            email="test@college.edu",
            password="secure_password123",
        )
        profile = StudentProfile.objects.create(
            user=user,
            campus="Main Campus",
            is_verified=False,
        )
        self.assertEqual(user.username, "test_student")
        self.assertEqual(user.email, "test@college.edu")
        self.assertFalse(profile.is_verified)
        self.assertEqual(profile.campus, "Main Campus")

    def test_signup_view_valid_email(self):
        response = self.client.post(reverse('signup'), {
            'username': 'jane_doe',
            'email': 'jane.doe@univ.edu',
            'campus': 'North Campus',
            'bio': 'Test bio',
            'password': 'mypassword123',
            'confirm_password': 'mypassword123'
        })
        self.assertRedirects(response, reverse('verify_email'))
        self.assertIn('signup_data', self.client.session)

    def test_signup_view_invalid_email(self):
        response = self.client.post(reverse('signup'), {
            'username': 'jane_doe',
            'email': 'jane.doe@gmail.com',
            'campus': 'North Campus',
            'bio': 'Test bio',
            'password': 'mypassword123',
            'confirm_password': 'mypassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('errors', response.context)
        self.assertIn("Only verified students with a valid institutional email (.edu or rguktrkv.ac.in) can register.", response.context['errors']['email'])

    def test_signup_view_rguktrkv_email(self):
        response = self.client.post(reverse('signup'), {
            'username': 'ram_rgukt',
            'email': 'r210105@rguktrkv.ac.in',
            'campus': 'RGUKT RK Valley',
            'bio': 'Seeded user bio',
            'password': 'mypassword123',
            'confirm_password': 'mypassword123'
        })
        self.assertRedirects(response, reverse('verify_email'))
        self.assertIn('signup_data', self.client.session)

    def test_email_verification_flow(self):
        from django.contrib.auth.hashers import make_password
        session = self.client.session
        session['signup_data'] = {
            'username': 'verify_test',
            'email': 'verify@college.edu',
            'campus': 'Main Campus',
            'bio': '',
            'password': make_password('testpass123'),
        }
        session['signup_otp'] = '123456'
        session['signup_email'] = 'verify@college.edu'
        session.save()

        response = self.client.post(reverse('verify_email'), {'code': '123456'})
        self.assertRedirects(response, reverse('home'))
        # Verify user and profile were created
        user = User.objects.get(username='verify_test')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertTrue(user.profile.is_verified)

class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profile_test_user",
            email="test@univ.edu",
            password="testpassword123"
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            campus="Main Campus",
            rating=4.5,
            is_verified=True
        )
        from marketplace.models import Item
        # Create active item
        self.active_item = Item.objects.create(
            owner=self.user,
            title="Active Item Test",
            description="Active Item Description",
            category="Books",
            listing_type="Sell",
            price=15.00,
            condition="Good",
            status="Available"
        )
        # Create completed item
        self.completed_item = Item.objects.create(
            owner=self.user,
            title="Completed Item Test",
            description="Completed Item Description",
            category="Electronics",
            listing_type="Sell",
            price=25.00,
            condition="Like New",
            status="Sold"
        )

    def test_user_rating_property(self):
        self.assertEqual(self.user.rating, 4.5)
        # Check fallback when profile does not exist
        user_no_profile = User.objects.create_user(
            username="no_profile",
            email="noprof@univ.edu",
            password="testpassword123"
        )
        self.assertEqual(user_no_profile.rating, 5.0)

    def test_profile_view_lists_completed_and_active_listings(self):
        self.client.login(username="profile_test_user", password="testpassword123")
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Item Test")
        self.assertContains(response, "Completed Item Test")
        self.assertContains(response, "Completed Listings")
        self.assertContains(response, "Post A Listing")
