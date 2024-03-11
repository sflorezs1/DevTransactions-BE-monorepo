import requests
import json

# Base URL for the GovCarpeta API (replace with actual URL)
GOVCARPETA_API_URL = 'https://govcarpeta-21868b7e9dd3.herokuapp.com/apis/validateCitizen/{id}'

def validate_citizen(citizen_id: int) -> dict:
    """Fetches and returns citizen data from GovCarpeta API.

    Args:
        citizen_id: The integer ID of the citizen to validate.

    Returns:
        A dictionary containing citizen data or an error message on failure.
    """

    url = GOVCARPETA_API_URL.format(id=citizen_id)  # Format URL with ID
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()['Data']  # Return citizen data from successful response
    else:
        return {"error": f"Error validating citizen: {response.status_code}"}


citizen_data = validate_citizen(12345678)
if 'error' in citizen_data:
    print(citizen_data['error'])
else:
    print(f"Citizen validated: {citizen_data['Name']}")
