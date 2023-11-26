from typing import Tuple

import aiohttp


async def request(url: str, method: str = 'get', params: dict = None, json: dict = None) -> Tuple[bool, dict]:
    try:
        async with aiohttp.ClientSession() as session:
            if method == 'get':
                response = await session.get(url=url, params=params)
                return True, await response.json()
            elif method == 'post':
                response = await session.post(url=url, json=json)
                return True, await response.json()

    except (Exception,):
        pass

    return False, {}
