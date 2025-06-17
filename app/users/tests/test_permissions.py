import pytest
from rest_framework.test import APIRequestFactory
from users.models import User
from users.permissions import IsUserOwner

@pytest.mark.django_db
def test_permission_allows_owner():
    user = User.objects.create_user(username="nico", password="123")
    request = APIRequestFactory().get("/fake-url/")
    request.user = user

    permission = IsUserOwner()
    assert permission.has_object_permission(request, None, user) is True

@pytest.mark.django_db
def test_permission_denies_other_user():
    user1 = User.objects.create_user(username="a", password="123")
    user2 = User.objects.create_user(username="b", password="456")

    request = APIRequestFactory().get("/fake-url/")
    request.user = user2

    permission = IsUserOwner()
    assert permission.has_object_permission(request, None, user1) is False

@pytest.mark.django_db
def test_permission_allows_superuser():
    admin = User.objects.create_superuser(username="admin", password="admin")
    user = User.objects.create_user(username="normal", password="123")

    request = APIRequestFactory().get("/fake-url/")
    request.user = admin

    permission = IsUserOwner()
    assert permission.has_object_permission(request, None, user) is True