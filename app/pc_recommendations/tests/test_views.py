import pytest
from rest_framework.test import APIClient
from pc_recommendations.views import extract_json_from_ai, PCRecommendationView

# === extract_json_from_ai ===
def test_extract_json_from_ai_valid():
    raw_response = """
        Sure, here's your build:
        ```json
        {"name": "BudgetBeast", "components": []}
        ```
    """
    result = extract_json_from_ai(raw_response)
    assert isinstance(result, dict)
    assert result["name"] == "BudgetBeast"


def test_extract_json_from_ai_invalid():
    raw_response = "This response does not contain JSON"
    with pytest.raises(ValueError):
        extract_json_from_ai(raw_response)

@pytest.mark.django_db
def test_validate_weight_distribution_variants():
    view = PCRecommendationView()

    # Testcase 1 – Valid distribution
    weights_valid = {
        "cpu": 25, "gpu": 30, "ram": 15, "ssd": 10,
        "psu": 7, "case": 5, "motherboard": 5, "cooler": 3
    }
    assert view._validate_weight_distribution(weights_valid) == True

    # Testcase 2 – All values = 0 → invalid
    weights_all_zero = {
        "cpu": 0, "gpu": 0, "ram": 0, "ssd": 0,
        "psu": 0, "case": 0, "motherboard": 0, "cooler": 0
    }
    assert view._validate_weight_distribution(weights_all_zero) == False

    # Testcase 3 – Everything much too high → Total much > 100
    weights_too_high = {
        "cpu": 30, "gpu": 30, "ram": 30, "ssd": 30,
        "psu": 30, "case": 30, "motherboard": 30, "cooler": 30
    }
    assert view._validate_weight_distribution(weights_too_high) == False

    # Testcase 4 – “case” is too small (<5)
    weights_case_too_low = {
        "cpu": 25, "gpu": 30, "ram": 15, "ssd": 10,
        "psu": 7, "case": 3, "motherboard": 5, "cooler": 5
    }
    assert view._validate_weight_distribution(weights_case_too_low) == False

def test_convert_component_type_cpu():
    view = PCRecommendationView()
    assert view._convert_component_type("cpu") == "CPU"

def test_convert_component_type_gpu():
    view = PCRecommendationView()
    assert view._convert_component_type("gpu") == "GPU"

def test_convert_component_type_psu():
    view = PCRecommendationView()
    assert view._convert_component_type("psu") == "Power Supply"

def test_convert_component_type_unknown():
    view = PCRecommendationView()
    assert view._convert_component_type("xyz") is None

# === POST request test (no API call, just logic error) ===
@pytest.mark.django_db
def test_post_missing_fields():
    client = APIClient()
    response = client.post("/api/pc_recommendations/recommend/", data={}, format="json")
    assert response.status_code == 400
    assert "error" in response.data