from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrderViewSet, Order_ItemViewSet, OrderPaymentViewSet

# Router for Orders
order_router = DefaultRouter()
order_router.register('orders', OrderViewSet)

# Router for Order Items
order_item_router = DefaultRouter()
order_item_router.register('order_items', Order_ItemViewSet)

# Router for payment
payment_router = DefaultRouter()
payment_router.register('pay', OrderPaymentViewSet, basename='pay')

urlpatterns = [
    path('', include(order_router.urls)),
    path('', include(order_item_router.urls)),
    path('', include(payment_router.urls)),
]