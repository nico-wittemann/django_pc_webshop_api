import pytest
from pc_components.models import Component, Pc, Pc_Components

@pytest.mark.django_db
def test_create_component():
    component = Component.objects.create(
        name="RTX 4090",
        type="GPU",
        manufacturer="NVIDIA",
        price=1999.99,
        currency="EUR",
        description="High-end GPU",
        technical_details="24GB GDDR6X"
    )
    assert str(component) == "RTX 4090 - (GPU) - (NVIDIA)"
    assert component.price == 1999.99
    assert component.currency == "EUR"

@pytest.mark.django_db
def test_create_pc_with_component():
    component = Component.objects.create(
        name="Intel i9",
        type="CPU",
        manufacturer="Intel",
        price=599.99,
        currency="EUR",
        description="High-end CPU",
        technical_details="8 cores"
    )

    pc = Pc.objects.create(
        name="Gaming Beast",
        description="Ultimate gaming machine",
        is_customized=True
    )
    pc.components.add(component)

    assert pc.components.count() == 1
    assert str(pc) == "Gaming Beast (Customized: True)"

@pytest.mark.django_db
def test_pc_components_through_model():
    component = Component.objects.create(
        name="Corsair RAM",
        type="RAM",
        manufacturer="Corsair",
        price=129.99,
        currency="EUR",
        description="DDR4 RAM",
        technical_details="16GB 3200MHz"
    )
    pc = Pc.objects.create(
        name="Workstation",
        description="PC for productivity",
        is_customized=False
    )
    link = Pc_Components.objects.create(pc=pc, component=component)

    assert str(link) == "Workstation - Corsair RAM"
    assert link.pc.name == "Workstation"
    assert link.component.name == "Corsair RAM"
