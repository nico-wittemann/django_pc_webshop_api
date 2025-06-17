import pytest
from orders.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_order_is_saved_correctly():
    user = User.objects.create_user(username="nico", password="123")
    order = Order.objects.create(
        user=user,
        total_price=149.99,
        payment_method="stripe",
        payment_status="paid",
        currency="USD",
        status="completed"
    )

    assert order.user == user
    assert order.total_price == 149.99
    assert order.payment_method == "stripe"
    assert order.payment_status == "paid"
    assert order.currency == "USD"
    assert order.status == "completed"
    assert order.created_at is not None

@pytest.mark.django_db
def test_order_default_status_is_pending():
    user = User.objects.create_user(username="nico", password="123")
    order = Order.objects.create(user=user, total_price=49.99)
    assert order.status == "pending"

@pytest.mark.django_db
def test_order_default_currency_is_eur():
    user = User.objects.create_user(username="nico", password="123")
    order = Order.objects.create(user=user, total_price=29.99)
    assert order.currency == "EUR"

@pytest.mark.django_db
def test_order_missing_user_raises_error():
    with pytest.raises(Exception):
        Order.objects.create(total_price=99.99)

@pytest.mark.django_db
def test_order_created_at_is_auto_set():
    user = User.objects.create_user(username="nico", password="123")
    order = Order.objects.create(user=user, total_price=89.99)
    assert order.created_at is not None