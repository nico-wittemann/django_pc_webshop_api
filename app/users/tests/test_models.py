import pytest
from users.models import User, User_Pc
from pc_components.models import Pc

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(username="nico", email="nico@test.de", password="geheim")
    assert user.username == "nico"
    assert user.email == "nico@test.de"
    assert user.check_password("geheim") is True

@pytest.mark.django_db
def test_user_pc_relationship():
    user = User.objects.create_user(username="puma", password="katze123")
    pc = Pc.objects.create(name="BeastPC", description="Power!", is_customized=True)

    link = User_Pc.objects.create(user=user, pc=pc)

    assert link.user.username == "puma"
    assert link.pc.name == "BeastPC"
    assert str(link) == f"{user.username} - {pc.id}"