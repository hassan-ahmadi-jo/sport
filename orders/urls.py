from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('payment/', views.PaymentOrderView.as_view(), name='payment'),
    path('payment/verify/', views.PaymentVerifyView.as_view(), name='payment_verify'),
]
