from typing import Any

from aiohttp import ClientSession

BASE_URL = "https://api.blockchain.info/v2"


class BlockchainClient:
    def __init__(self):
        self._session = None

    async def clean_up(self):
        await self._session.close()
        self._session = None

    def startup(self):
        self._session = ClientSession()

    async def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        async with self._session.request(method, url, **kwargs) as response:
            return await response.json()

    async def get_address_data(self, symbol: str, address: str):
        return await self._request(
            "GET", f"{BASE_URL}/{symbol.lower()}/data/account/{address}/wallet"
        )


client = BlockchainClient()
