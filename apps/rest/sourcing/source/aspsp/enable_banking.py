from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from aiohttp import ClientSession
from jose import jwt

from sourcing.config import EB_APPLICATION_ID, EB_PRIVATE_KEY_FILE_PATH

BASE_URL = "https://api.enablebanking.com"


class EnableBankingClient:
    def __init__(self, private_key_file_path: Path, application_id: str):
        self._private_key = private_key_file_path.read_text()
        self._application_id = application_id
        self._session = None

    async def clean_up(self):
        await self._session.close()
        self._session = None

    def startup(self):
        self._session = ClientSession()

    async def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        headers = {"Authorization": f"Bearer {self._generate_token()}"}
        async with self._session.request(
            method, url, headers=headers, **kwargs
        ) as response:
            return await response.json()

    def _generate_token(self):
        iat = int(datetime.now().timestamp())
        payload = {
            "iss": "enablebanking.com",
            "aud": "api.enablebanking.com",
            "iat": iat,
            "exp": iat + 3600,
        }
        token = jwt.encode(
            payload,
            self._private_key,
            algorithm="RS256",
            headers={"kid": self._application_id},
        )
        return token

    async def get_aspsps(self, country_code: str):
        return await self._request("GET", f"{BASE_URL}/aspsps?country={country_code}")

    async def create_auth_session(
        self, name: str, country: str, redirect_url: str, state: str = ""
    ):
        body = {
            "access": {
                "valid_until": (datetime.now(UTC) + timedelta(days=10)).isoformat()
            },
            "aspsp": {"name": name, "country": country},
            "redirect_url": redirect_url,
            "psu_type": "personal",
            "state": state,
        }
        return await self._request("POST", f"{BASE_URL}/auth", json=body)

    async def create_session(self, code: str):
        return await self._request("POST", f"{BASE_URL}/sessions", json={"code": code})

    async def get_account_balances(self, account_id: str):
        return await self._request("GET", f"{BASE_URL}/accounts/{account_id}/balances")


client = EnableBankingClient(
    private_key_file_path=EB_PRIVATE_KEY_FILE_PATH, application_id=EB_APPLICATION_ID
)
