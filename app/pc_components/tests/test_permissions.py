import pytest
from rest_framework.test import APIRequestFactory
from pc_components.models import Pc
from pc_components.permissions import IsPcOwnerOrCustomizedFalse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_permission_allows_non_customized():
    pc = Pc.objects.create(name="Public PC", description="Free for all", is_customized=False)
    user = User.objects.create_user(username="testuser", password="123")

    request = APIRequestFactory().get("/fake-url/")
    request.user = user

    permission = IsPcOwnerOrCustomizedFalse()
    assert permission.has_object_permission(request, None, pc) is True

@pytest.mark.django_db
def test_permission_denies_customized_wrong_user():
    pc = Pc.objects.create(name="Private PC", description="Locked", is_customized=True)
    user = User.objects.create_user(username="stranger", password="123")

    request = APIRequestFactory().get("/fake-url/")
    request.user = user

    permission = IsPcOwnerOrCustomizedFalse()
    assert permission.has_object_permission(request, None, pc) is False
