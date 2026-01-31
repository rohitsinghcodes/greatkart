from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('cash-on-delivery/', views.cash_on_delivery, name='cash_on_delivery'),
    path('paypal-success/', views.paypal_payment_success, name='paypal_payment_success'),
    path('order-complete/', views.order_complete, name='order_complete'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
