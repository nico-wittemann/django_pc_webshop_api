import pytest
import uuid
from rest_framework.test import APIClient
from users.models import User

def random_username(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:6]}"

@pytest.mark.django_db
def test_create_user():
    client = APIClient()
    username = random_username("nico")
    data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "secretpass"
    }
    response = client.post("/users/", data, format="json")
    assert response.status_code == 201
    assert User.objects.filter(username=username).exists()

@pytest.mark.django_db
def test_user_can_only_see_own_data():
    user1 = User.objects.create_user(username=random_username("user1"), password="123")
    user2 = User.objects.create_user(username=random_username("user2"), password="123")

    client = APIClient()
    client.force_authenticate(user=user2)
    response = client.get("/users/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["username"] == user2.username

@pytest.mark.django_db
def test_admin_can_see_all_users():
    admin = User.objects.create_superuser(username=random_username("admin"), password="admin")
    user1 = User.objects.create_user(username=random_username("user1"), password="123")
    user2 = User.objects.create_user(username=random_username("user2"), password="456")

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get("/users/")

    assert response.status_code == 200
    assert len(response.data) >= 3  # admin + 2 users