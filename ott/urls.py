from django.urls import path
from . import views

urlpatterns = [
    path('', views.ott_list_view, name='ott_list'),
    path('<int:pk>/', views.ott_detail_view, name='ott_detail'),
    path('new/', views.ott_create_view, name='ott_create'),
    path('<int:pk>/request/', views.ott_request_slot_view, name='ott_request'),
    path('request/<int:pk>/approve/', views.ott_approve_request_view, name='ott_approve'),
    path('request/<int:pk>/reject/', views.ott_reject_request_view, name='ott_reject'),
]
