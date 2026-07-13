from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Item, SavedItem

def home_view(request):
    # Fetch available listings
    items = Item.objects.filter(status='Available').select_related('owner').order_by('-created_at')

    # Apply Search Query
    q = request.GET.get('q', '').strip()
    if q:
        items = items.filter(Q(title__icontains=q) | Q(description__icontains=q))

    # Apply Filters
    category = request.GET.get('category', '').strip()
    if category and category != 'All':
        items = items.filter(category=category)

    listing_type = request.GET.get('type', '').strip()
    if listing_type:
        items = items.filter(listing_type=listing_type)

    condition = request.GET.get('condition', '').strip()
    if condition:
        items = items.filter(condition=condition)

    min_price = request.GET.get('min_price', '').strip()
    if min_price:
        try:
            items = items.filter(price__gte=float(min_price))
        except ValueError:
            pass

    max_price = request.GET.get('max_price', '').strip()
    if max_price:
        try:
            items = items.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Sort Listings
    sort = request.GET.get('sort', '').strip()
    if sort == 'price_asc':
        items = items.order_by('price')
    elif sort == 'price_desc':
        items = items.order_by('-price')
    elif sort == 'oldest':
        items = items.order_by('created_at')

    # Get saved item IDs for current user to show solid bookmark icons
    saved_ids = []
    if request.user.is_authenticated:
        saved_ids = SavedItem.objects.filter(user=request.user).values_list('item_id', flat=True)

    categories = Item.CATEGORY_CHOICES
    listing_types = Item.LISTING_TYPE_CHOICES
    conditions = Item.CONDITION_CHOICES

    context = {
        'items': items,
        'categories': categories,
        'listing_types': listing_types,
        'conditions': conditions,
        'saved_ids': saved_ids,
        'selected_category': category or 'All',
        'selected_type': listing_type,
        'selected_condition': condition,
        'min_price': min_price,
        'max_price': max_price,
        'q': q,
        'sort': sort,
    }
    return render(request, 'marketplace/home.html', context)

def item_detail_view(request, pk):
    item = get_object_or_404(Item.objects.select_related('owner'), pk=pk)
    
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedItem.objects.filter(user=request.user, item=item).exists()

    # Recommendations (same category, excluding current item)
    recommendations = Item.objects.filter(category=item.category, status='Available').exclude(pk=item.pk)[:4]

    context = {
        'item': item,
        'is_saved': is_saved,
        'recommendations': recommendations,
    }
    return render(request, 'marketplace/item_detail.html', context)

