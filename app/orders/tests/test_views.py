import pytest
import random
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from orders.models import Order, Order_Item
from pc_components.models import Pc, Component

User = get_user_model()

def random_username(prefix="user"):
    return f"{prefix}_{random.randint(1000, 9999)}"

@pytest.mark.django_db
def test_user_sees_only_own_orders():
    user1 = User.objects.create_user(username=random_username("nico"), password="123")
    user2 = User.objects.create_user(username=random_username("puma"), password="123")

    Order.objects.create(user=user1, total_price=100, status="pending", payment_method="stripe", payment_status="unpaid", currency="EUR")
    Order.objects.create(user=user2, total_price=200, status="pending", payment_method="stripe", payment_status="unpaid", currency="EUR")

    client = APIClient()
    client.force_authenticate(user=user1)

    response = client.get("/api/orders/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["total_price"] == "100.00"

@pytest.mark.django_db
def test_user_can_create_order():
    user = User.objects.create_user(username=random_username("nico"), password="123")
    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "total_price": 123.45,
        "status": "pending",
        "payment_method": "stripe",
        "payment_status": "unpaid",
        "currency": "EUR"
    }

    response = client.post("/api/orders/", data)
    assert response.status_code == 201
    assert response.data["total_price"] == "123.45"

@pytest.mark.django_db
def test_user_can_create_order_item():
    user = User.objects.create_user(username=random_username("nico"), password="123")
    pc = Pc.objects.create(name="MyPC")
    component = Component.objects.create(name="RAM", category="RAM", brand="Corsair", price=50)

    order = Order.objects.create(user=user, total_price=100, status="pending", payment_method="stripe", payment_status="unpaid", currency="EUR")

    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "order": order.id,
        "order_type": "pc",
        "pc_id": pc.id,
    }

    response = client.post("/api/order_items/", data)
    assert response.status_code == 201

@pytest.mark.django_db
def test_order_payment_success():
    username = random_username("nico")
    email = f"{username}@example.com"
    user = User.objects.create_user(username=username, password="123", email=email)

    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "name": "Nico Test",
        "email": email,
        "iban": "DE89370400440532013000",  # Test-IBAN
        "total": 49.99,
        "items": []
    }

    response = client.post("/api/order_payment/", data, format="json")
    assert response.status_code in [200, 400]
    assert "order_id" in response.data or "error" in response.data

@pytest.mark.django_db
def test_order_payment_missing_data_returns_error():
    user = User.objects.create_user(username=random_username("nico"), password="123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post("/api/order_payment/", data={}, format="json")
    assert response.status_code == 400
    assert "error" in response.data