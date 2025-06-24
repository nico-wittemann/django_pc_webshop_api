from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pc_components.models import Component, Pc
import requests
import re
import json
import openai
import os
from django.db.models.functions import Random


class PCRecommendationView(APIView):
    """
    API endpoint for generating a custom PC build recommendation.

    This view receives a budget and user requirements, calculates an optimal component budget distribution,
    filters compatible components from the database, and queries a language model to generate a valid PC configuration.
    """

    def post(self, request):
        """
        Handles the incoming POST request to generate a PC recommendation.

        Steps:
        1. Validates that both budget and requirements are present in the request.
        2. Sends a prompt to OpenAI to calculate percentage-based budget allocation.
        3. Filters components from the database based on that allocation.
        4. Sends a second prompt to generate the final PC build.
        5. If no valid build is found, retries with new components (max 4 times).
        6. Returns the recommendation as a JSON response.

        Returns:
            Response: A JSON response with either the PC build or an error message.
        """
        try:
            budget = request.data.get('budget')
            requirements = request.data.get('requirements')

            if not budget or not requirements:
                return Response(
                    {"error": "Budget and requirements are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            base_prompt = f"""You are an experienced PC expert. Create a percentage-based budget distribution for a custom PC build based on the following:

            - Total budget: {budget} Euros
            - Requirements: {requirements}

            ⚠️ STRICT INSTRUCTIONS:
            - Return only a valid JSON object – absolutely no comments, explanation, or extra formatting
            - Use exactly these 8 component types as keys:
              "cpu", "gpu", "ram", "ssd", "psu", "case", "motherboard", "cooler"
            - The sum of all values must be **exactly 100** (as percentages) – no rounding errors
            - All values must be positive numbers
            - The share for "case" must be at least 5%
            - Do not include extra keys like "monitor", "keyboard", "others", etc.

            📦 Example format (structure must match exactly):

            {{
              "cpu": 25,
              "gpu": 30,
              "ram": 15,
              "ssd": 10,
              "psu": 7,
              "case": 5,
              "motherboard": 5,
              "cooler": 3
            }}
            """

            MAX_RETRIES = 6
            for attempt in range(MAX_RETRIES):
                try:
                    prompt = base_prompt
                    if attempt == 1:
                        prompt += "\n\n// Please repeat the calculation with a completely new approach. The previous result did not sum up to exactly 100 – this time, make absolutely sure that the percentage values add up to exactly 100, with no rounding errors."
                    weight_response = self._send_to_lm_studio(prompt, is_weight_distribution=True)
                    weight_data = extract_json_from_ai(weight_response)

                    if not self._validate_weight_distribution(weight_data):
                        raise ValueError("Invalid price distribution from the AI")

                    build_attempts = 4
                    for build_try in range(build_attempts):
                        filtered_components = self._get_filtered_components(budget, weight_data)
                        print("[DEBUG] Filtered Components:")
                        for key, comps in filtered_components.items():
                            print(f"  {key.upper()}:")
                            for c in comps:
                                print(f"    - {c['name']} | {c['price']}€")

                        final_prompt = self._create_final_prompt(budget, requirements, filtered_components)
                        final_recommendation = self._send_to_lm_studio(final_prompt, is_weight_distribution=False)

                        try:
                            parsed = extract_json_from_ai(final_recommendation)
                        except ValueError:
                            parsed = {}

                        if "error" in parsed and parsed["error"] == "NO_VALID_BUILD":
                            if build_try < build_attempts - 1:
                                continue  # retry with new components
                            else:
                                return Response(
                                    {"error": "AI could not create a valid build after multiple attempts."},
                                    status=status.HTTP_424_FAILED_DEPENDENCY
                                )
                        else:
                            self._save_created_pc_to_database(parsed)
                            return Response({"recommendation": final_recommendation})

                except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
                    print(f"Error during processing: {str(e)}")
                    if attempt == MAX_RETRIES - 1:
                        return Response(
                            {"error": f"Error during processing: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

        except Exception as e:
            print(f'Unexpected error: {str(e)}')
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_to_lm_studio(self, prompt, is_weight_distribution=True):
        """
        Sends a prompt to the OpenAI ChatGPT API and returns the model's JSON-formatted response.

        Args:
            prompt (str): The user prompt to send to the model.
            is_weight_distribution (bool): If True, uses a prompt to get percentage allocation.
                                           If False, generates a full PC build.

        Returns:
            str: JSON string extracted from the model's response.

        Raises:
            ValueError: If the response is empty or invalid, or if parsing fails.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenAI API Key in environment variables.")

        openai.api_key = api_key

        system_prompt = (
            "You are an experienced PC expert. Only return the required JSON answer, "
            "without any additional explanations or text. When providing a budget distribution, "
            "make sure the sum is exactly 100% and the case share is at least 5%."
            if is_weight_distribution else
            "You are an experienced PC expert. Analyze the given components and create an optimal PC build. "
            "Provide a detailed but concise recommendation that covers all required aspects."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )

            content = response['choices'][0]['message']['content']
            content = content.replace('```json', '').replace('```', '').strip()
            start = content.find('{')
            end = content.rfind('}') + 1

            if start != -1 and end != 0:
                json_str = content[start:end]
                json.loads(json_str)  # Test for valid JSON
                return json_str
            else:
                raise ValueError("No JSON found in the response")
        except Exception as e:
            raise ValueError(f"OpenAI API Error: {e}")

    def _validate_weight_distribution(self, weight_data):
        """
        Validates the AI-generated budget allocation for PC components.

        Ensures:
        - All required component keys are present.
        - All values are positive numbers.
        - Total percentage equals exactly 100 (±15% tolerance).
        - The case percentage is at least 5%.

        Args:
            weight_data (dict): Dictionary with component percentages.

        Returns:
            bool: True if the distribution is valid, False otherwise.
        """
        try:
            weight_data = {k: float(v) for k, v in weight_data.items()}
            required_keys = ['cpu', 'gpu', 'ram', 'ssd', 'psu', 'case', 'motherboard', 'cooler']
            if not all(key in weight_data for key in required_keys):
                return False
            total = sum(weight_data.values())
            if not (90 <= total <= 110):
                return False
            if weight_data['case'] < 5:
                print("Note: Case share too low, setting it to 5%")
                weight_data['case'] = 5.0
            if not all(v > 0 for v in weight_data.values()):
                return False
            return True
        except (ValueError, TypeError):
            return False

    def _get_filtered_components(self, budget, weight_data):
        """
        Filters PC components from the database based on price allocation per component type.

        Uses an expanding price range to ensure that at least 8 components are found for each type.
        Removes duplicates to ensure variety in the final prompt.

        Args:
            budget (float): Total user budget.
            weight_data (dict): Percentage allocation per component type.

        Returns:
            dict: Mapping from component type (str) to list of matching components (dicts).
        """
        filtered_components = {}

        for component_type, percentage in weight_data.items():
            target_price = (budget * percentage) / 100
            db_type = self._convert_component_type(component_type)

            min_count = 8
            current_range = 0.1
            max_range = 0.6
            step = 0.05

            while current_range <= max_range:
                min_price = target_price * (1 - current_range)
                max_price = target_price * (1 + current_range)
                components = Component.objects.filter(
                    type=db_type,
                    price__gte=min_price,
                    price__lte=max_price
                ).order_by(Random())[:50]

                unique_components = self._remove_duplicates([
                    {
                        'name': comp.name,
                        'manufacturer': comp.manufacturer,
                        'price': float(comp.price)
                    }
                    for comp in components
                ])

                if len(unique_components) >= min_count:
                    filtered_components[component_type] = unique_components[:min_count]
                    break

                current_range += step

            if component_type not in filtered_components:
                filtered_components[component_type] = unique_components[:min_count]

        return filtered_components

    def _convert_component_type(self, type_str):
        """
        Maps internal AI component type names to database-compatible type strings.

        Args:
            type_str (str): AI component type name (e.g., 'gpu', 'psu').

        Returns:
            str: Matching database type name (e.g., 'GPU', 'Power Supply').
        """
        type_map = {
            'cpu': 'CPU',
            'gpu': 'GPU',
            'ram': 'RAM',
            'ssd': 'Storage',
            'psu': 'Power Supply',
            'case': 'Case',
            'motherboard': 'Motherboard',
            'cooler': 'Cooler'
        }
        return type_map.get(type_str.lower())

    def _remove_duplicates(self, components_list):
        seen = set()
        unique = []
        for comp in components_list:
            identifier = comp['name'].lower()
            if identifier not in seen:
                seen.add(identifier)
                unique.append(comp)
        return unique

    def _create_final_prompt(self, budget, requirements, filtered_components):
        """
        Constructs the final prompt to send to OpenAI to generate a full PC build.

        Includes:
        - Budget
        - Requirements
        - List of filtered components
        - JSON format template the model must return

        Args:
            budget (float): User-defined budget.
            requirements (str): Usage scenario or preferences.
            filtered_components (dict): Dict of filtered components per type.

        Returns:
            str: Fully formatted prompt to send to the model.
        """
        components_str = ""
        for comp_type, components in filtered_components.items():
            components_str += f"\n{comp_type.upper()} Components:\n"
            for comp in components:
                components_str += f"- {comp['name']} ({comp['manufacturer']}) - {comp['price']:.2f}€\n"
            components_str += "\n"
        prompt = f"""You are a professional PC builder.

        Your task is to recommend a **complete PC build** using **exactly one component from each of the following categories**:
        - CPU
        - GPU
        - RAM
        - SSD
        - PSU
        - Case
        - Motherboard
        - Cooler

        🛑 STRICT RULES:
        - Total budget: {budget}€
        - Use case: {requirements}
        - Components must be chosen **only from the list below**
        - All 8 components must be included – none may be skipped
        - All components must be **fully compatible**
        - CPU and motherboard must have the **same socket** (e.g., AM4 with AM4, LGA1700 with LGA1700)
        - Do **not mix** AMD CPUs with Intel motherboards, or Intel CPUs with AMD motherboards
        - RAM must be compatible with the motherboard (e.g., DDR4 not on DDR3-only boards)
        - PSU must be powerful enough for the selected GPU and CPU
        - Intel 12th/13th Gen CPUs (e.g., i5-12600K, i7-13700K) may only be paired with motherboards that officially support these generations, such as H610, B660, Z690, Z790, etc.
        - Do not use older chipsets like B560, B460, or H510 with 12th/13th Gen CPUs under any circumstances – they are not compatible out of the box and must be strictly avoided.
        - Total cost must be as close to the budget as possible (within 2–5%), without exceeding it
        - You must return **only a valid JSON object** – no extra text or explanation
        - Add a short and unique name to the build (1–3 words). It should be creative, relevant, and cool (e.g., "ShadowForge", "BudgetBeast", "ZenStreamX")
        - Return it as a string in a "name" field at the beginning of the JSON


        📦 JSON format (must match exactly):

        {{
          "name": "ShadowForge",
          "components": [
            {{ "name": "Example CPU", "price": 250.00 }},
            {{ "name": "Example GPU", "price": 400.00 }},
            {{ "name": "Example RAM", "price": 120.00 }},
            {{ "name": "Example SSD", "price": 100.00 }},
            {{ "name": "Example PSU", "price": 80.00 }},
            {{ "name": "Example Case", "price": 70.00 }},
            {{ "name": "Example Motherboard", "price": 130.00 }},
            {{ "name": "Example Cooler", "price": 50.00 }}
          ],
          "total_cost": 1200.00,
          "justification": "Explain briefly why these components were selected."
        }}
        
        IF no valid combination of 8 compatible components exists, return the following instead:
        {{
          "error": "NO_VALID_BUILD"
        }}
        Do not try to guess or work around this. Only return that exact JSON object if compatibility is impossible.

        Available components to choose from:

        {components_str}
        """
        return prompt

    def _save_created_pc_to_database(self, new_pc_data):
        """
        Saves a newly generated PC build to the database.

        This method receives a parsed JSON object from the AI recommendation,
        checks if the suggested PC name is unique, and creates a new `Pc` entry
        with all selected components. If the name already exists, a numeric suffix
        is appended to ensure uniqueness.

        Args:
            new_pc_data (dict): A dictionary containing:
                - "name" (str): The recommended PC name.
                - "components" (list of dicts): Each dict includes "name" and "price".

        Notes:
            - Only components that exist in the database (matched by name) are linked.
            - If a component is not found in the database, it is skipped with a warning.
            - The PC is marked as `is_customized=True` to indicate an AI-generated build.
        """

        name = new_pc_data["name"]
        components = new_pc_data["components"]

        # Make name unique
        base_name = name
        counter = 1
        while Pc.objects.filter(name=name).exists():
            name = f"{base_name}-{counter}"
            counter += 1

        # Create Pc in Database
        pc = Pc.objects.create(
            name=name,
            is_customized=True
        )

        # Add components to Pc
        for comp in components:
            clean_name = re.sub(r"\s+\([^)]+\)$", "", comp["name"])
            db_component = Component.objects.filter(name__icontains=clean_name).first()
            if db_component:
                pc.components.add(db_component)
            else:
                print(f"[WARN] Component not found in DB: {comp['name']}")

        print(f"[INFO] Created PC: {pc.name} with {pc.components.count()} components")



def extract_json_from_ai(content: str):
    """
    Extracts the first valid JSON object from a raw string returned by a language model.

    Args:
        content (str): Raw response text from the AI.

    Returns:
        dict: Parsed JSON object.

    Raises:
        ValueError: If extraction or JSON parsing fails.
    """
    try:
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found")
        json_str = json_match.group()
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Error while extracting JSON: {e}")
