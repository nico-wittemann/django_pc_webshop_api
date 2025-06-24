import pytest
from rest_framework.test import APIClient
from pc_components.models import Component, Pc

@pytest.mark.django_db
def test_get_component_list():
    Component.objects.create(
        name="Test GPU", type="GPU", manufacturer="NVIDIA",
        price=1000, currency="EUR", description="", technical_details=""
    )

    client = APIClient()
    response = client.get("/api/components/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Test GPU"

@pytest.mark.django_db
def test_create_component():
    client = APIClient()
    data = {
        "name": "Test RAM",
        "type": "RAM",
        "manufacturer": "Corsair",
        "price": 79.99,
        "currency": "EUR",
        "description": "16GB RAM",
        "technical_details": "DDR4 3200MHz"
    }

    response = client.post("/api/components/", data, format="json")
    assert response.status_code == 201
    assert Component.objects.filter(name="Test RAM").exists()

@pytest.mark.django_db
def test_create_pc_with_components():
    comp = Component.objects.create(
        name="Test CPU", type="CPU", manufacturer="Intel",
        price=299.99, currency="EUR", description="", technical_details=""
    )

    client = APIClient()
    data = {
        "name": "My Build",
        "description": "Gaming PC",
        "is_customized": True,
        "components": [comp.id]
    }

    response = client.post("/api/pcs/", data, format="json")
    assert response.status_code == 201
    assert Pc.objects.filter(name="My Build").exists()
    pc = Pc.objects.get(name="My Build")
    assert pc.components.count() == 1

@pytest.mark.django_db
def test_get_pc_list():
    Pc.objects.create(name="Public PC", description="Offenes System", is_customized=False)

    client = APIClient()
    response = client.get("/api/pcs/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Public PC"