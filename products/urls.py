from django.urls import path
from . import views

urlpatterns = [
    path('subscriptions/<str:slug>/', views.SubscriptionProductDetailView.as_view(), name='subscription_product'),
    path('', views.ProductsView.as_view(), name='products_list')
]
