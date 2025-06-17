import pytest
from orders.serializers import OrderSerializer, Order_ItemSerializer
from orders.models import Order, Order_Item
from pc_components.models import Pc, Component
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_order_serializer_valid_data():
    user = User.objects.create_user(username="nico", password="123")
    data = {
        "total_price": 100.00,
        "status": "pending",
        "payment_method": "stripe",
        "payment_status": "unpaid",
        "currency": "EUR",
    }

    serializer = OrderSerializer(data=data)
    assert serializer.is_valid()
    order = serializer.save(user=user)
    assert order.user == user
    assert order.total_price == 100.00

@pytest.mark.django_db
def test_order_item_serializer_missing_component_for_pc_type():
    order = Order.objects.create(
        user=User.objects.create_user(username="nico", password="123"),
        total_price=100,
        status="pending",
        payment_method="stripe",
        payment_status="unpaid",
        currency="EUR"
    )

    data = {
        "order": order.id,
        "order_type": "pc",
        "component": None,
        "pc": None
    }

    serializer = Order_ItemSerializer(data=data)
    assert not serializer.is_valid()
    assert "component" in serializer.errors

@pytest.mark.django_db
def test_order_item_serializer_missing_pc_for_component_type():
    order = Order.objects.create(
        user=User.objects.create_user(username="user2", password="123"),
        total_price=200,
        status="pending",
        payment_method="paypal",
        payment_status="unpaid",
        currency="EUR"
    )

    data = {
        "order": order.id,
        "order_type": "component",
        "pc": None,
        "component": None
    }

    serializer = Order_ItemSerializer(data=data)
    assert not serializer.is_valid()
    assert "pc" in serializer.errors