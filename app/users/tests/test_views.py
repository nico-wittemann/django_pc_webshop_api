import pytest
from rest_framework.test import APIClient
from users.models import User

@pytest.mark.django_db
def test_create_user():
    client = APIClient()
    data = {
        "username": "nico",
        "email": "nico@example.com",
        "password": "secretpass"
    }
    response = client.post("/users/", data, format="json")
    assert response.status_code == 201
    assert User.objects.filter(username="nico").exists()

@pytest.mark.django_db
def test_user_can_only_see_own_data():
    user1 = User.objects.create_user(username="user1", password="123")
    user2 = User.objects.create_user(username="user2", password="123")

    client = APIClient()
    client.force_authenticate(user=user2)
    response = client.get("/api/users/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["username"] == "user2"

@pytest.mark.django_db
def test_admin_can_see_all_users():
    admin = User.objects.create_superuser(username="admin", password="admin")
    user1 = User.objects.create_user(username="user1", password="123")
    user2 = User.objects.create_user(username="user2", password="456")

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get("/api/users/")

    assert response.status_code == 200
    assert len(response.data) >= 3  # admin + 2 users
