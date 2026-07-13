from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import OTTSubscription, OTTMember
from notifications.utils import create_notification

def ott_list_view(request):
    subscriptions = OTTSubscription.objects.exclude(status='Closed').select_related('owner').order_by('-created_at')
    
    # Platform filter
    platform = request.GET.get('platform', '').strip()
    if platform and platform != 'All':
        subscriptions = subscriptions.filter(platform=platform)

    platforms = [choice[0] for choice in OTTSubscription.PLATFORM_CHOICES]

    context = {
        'subscriptions': subscriptions,
        'platforms': platforms,
        'selected_platform': platform or 'All',
    }
    return render(request, 'ott/ott_list.html', context)

@login_required
def ott_detail_view(request, pk):
    subscription = get_object_or_404(OTTSubscription.objects.select_related('owner'), pk=pk)
    
    # Check current user status
    user_member = OTTMember.objects.filter(subscription=subscription, user=request.user).first()
    
    # Host details (pending and approved members)
    pending_requests = []
    approved_members = []
    if request.user == subscription.owner:
        pending_requests = subscription.members.filter(status='Pending').select_related('user')
        approved_members = subscription.members.filter(status='Approved').select_related('user')
    else:
        approved_members = subscription.members.filter(status='Approved').select_related('user')

    context = {
        'subscription': subscription,
        'user_member': user_member,
        'pending_requests': pending_requests,
        'approved_members': approved_members,
        'available_slots': subscription.get_available_slots(),
    }
    return render(request, 'ott/ott_detail.html', context)

@login_required
def ott_create_view(request):
    errors = {}
    values = {}
    
    if request.method == 'POST':
        platform = request.POST.get('platform', '').strip()
        plan_name = request.POST.get('plan_name', '').strip()
        total_slots = request.POST.get('total_slots', '').strip()
        price_per_slot = request.POST.get('price_per_slot', '').strip()
        billing_cycle = request.POST.get('billing_cycle', '').strip()
        description = request.POST.get('description', '').strip()
        
        values = {
            'platform': platform,
            'plan_name': plan_name,
            'total_slots': total_slots,
            'price_per_slot': price_per_slot,
            'billing_cycle': billing_cycle,
            'description': description,
        }
        
        # Validation checks
        if not platform:
            errors['platform'] = "Platform is required."
        if not plan_name:
            errors['plan_name'] = "Plan name is required."
            
        if not total_slots:
            errors['total_slots'] = "Number of slots is required."
        else:
            try:
                slots_val = int(total_slots)
                if slots_val <= 0:
                    errors['total_slots'] = "You must offer at least 1 slot to share."
            except ValueError:
                errors['total_slots'] = "Number of slots must be a valid integer."
                
        if not price_per_slot:
            errors['price_per_slot'] = "Price per slot is required."
        else:
            try:
                price_val = float(price_per_slot)
                if price_val < 0:
                    errors['price_per_slot'] = "Price per slot cannot be negative."
            except ValueError:
                errors['price_per_slot'] = "Price per slot must be a valid number."
                
        if not billing_cycle:
            errors['billing_cycle'] = "Billing cycle is required."
            
        if not errors:
            sub = OTTSubscription.objects.create(
                owner=request.user,
                platform=platform,
                plan_name=plan_name,
                total_slots=int(total_slots),
                price_per_slot=float(price_per_slot),
                billing_cycle=billing_cycle,
                description=description,
                status='Active'
            )
            messages.success(request, f"Successfully created a subscription share group for {sub.platform}!")
            return redirect('ott_detail', pk=sub.pk)
            
    platforms = OTTSubscription.PLATFORM_CHOICES
    billing_cycles = OTTSubscription.BILLING_CYCLE_CHOICES
    
    return render(request, 'ott/ott_form.html', {
        'errors': errors,
        'values': values,
        'platforms': platforms,
        'billing_cycles': billing_cycles,
    })

@login_required
def ott_request_slot_view(request, pk):
    subscription = get_object_or_404(OTTSubscription, pk=pk)
    if subscription.owner == request.user:
        messages.error(request, "You cannot join your own subscription sharing group.")
        return redirect('ott_detail', pk=pk)

    if subscription.get_available_slots() <= 0:
        messages.error(request, "Sorry, this group is already full.")
        return redirect('ott_detail', pk=pk)

    member, created = OTTMember.objects.get_or_create(subscription=subscription, user=request.user)
    if created:
        messages.success(request, f"Requested to join {subscription.platform} group. Waiting for host approval.")
        # Notify host
        create_notification(
            user=subscription.owner,
            title="New OTT Group Request",
            message=f"{request.user.username} requested a slot in your {subscription.platform} group.",
            link=f"/ott/{subscription.id}/",
            notif_type='OTT'
        )
    else:
        if member.status == 'Rejected':
            # Allow requesting again
            member.status = 'Pending'
            member.save()
            messages.success(request, "Re-submitted slot request.")
            create_notification(
                user=subscription.owner,
                title="OTT Group Request Re-submitted",
                message=f"{request.user.username} re-requested a slot in your {subscription.platform} group.",
                link=f"/ott/{subscription.id}/",
                notif_type='OTT'
            )
        else:
            messages.info(request, "You already have a pending or active request for this subscription.")

    return redirect('ott_detail', pk=pk)

@login_required
def ott_approve_request_view(request, pk):
    member = get_object_or_404(OTTMember.objects.select_related('subscription', 'user'), pk=pk)
    sub = member.subscription

    if sub.owner != request.user:
        messages.error(request, "Unauthorized operation.")
        return redirect('ott_detail', pk=sub.pk)

    if sub.get_available_slots() <= 0:
        messages.error(request, "Cannot approve. No slots available.")
        return redirect('ott_detail', pk=sub.pk)

    member.status = 'Approved'
    member.save()

    # If no slots left, automatically mark subscription Full
    if sub.get_available_slots() == 0:
        sub.status = 'Full'
        sub.save()

    messages.success(request, f"Approved request from {member.user.username}.")
    
    # Notify requestor
    create_notification(
        user=member.user,
        title="OTT Request Approved!",
        message=f"Your request to join {sub.owner.username}'s {sub.platform} group was approved. Contact host to arrange payment.",
        link=f"/ott/{sub.id}/",
        notif_type='OTT'
    )

    return redirect('ott_detail', pk=sub.pk)

@login_required
def ott_reject_request_view(request, pk):
    member = get_object_or_404(OTTMember.objects.select_related('subscription', 'user'), pk=pk)
    sub = member.subscription

    if sub.owner != request.user:
        messages.error(request, "Unauthorized operation.")
        return redirect('ott_detail', pk=sub.pk)

    member.status = 'Rejected'
    member.save()

    messages.success(request, f"Rejected request from {member.user.username}.")
    
    # Notify requestor
    create_notification(
        user=member.user,
        title="OTT Request Declined",
        message=f"Your request to join {sub.owner.username}'s {sub.platform} group was declined.",
        link=f"/ott/{sub.id}/",
        notif_type='OTT'
    )

    return redirect('ott_detail', pk=sub.pk)
