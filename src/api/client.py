"""
API client module for AltoroMutual banking API integration.

This module provides a robust API client with retry logic, authentication,
and methods for retrieving account and transaction data following PEP 8 standards.
"""

import base64
from typing import Any, Dict, List, Optional

import backoff
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from api.models import Account, ApiResponse, Transaction
from utils.config_loader import settings
from utils.logging_utils import execution_logger


class AltoroApiClient:
    """API client for AltoroMutual banking API."""

    def __init__(self) -> None:
        """
        Initialize API client with configuration and retry strategy.

        Sets up HTTP session with automatic retry on server errors
        and configures timeouts from settings.
        """
        self.base_url: str = settings.api.base_url
        self.timeout: float = settings.api.timeout / 1000  # Convert to seconds
        self.verify_ssl: bool = settings.api.verify_ssl

        # Create session with retry strategy for resilience
        self.session: requests.Session = requests.Session()
        retry_strategy = Retry(
            total=settings.retry.max_attempts,
            backoff_factor=settings.retry.backoff_factor,
            status_forcelist=[500, 502, 503, 504],  # Retry on server errors
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self._token: Optional[str] = None  # Store auth token

    def _get_auth_header(self, username: str, password: str) -> str:
        """
        Generate basic auth header.

        Args:
            username: API username
            password: API password

        Returns:
            Authorization header value
        """
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    @backoff.on_exception(backoff.expo, requests.RequestException, max_tries=3)
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with API.

        Args:
            username: API username
            password: API password

        Returns:
            True if authenticated
        """
        try:
            headers = {
                "Authorization": self._get_auth_header(username, password),
                "Content-Type": "application/json",
            }

            response = self.session.post(
                f"{self.base_url}/auth/login",
                headers=headers,
                json={"username": username, "password": password},
                timeout=self.timeout,
                verify=self.verify_ssl,
            )

            if response.status_code == 200:
                data = response.json()
                self._token = data.get("token", "")
                self.session.headers.update({"Authorization": f"Bearer {self._token}"})

                execution_logger.log_action("api_auth", "success", username=username)
                return True
            else:
                execution_logger.log_action(
                    "api_auth",
                    "failed",
                    username=username,
                    status_code=response.status_code,
                )
                return False

        except Exception as e:
            execution_logger.logger.error(f"Authentication failed: {e}")
            return False

    def get_accounts(self) -> List[Account]:
        """
        Get list of accounts.

        Returns:
            List of Account objects
        """
        try:
            response = self.session.get(
                f"{self.base_url}/accounts",
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            response.raise_for_status()

            data = response.json()
            accounts = [Account(**acc) for acc in data.get("accounts", [])]

            execution_logger.log_action("api_get_accounts", "success", count=len(accounts))
            return accounts

        except Exception as e:
            execution_logger.logger.error(f"Failed to get accounts: {e}")
            return []

    def get_account_details(self, account_id: str) -> Optional[Account]:
        """
        Get account details.

        Args:
            account_id: Account ID

        Returns:
            Account object or None
        """
        try:
            response = self.session.get(
                f"{self.base_url}/accounts/{account_id}",
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            response.raise_for_status()

            data = response.json()
            account = Account(**data)

            execution_logger.log_action("api_get_account", account_id)
            return account

        except Exception as e:
            execution_logger.logger.error(f"Failed to get account {account_id}: {e}")
            return None

    def get_transactions(
        self,
        account_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Transaction]:
        """
        Get transactions with optional filters.

        Args:
            account_id: Optional account ID filter
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            List of Transaction objects
        """
        try:
            params = {}
            if account_id:
                params["account_id"] = account_id
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            response = self.session.get(
                f"{self.base_url}/transactions",
                params=params,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            response.raise_for_status()

            data = response.json()
            transactions = [Transaction(**tx) for tx in data.get("transactions", [])]

            execution_logger.log_action(
                "api_get_transactions",
                "success",
                count=len(transactions),
                filters=params,
            )
            return transactions

        except Exception as e:
            execution_logger.logger.error(f"Failed to get transactions: {e}")
            return []

    def transfer_funds(
        self,
        from_account: str,
        to_account: str,
        amount: float,
        description: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        Transfer funds between accounts.

        Args:
            from_account: Source account ID
            to_account: Destination account ID
            amount: Transfer amount
            description: Optional description

        Returns:
            Transfer confirmation or None
        """
        try:
            payload = {
                "from_account": from_account,
                "to_account": to_account,
                "amount": amount,
                "description": description,
            }

            response = self.session.post(
                f"{self.base_url}/transfers",
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            response.raise_for_status()

            confirmation = response.json()

            execution_logger.log_action(
                "api_transfer",
                "success",
                from_account=from_account,
                to_account=to_account,
                amount=amount,
            )
            return confirmation

        except Exception as e:
            execution_logger.logger.error(f"Failed to transfer funds: {e}")
            return None
