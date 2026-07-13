from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('item/<int:pk>/', views.item_detail_view, name='item_detail'),
    path('item/new/', views.item_create_view, name='item_create'),
    path('item/<int:pk>/edit/', views.item_update_view, name='item_update'),
    path('item/<int:pk>/delete/', views.item_delete_view, name='item_delete'),
    path('item/<int:pk>/complete/', views.item_complete_view, name='item_complete'),
    path('save/<int:pk>/', views.save_item_toggle, name='save_item_toggle'),
]