@login_required
def item_create_view(request):
    errors = {}
    values = {}
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '').strip()
        listing_type = request.POST.get('listing_type', '').strip()
        price = request.POST.get('price', '').strip()
        condition = request.POST.get('condition', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        image = request.FILES.get('image')
        
        values = {
            'title': title,
            'description': description,
            'category': category,
            'listing_type': listing_type,
            'price': price,
            'condition': condition,
            'image_url': image_url,
        }
        
        # Validation checks
        if not title:
            errors['title'] = "Title is required."
        if not description:
            errors['description'] = "Description is required."
        if not category:
            errors['category'] = "Category is required."
        if not listing_type:
            errors['listing_type'] = "Listing type is required."
        if not condition:
            errors['condition'] = "Condition is required."
            
        if listing_type in ['Sell', 'Rent']:
            if not price:
                errors['price'] = "Price is required for buying/selling or renting."
            else:
                try:
                    price_val = float(price)
                    if price_val < 0:
                        errors['price'] = "Price cannot be negative."
                except ValueError:
                    errors['price'] = "Price must be a valid number."
        else:
            price = None
            
        if not errors:
            item = Item.objects.create(
                owner=request.user,
                title=title,
                description=description,
                category=category,
                listing_type=listing_type,
                price=price,
                condition=condition,
                image=image,
                image_url=image_url,
                status='Available'
            )
            messages.success(request, f"Successfully listed '{item.title}' in the campus marketplace!")
            return redirect('item_detail', pk=item.pk)
            
    categories = Item.CATEGORY_CHOICES
    listing_types = Item.LISTING_TYPE_CHOICES
    conditions = Item.CONDITION_CHOICES
    
    return render(request, 'marketplace/item_form.html', {
        'errors': errors,
        'values': values,
        'action': 'List New Item',
        'categories': categories,
        'listing_types': listing_types,
        'conditions': conditions,
    })

@login_required
def item_update_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.owner != request.user:
        messages.error(request, "You are not authorized to edit this listing.")
        return redirect('item_detail', pk=item.pk)
        
    errors = {}
    values = {
        'title': item.title,
        'description': item.description,
        'category': item.category,
        'listing_type': item.listing_type,
        'price': item.price,
        'condition': item.condition,
        'image_url': item.image_url,
    }
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '').strip()
        listing_type = request.POST.get('listing_type', '').strip()
        price = request.POST.get('price', '').strip()
        condition = request.POST.get('condition', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        image = request.FILES.get('image')
        
        values = {
            'title': title,
            'description': description,
            'category': category,
            'listing_type': listing_type,
            'price': price,
            'condition': condition,
            'image_url': image_url,
        }
        
        # Validation checks
        if not title:
            errors['title'] = "Title is required."
        if not description:
            errors['description'] = "Description is required."
        if not category:
            errors['category'] = "Category is required."
        if not listing_type:
            errors['listing_type'] = "Listing type is required."
        if not condition:
            errors['condition'] = "Condition is required."
            
        if listing_type in ['Sell', 'Rent']:
            if not price:
                errors['price'] = "Price is required for buying/selling or renting."
            else:
                try:
                    price_val = float(price)
                    if price_val < 0:
                        errors['price'] = "Price cannot be negative."
                except ValueError:
                    errors['price'] = "Price must be a valid number."
        else:
            price = None
            
        if not errors:
            item.title = title
            item.description = description
            item.category = category
            item.listing_type = listing_type
            item.price = price
            item.condition = condition
            item.image_url = image_url
            if image:
                item.image = image
            item.save()
            
            messages.success(request, f"Updated '{item.title}' successfully.")
            return redirect('item_detail', pk=item.pk)
            
    categories = Item.CATEGORY_CHOICES
    listing_types = Item.LISTING_TYPE_CHOICES
    conditions = Item.CONDITION_CHOICES
    
    return render(request, 'marketplace/item_form.html', {
        'errors': errors,
        'values': values,
        'action': 'Update Item',
        'item': item,
        'categories': categories,
        'listing_types': listing_types,
        'conditions': conditions,
    })

@login_required
def item_delete_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    # Ensure owner
    if item.owner != request.user:
        messages.error(request, "You are not authorized to delete this listing.")
        return redirect('item_detail', pk=item.pk)
    
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f"Deleted listing '{title}' from marketplace.")
        return redirect('home')
        
    return render(request, 'marketplace/item_confirm_delete.html', {'item': item})

@login_required
@require_POST
def save_item_toggle(request, pk):
    item = get_object_or_404(Item, pk=pk)
    saved_item, created = SavedItem.objects.get_or_create(user=request.user, item=item)
    if not created:
        saved_item.delete()
        saved = False
    else:
        saved = True
    return JsonResponse({'saved': saved})

@login_required
@require_POST
def item_complete_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.owner != request.user:
        messages.error(request, "You are not authorized to complete this deal.")
        return redirect('item_detail', pk=item.pk)

    buyer_id = request.POST.get('buyer_id')
    final_price = request.POST.get('final_price')

    if not buyer_id:
        messages.error(request, "Buyer is required to complete the transaction.")
        return redirect('item_detail', pk=item.pk)

    buyer = get_object_or_404(User, pk=buyer_id)

    # Update item status, buyer and price
    if item.listing_type in ['Sell', 'Rent']:
        if final_price:
            try:
                item.price = float(final_price)
            except ValueError:
                messages.error(request, "Invalid final price.")
                return redirect('item_detail', pk=item.pk)

        if item.listing_type == 'Sell':
            item.status = 'Sold'
        else:
            item.status = 'Rented'
    else:
        item.status = 'Inactive'
        item.price = None

    item.buyer = buyer
    item.save()

    messages.success(request, f"Congratulations! You completed the deal with {buyer.username} for {item.title}.")

    # Try to redirect to the chat room if it exists
    from chat.models import ChatRoom
    room = ChatRoom.objects.filter(item=item, buyer=buyer, seller=request.user).first()
    if room:
        return redirect('chat_room', pk=room.id)
    return redirect('item_detail', pk=item.pk)
