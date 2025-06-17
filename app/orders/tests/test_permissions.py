import pytest
from rest_framework.permissions import SAFE_METHODS
from orders.permissions import IsOrderOwner
from orders.models import Order
from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

User = get_user_model()


@pytest.mark.django_db
def test_is_order_owner_allows_owner():
    user = User.objects.create_user(username="nico", password="123")
    order = Order.objects.create(user=user, total_price=100)

    factory = APIRequestFactory()
    request = factory.get("/fake-url/")
    request.user = user

    permission = IsOrderOwner()
    assert permission.has_object_permission(request, None, order) is True


@pytest.mark.django_db
def test_is_order_owner_denies_other_user():
    user1 = User.objects.create_user(username="user1", password="123")
    user2 = User.objects.create_user(username="user2", password="123")
    order = Order.objects.create(user=user1, total_price=100)

    factory = APIRequestFactory()
    request = factory.get("/fake-url/")
    request.user = user2

    permission = IsOrderOwner()
    assert permission.has_object_permission(request, None, order) is False


@pytest.mark.django_db
def test_is_order_owner_allows_admin():
    admin = User.objects.create_superuser(username="admin", password="admin123")
    user = User.objects.create_user(username="user", password="123")
    order = Order.objects.create(user=user, total_price=100)

    factory = APIRequestFactory()
    request = factory.get("/fake-url/")
    request.user = admin

    permission = IsOrderOwner()
    assert permission.has_object_permission(request, None, order) is True
