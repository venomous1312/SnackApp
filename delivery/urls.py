from django.urls import path
from django.contrib.auth import views as auth_views  # <--- Add this exact line
from . import views

urlpatterns = [
    path('', views.main_menu, name='Home'),
    path('order/',views.place_order, name='place_order'),
    path('portal/', views.driver_portal, name='driver_portal'),
    path('track/', views.track_order, name='track_order'),
    path('<slug:business_slug>/order/', views.place_order, name='place_order'),
    path('claim/<int:order_id>/', views.claim_order, name='claim_order'),
    path('complete/<int:order_id>/', views.complete_order, name='complete_order'),
    
    # This uses the 'auth_views' name you just imported
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.customer_register, name='customer_signup'),
]