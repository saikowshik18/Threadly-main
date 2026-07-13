import os
import django

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'threadly.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import StudentProfile
from marketplace.models import Item
from ott.models import OTTSubscription

def seed_database():
    print("Seeding database...")

    # Clear existing seed data
    Item.objects.all().delete()
    OTTSubscription.objects.all().delete()
    # Keep superusers, delete other seeded users if they exist
    User.objects.filter(is_superuser=False).delete()

    # 1. Create Verified Student Users using Django's built-in User model
    students = [
        {
            'username': 'alex_mit',
            'email': 'alex@mit.edu',
            'campus': 'MIT Main Campus',
            'bio': 'Computer Science junior. Looking to share Netflix and clear out old textbook clutter.',
            'avatar_url': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=150&q=80',
            'rating': 4.9
        },
        {
            'username': 'sarah_harvard',
            'email': 'sarah.k@harvard.edu',
            'campus': 'Harvard Yard',
            'bio': 'Biology sophomore. Love sustainable living. Ride a bike everywhere!',
            'avatar_url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80',
            'rating': 4.8
        },
        {
            'username': 'marcus_stanford',
            'email': 'marcus@stanford.edu',
            'campus': 'Stanford West Campus',
            'bio': 'Senior studying MechEng. Selling old project equipment and dorm furniture.',
            'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80',
            'rating': 4.7
        }
    ]

    user_objs = {}
    for student in students:
        # Create Django's built-in User
        user = User.objects.create_user(
            username=student['username'],
            email=student['email'],
            password='studentpassword123',
        )
        # Create associated StudentProfile
        StudentProfile.objects.create(
            user=user,
            campus=student['campus'],
            bio=student['bio'],
            avatar_url=student['avatar_url'],
            rating=student['rating'],
            is_verified=True,
        )
        user_objs[student['username']] = user
        print(f"Created student user: {user.username}")

    # 2. Create Marketplace Items
    items = [
        {
            'owner': user_objs['sarah_harvard'],
            'title': 'Schwinn Cruiser Bicycle - 7 Speed',
            'description': 'Moving off campus and cannot take my bicycle. Gently used for one semester. Comes with a combination cable lock and a front wicker basket. Perfect for Harvard Yard commuting!',
            'category': 'Bicycles',
            'listing_type': 'Sell',
            'price': 120.00,
            'condition': 'Good',
            'image_url': 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=800&q=80'
        },
        {
            'owner': user_objs['alex_mit'],
            'title': 'Sony WH-1000XM4 Noise Canceling Headphones',
            'description': 'Active noise cancellation works perfectly. Great for study sessions in the library. Box and charging cable included. Selling because I upgraded to XM5.',
            'category': 'Electronics',
            'listing_type': 'Sell',
            'price': 145.00,
            'condition': 'Like New',
            'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80'
        },
        {
            'owner': user_objs['marcus_stanford'],
            'title': 'Calculus: Early Transcendentals (8th Edition)',
            'description': 'Required book for Math 51/52. No highlights or markings. Can meet up in White Plaza or Tresidder Union for exchange.',
            'category': 'Books',
            'listing_type': 'Exchange',
            'price': None,
            'condition': 'Like New',
            'image_url': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80'
        },
        {
            'owner': user_objs['sarah_harvard'],
            'title': 'Dorm Desk Lamp with USB Charging Port',
            'description': 'A sleek LED desk lamp with 3 brightness modes and a built-in USB port. Perfect for night studying without waking your roommate.',
            'category': 'Furniture',
            'listing_type': 'Share',
            'price': None,
            'condition': 'Good',
            'image_url': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80'
        },
        {
            'owner': user_objs['marcus_stanford'],
            'title': 'Texas Instruments TI-84 Plus CE Graphing Calculator',
            'description': 'Standard graphing calculator. Screen works perfectly, buttons are responsive, battery holds charge for weeks. Comes with charging brick and cable.',
            'category': 'Lab Equipment',
            'listing_type': 'Rent',
            'price': 10.00,
            'condition': 'Good',
            'image_url': 'https://images.unsplash.com/photo-1628155930542-3c7a64e2c833?auto=format&fit=crop&w=800&q=80'
        },
        {
            'owner': user_objs['alex_mit'],
            'title': 'Ergonomic Mesh Office Desk Chair',
            'description': 'Height adjustable with lumbar support. Mesh back stays cool during long coding marathons. Available for pickup at Tang Hall.',
            'category': 'Furniture',
            'listing_type': 'Sell',
            'price': 60.00,
            'condition': 'Like New',
            'image_url': 'https://images.unsplash.com/photo-1505797149-43b0069ec26b?auto=format&fit=crop&w=800&q=80'
        }
    ]

    for item in items:
        obj = Item.objects.create(
            owner=item['owner'],
            title=item['title'],
            description=item['description'],
            category=item['category'],
            listing_type=item['listing_type'],
            price=item['price'],
            condition=item['condition'],
            image_url=item['image_url'],
            status='Available'
        )
        print(f"Created marketplace item: {obj.title}")

    # 3. Create OTT Subscriptions
    subscriptions = [
        {
            'owner': user_objs['alex_mit'],
            'platform': 'Netflix',
            'plan_name': 'Premium 4K Ultra HD (4 Slots)',
            'total_slots': 3,
            'price_per_slot': 5.50,
            'billing_cycle': 'Monthly',
            'description': 'I have 3 slots open for billing sharing. Monthly payments via Venmo or CashApp. Code/credentials shared on the approved date of payment.'
        },
        {
            'owner': user_objs['sarah_harvard'],
            'platform': 'Spotify',
            'plan_name': 'Premium Family Plan (6 Slots)',
            'total_slots': 5,
            'price_per_slot': 3.00,
            'billing_cycle': 'Monthly',
            'description': 'Looking for 5 students to fill our Spotify family plan. Easy automatic payments setup. I will invite your email address upon verification.'
        },
        {
            'owner': user_objs['marcus_stanford'],
            'platform': 'YouTube Premium',
            'plan_name': 'YouTube Family Plan',
            'total_slots': 4,
            'price_per_slot': 4.00,
            'billing_cycle': 'Monthly',
            'description': 'Split billing. No ads and includes YouTube Music! Send request to join, then pay via Paypal.'
        }
    ]

    for sub in subscriptions:
        obj = OTTSubscription.objects.create(
            owner=sub['owner'],
            platform=sub['platform'],
            plan_name=sub['plan_name'],
            total_slots=sub['total_slots'],
            price_per_slot=sub['price_per_slot'],
            billing_cycle=sub['billing_cycle'],
            description=sub['description'],
            status='Active'
        )
        print(f"Created OTT subscription group: {obj.platform}")

    print("\nDatabase seeded successfully!")
    print("Mock Student login credentials password is 'studentpassword123' for:")
    print(" - alex_mit (alex@mit.edu)")
    print(" - sarah_harvard (sarah.k@harvard.edu)")
    print(" - marcus_stanford (marcus@stanford.edu)")

if __name__ == "__main__":
    seed_database()


# this is kowshik branch