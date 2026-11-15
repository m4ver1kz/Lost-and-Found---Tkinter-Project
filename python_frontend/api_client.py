"""
api_client.py
-----------------------------------------------------------------------------
Client module responsible for all HTTP REST API communication with the Java
Spring Boot backend.

Contains zero SQL or database queries. All data access occurs over HTTP/JSON.
-----------------------------------------------------------------------------
"""

import os
import requests
from typing import Optional, List, Dict, Any


class ApiException(Exception):
    """Custom exception raised when an API request fails or returns an error."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    """HTTP Client interfacing with the Java Spring Boot REST backend."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 6):
        if base_url is None:
            base_url = os.getenv("API_BASE_URL", "http://localhost:8080/api")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def check_health(self) -> Dict[str, Any]:
        """Check backend server status and MySQL database connectivity."""
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                data = response.json() if response.headers.get("Content-Type", "").startswith("application/json") else {}
                msg = data.get("error", f"Backend returned status {response.status_code}")
                raise ApiException(msg, status_code=response.status_code)
        except requests.exceptions.ConnectionError:
            raise ApiException("Cannot connect to Java backend. Please ensure the server is running on port 8080.")
        except requests.exceptions.Timeout:
            raise ApiException("Connection to backend timed out.")
        except Exception as e:
            if isinstance(e, ApiException):
                raise
            raise ApiException(f"Unexpected connection error: {str(e)}")

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Fetch dashboard summary statistics (total, lost, found, category breakdown)."""
        url = f"{self.base_url}/dashboard/stats"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                self._handle_error_response(response)
        except requests.exceptions.RequestException as e:
            self._handle_network_exception(e)

    def get_items(self, category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve items from MySQL, optionally filtered by category and/or status."""
        url = f"{self.base_url}/items"
        params = {}
        if category and category.strip() and category != "All Categories":
            params["category"] = category.strip()
        if status and status.strip() and status != "ALL":
            params["status"] = status.strip()

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                self._handle_error_response(response)
        except requests.exceptions.RequestException as e:
            self._handle_network_exception(e)

    def search_items(self, name: str) -> List[Dict[str, Any]]:
        """Search items by name using the /api/items/search?name={name} endpoint."""
        url = f"{self.base_url}/items/search"
        params = {"name": name.strip()} if name else {}
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                self._handle_error_response(response)
        except requests.exceptions.RequestException as e:
            self._handle_network_exception(e)

    def get_item_by_id(self, item_id: int) -> Dict[str, Any]:
        """Fetch details of a single item by its ID."""
        url = f"{self.base_url}/items/{item_id}"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                self._handle_error_response(response)
        except requests.exceptions.RequestException as e:
            self._handle_network_exception(e)

    def report_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a new item report (initial status set to LOST). Returns created item with ID."""
        url = f"{self.base_url}/items"
        try:
            response = requests.post(url, json=item_data, timeout=self.timeout)
            if response.status_code in (200, 201):
                return response.json()
            else:
                self._handle_error_response(response)
        except requests.exceptions.RequestException as e:
            self._handle_network_exception(e)

    def mark_as_found(self, item_id: int) -> Dict[str, Any]:
        """Update an item's status to FOUND."""
        url = f"{self.base_url}/items/{item_id}/status"
        payload = {"status": "FOUND"}
        try:
            response = requests.patch(url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                self._handle_error_response(response)
        except requests.exceptions.RequestException as e:
            self._handle_network_exception(e)

    def _handle_error_response(self, response: requests.Response):
        """Parse structured error responses from GlobalExceptionHandler."""
        try:
            data = response.json()
            # Check for validation errors dict
            if "details" in data and isinstance(data["details"], dict):
                field_errors = ", ".join(f"{k}: {v}" for k, v in data["details"].items())
                msg = f"Validation failed: {field_errors}"
            else:
                msg = data.get("message") or data.get("error") or f"Server returned status {response.status_code}"
        except Exception:
            msg = f"Server returned error status {response.status_code}"
        raise ApiException(msg, status_code=response.status_code)

    def _handle_network_exception(self, e: Exception):
        """Handle request connection errors and timeouts."""
        if isinstance(e, requests.exceptions.ConnectionError):
            raise ApiException("Cannot connect to Java backend. Please ensure the server is running on port 8080.")
        elif isinstance(e, requests.exceptions.Timeout):
            raise ApiException("The request to the backend timed out.")
        else:
            raise ApiException(f"Network error: {str(e)}")
