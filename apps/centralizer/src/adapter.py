import aiohttp
import requests
from .config import CENTRALIZER_BASE_URL


class GovCarpetaAPIAdapter:
    def __init__(self):
        self.base_url = CENTRALIZER_BASE_URL

    async def register_citizen(self, citizen_data):
        """
        Registers a citizen or a company with the provided data.
        
        :param citizen_data: A dictionary containing the citizen or company data.
        :return: A dictionary with the response data.
        """
        endpoint = "apis/registerCitizen"
        response = await self._post(endpoint, data=citizen_data)
        return response

    async def _post(self, endpoint, data=None):
        """
        Generic POST request method.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/{endpoint}", json=data) as response:
                response.raise_for_status()  # Will raise an exception for HTTP error codes
                return {"status": response.status, "data": await response.json()}

    async def unregister_citizen(self, citizen_data):
        """
        Unregisters a citizen or a company with the provided data.
        
        :param citizen_data: A dictionary containing the citizen or company data to be unregistered.
        :return: A dictionary with the response data.
        """
        endpoint = "apis/unregisterCitizen"
        response = await self._delete(endpoint, data=citizen_data)
        return response

    async def _delete(self, endpoint, data=None):
        """
        Generic DELETE request method.
        """
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/{endpoint}", json=data) as response:
                response.raise_for_status()  # Will raise an exception for HTTP error codes
                if response.status == 204:  # HTTP 204 No Content
                    return {"status": response.status, "data": None}
                else:
                    return {"status": response.status, "data": await response.json()}
    
    async def validate_citizen(self, citizen_id):
        """
        Validates a citizen for registration based on their ID.
        
        :param citizen_id: The ID of the citizen to validate.
        :return: A dictionary with the response data.
        """
        endpoint = f"apis/validateCitizen/{citizen_id}"
        response = await self._get(endpoint)
        return response

    async def _get(self, endpoint):
        """
        Generic GET request method.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/{endpoint}") as response:
                response.raise_for_status()  # Will raise an exception for HTTP error codes
                if response.status == 204:  # HTTP 204 No Content
                    return {"status": response.status, "data": None}
                else:
                    return {"status": response.status, "data": await response.json()}