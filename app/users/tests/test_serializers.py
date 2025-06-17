import pytest
from users.models import User
from users.serializers import UserSerializer

@pytest.mark.django_db
def test_user_serializer_creates_user_with_hashed_password():
    data = {
        "username": "nico",
        "email": "nico@test.de",
        "password": "geheim"
    }
    serializer = UserSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    user = serializer.save()
    assert user.username == "nico"
    assert user.email == "nico@test.de"
    assert user.check_password("geheim") is True

@pytest.mark.django_db
def test_user_serializer_does_not_return_password():
    user = User.objects.create_user(username="testuser", email="t@example.com", password="pass")
    serializer = UserSerializer(user)
    data = serializer.data
    assert "password" not in data
