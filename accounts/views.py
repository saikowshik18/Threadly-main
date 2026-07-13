import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .models import StudentProfile
from marketplace.models import Item, SavedItem
from ott.models import OTTSubscription, OTTMember


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    errors = {}
    values = {}

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        campus = request.POST.get('campus', '').strip()
        bio = request.POST.get('bio', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        values = {'username': username, 'email': email, 'campus': campus, 'bio': bio}

        # Validation checks
        if not username:
            errors['username'] = "Username is required."
        elif User.objects.filter(username__iexact=username).exists():
            errors['username'] = "A user with this username already exists."

        if not email:
            errors['email'] = "Email is required."
        elif not any(email.endswith(dom) for dom in ['.edu', 'rguktrkv.ac.in']):
            errors['email'] = "Only verified students with a valid institutional email (.edu or rguktrkv.ac.in) can register."
        elif User.objects.filter(email__iexact=email).exists():
            errors['email'] = "A user with this email already exists."

        if not password:
            errors['password'] = "Password is required."

        if password != confirm_password:
            errors['confirm_password'] = "Passwords do not match."

        if not errors:
            otp = f"{random.randint(100000, 999999)}"
            signup_data = {
                'username': username,
                'email': email,
                'campus': campus or 'Main Campus',
                'bio': bio,
                'password': make_password(password),
            }
            request.session['signup_data'] = signup_data
            request.session['signup_otp'] = otp
            request.session['signup_email'] = email

            # Always print OTP to terminal for debugging
            print(f"\n{'='*50}")
            print(f"  OTP for {email}: {otp}")
            print(f"{'='*50}\n")

            try:
                send_mail(
                    subject="Verify your Threadly Account",
                    message=f"Hi {username},\n\nWelcome to Threadly! Your 6-digit verification code is: {otp}\n\nShare More. Spend Less. Waste Less.\n\n- The Threadly Team",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.info(request, f"Verification code sent to {email}. Check your inbox (and spam folder).")
            except Exception as e:
                print(f"EMAIL ERROR: {e}")
                messages.warning(request, f"Email delivery failed ({e}). Use the code printed in your terminal.")

            return redirect('verify_email')



    return render(request, 'accounts/signup.html', {'errors': errors, 'values': values})


def verify_email_view(request):
    signup_data = request.session.get('signup_data')
    signup_otp = request.session.get('signup_otp')
    signup_email = request.session.get('signup_email')

    if not signup_data or not signup_otp or not signup_email:
        messages.error(request, "Invalid verification session. Please sign up first.")
        return redirect('signup')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if code == signup_otp:
            try:
                # Create Django built-in User
                user = User(
                    username=signup_data['username'],
                    email=signup_data['email'],
                    password=signup_data['password'],  # already hashed
                )
                user.save()

                # Create StudentProfile with campus-specific fields
                StudentProfile.objects.create(
                    user=user,
                    campus=signup_data['campus'],
                    bio=signup_data['bio'],
                    is_verified=True,
                )

                # Log user in using Django's default backend
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                # Clear session keys
                del request.session['signup_data']
                del request.session['signup_otp']
                del request.session['signup_email']

                messages.success(request, f"Welcome to Threadly, {user.username}! Your account has been verified.")
                return redirect('home')
            except Exception as e:
                messages.error(request, f"An error occurred while creating your account: {e}")
        else:
            messages.error(request, "Invalid verification code. Please try again.")

    return render(request, 'accounts/verify_email.html', {'user_email': signup_email})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    error = None
    username_val = ''

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        username_val = username_or_email

        username = username_or_email
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                pass

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            error = "Invalid username/email or password."

    return render(request, 'accounts/login.html', {'error': error, 'username_val': username_val})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    active_listings = Item.objects.filter(owner=user, status='Available').order_by('-created_at')
    completed_listings = Item.objects.filter(owner=user).exclude(status='Available').order_by('-created_at')
    saved = SavedItem.objects.filter(user=user).select_related('item').order_by('-created_at')
    ott_owned = OTTSubscription.objects.filter(owner=user).order_by('-created_at')
    ott_joined = OTTMember.objects.filter(user=user, status='Approved').select_related('subscription')

    context = {
        'profile_user': user,
        'active_listings': active_listings,
        'completed_listings': completed_listings,
        'saved_items': saved,
        'ott_owned': ott_owned,
        'ott_joined': ott_joined,
        'is_own_profile': True,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    user = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        profile.campus = request.POST.get('campus', '').strip()
        profile.bio = request.POST.get('bio', '').strip()
        profile.avatar_url = request.POST.get('avatar_url', '').strip()
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'accounts/edit_profile.html')


def public_profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    active_listings = Item.objects.filter(owner=profile_user, status='Available').order_by('-created_at')
    completed_listings = Item.objects.filter(owner=profile_user).exclude(status='Available').order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'active_listings': active_listings,
        'completed_listings': completed_listings,
        'is_own_profile': request.user.is_authenticated and (request.user == profile_user),
    }
    return render(request, 'accounts/profile.html', context)
