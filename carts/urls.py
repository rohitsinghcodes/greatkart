from django.urls import path
from . import views

urlpatterns = [
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('', views.cart, name='cart'),
    path('check-cart-variation/', views.check_cart_variation, name='check_cart_variation'),
]
