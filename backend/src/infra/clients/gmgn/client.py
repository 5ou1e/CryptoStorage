import logging

import aiohttp
from aiohttp import BasicAuth

logger = logging.getLogger(__name__)


class GmgnAPIClient:
    BASE_URL = "https://gmgn.ai/defi/quotation/v1/"

    def __init__(self, cookies, proxy=None):
        self.cookies = cookies
        self.session = None
        self.init_session(proxy)

    def init_session(self, proxy):
        if proxy:
            proxy_address, proxy_auth = self.parse_proxy(proxy)
            self.session = aiohttp.ClientSession(proxy=proxy_address, proxy_auth=proxy_auth)
        else:
            self.session = aiohttp.ClientSession()

    def parse_proxy(self, proxy):
        proxy_parts = proxy.split(":")
        proxy_address = "http://" + proxy_parts[0] + ":" + proxy_parts[1]
        proxy_auth = BasicAuth(proxy_parts[2], proxy_parts[3])
        return proxy_address, proxy_auth

    async def close(self):
        """Закрытие сессии."""
        if not self.session.closed:
            await self.session.close()

    async def get_token_trades(
        self,
        token_address,
        limit=None,
        limit_per_req=100,
        maker_address="",
        from_timestamp="",
    ):
        url = f"https://gmgn.ai/api/v1/token_trades/sol/{token_address}?limit={limit_per_req}&maker={maker_address}&from={from_timestamp}"

        headers = self.headers()
        headers.update({"referer": f"https://gmgn.ai/sol/token/{token_address}"})

        _next = ""
        stop = False
        results = []  # Список для накопления результатов

        while not stop:
            try:
                next_url = f"{url}&cursor={_next}"
                result = await self.fetch(next_url, headers)
                results.extend(result["data"]["history"])
                _next = result["data"].get("next")  # Проверяем, есть ли 'next' в ответе
                if not _next or (limit and len(results) >= limit):
                    stop = True
            except Exception as e:
                logger.error(f"Ошибка при получении трейдов токена {token_address} -- {e}")

        return results

    async def get_new_pools(self):
        new_pair_ranks = await self.get_new_pair_ranks()
        return new_pair_ranks["new_pools"]

    async def get_new_pair_ranks(self):
        url = (
            self.BASE_URL
            + f"pairs/sol/new_pair_ranks/1h?limit=50&new_pool=%7B%22filters%22:[],%22platforms%22:[%22pump%22,%22moonshot%22,%22raydium%22]%7D&burnt=%7B%22filters%22:[],%22platforms%22:[%22pump%22,%22moonshot%22,%22raydium%22]%7D&dexscreener_spent=%7B%22filters%22:[],%22platforms%22:[%22pump%22,%22moonshot%22,%22raydium%22]%7D"
        )

        headers = self.headers()
        headers.update({"referer": f"https://gmgn.ai/new-pair?chain=sol"})

        result = await self.fetch(url, headers)

        return result["data"]

    async def get_wallet_data(self, wallet):
        url = self.BASE_URL + f"smartmoney/sol/walletNew/{wallet}?period=30d"

        headers = self.headers()
        headers.update({"referer": f"https://gmgn.ai/sol/address/{wallet}"})

        result = await self.fetch(url, headers)

        return result["data"]

    async def get_wallet_activities_data(
        self,
        wallet,
        limit=None,
        limit_per_req=100,
        from_timestamp=None,
    ):
        if limit_per_req and limit_per_req > 100:
            limit_per_req = 100
        url = self.BASE_URL + f"wallet_activity/sol?type=buy&type=sell&wallet={wallet}&limit={limit_per_req}&cost=10"

        headers = self.headers()
        headers.update({"referer": f"https://gmgn.ai/sol/address/{wallet}"})

        _next = ""
        stop = False
        results = []  # Список для накопления результатов

        while not stop:
            try:
                next_url = f"{url}&cursor={_next}"
                result = await self.fetch(next_url, headers)
                _next = result["data"].get("next")  # Проверяем, есть ли 'next' в ответе

                if from_timestamp:
                    filtered_activities = [
                        activity
                        for activity in result["data"]["activities"]
                        if int(activity.get("timestamp")) >= from_timestamp
                    ]
                    results.extend(filtered_activities)
                    if not filtered_activities or len(filtered_activities) < limit_per_req:
                        stop = True
                else:
                    results.extend(result["data"]["activities"])

                if not next or (limit and len(results) >= limit):
                    stop = True
            except Exception as e:
                logger.error(f"Ошибка при получении активностей кошелька {wallet} - {e}")

        return results

    async def fetch(self, url, headers, data=None):
        if data:
            """Метод для выполнения запроса."""
            async with self.session.post(url, data=data, headers=headers, cookies=self.cookies) as response:
                data = await response.json()
        else:
            """Метод для выполнения запроса."""
            async with self.session.get(url, headers=headers, cookies=self.cookies) as response:
                data = await response.json()

        response.raise_for_status()

        return data

    def headers(self):
        cookie_string = ";".join([f"{key}={value}" for key, value in self.cookies.items()])
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "ru,en;q=0.9,es;q=0.8,en-US;q=0.7,ru-RU;q=0.6",
            "cache-control": "no-cache",
            "cookie": cookie_string,
            "priority": "u=1, i",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version": '"131.0.6778.86"',
            "sec-ch-ua-full-version-list": '"Google Chrome";v="131.0.6778.86", "Chromium";v="131.0.6778.86", "Not_A Brand";v="24.0.0.0"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"15.0.0"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:40.0) Gecko/20100101 Firefox/40.0",
        }

        return headers
