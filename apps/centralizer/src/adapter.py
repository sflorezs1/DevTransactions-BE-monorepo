import requests

class GovCarpetaAPIAdapter:
    def __init__(self, base_url="https://govcarpeta-21868b7e9dd3.herokuapp.com"):
        self.base_url = base_url

    def register_citizen(self, citizen_data):
        """
        Registers a citizen or a company with the provided data.
        
        :param citizen_data: A dictionary containing the citizen or company data.
        :return: A dictionary with the response data.
        """
        endpoint = "apis/registerCitizen"
        response = self._post(endpoint, data=citizen_data)
        return response

    def _post(self, endpoint, data=None):
        """
        Generic POST request method.
        """
        try:
            response = requests.post(f"{self.base_url}/{endpoint}", json=data)
            response.raise_for_status()  # Will raise an exception for HTTP error codes
            return {"status": "success", "data": response.json()}
        except requests.exceptions.HTTPError as e:
            # HTTP error occurred
            return {"status": "error", "message": str(e), "code": e.response.status_code}
        except requests.exceptions.RequestException as e:
            # Other errors (e.g., network issues)
            return {"status": "error", "message": str(e)}

    def unregister_citizen(self, citizen_data):
        """
        Unregisters a citizen or a company with the provided data.
        
        :param citizen_data: A dictionary containing the citizen or company data to be unregistered.
        :return: A dictionary with the response data.
        """
        endpoint = "apis/unregisterCitizen"
        response = self._delete(endpoint, data=citizen_data)
        return response

    def _delete(self, endpoint, data=None):
        """
        Generic DELETE request method.
        """
        try:
            response = requests.delete(f"{self.base_url}/{endpoint}", json=data)
            response.raise_for_status()  # Will raise an exception for HTTP error codes
            if response.status_code == 204:  # HTTP 204 No Content
                return {"status": "success", "message": "No Content"}
            else:
                return {"status": "success", "data": response.json()}
        except requests.exceptions.HTTPError as e:
            # HTTP error occurred
            return {"status": "error", "message": str(e), "code": e.response.status_code}
        except requests.exceptions.RequestException as e:
            # Other errors (e.g., network issues)
            return {"status": "error", "message": str(e)}
