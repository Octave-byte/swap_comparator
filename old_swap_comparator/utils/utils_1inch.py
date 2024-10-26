import aiohttp
import asyncio
import datetime

from swap_comparator.utils.constant import ID1inch, ARBISCAN_MAINNET_ADDRESS, AmountCategory, MainnetAddress


async def run_1inch(data: list[dict], timestamp: datetime.datetime):
    tasks = []

    for amount_stable_coin in AmountCategory.stable_coin:
        tasks.append(
            update_data(
                data,
                timestamp,
                ARBISCAN_MAINNET_ADDRESS["USDC"],
                ARBISCAN_MAINNET_ADDRESS["USDT"],
                amount_stable_coin,
            )
        )

    for amount_WETH in AmountCategory.WETH:
        tasks.append(update_data(data, timestamp, amount_WETH))

    for amount_WBTC in AmountCategory.WBTC:
        tasks.append(update_data(data, timestamp, amount_WBTC))

    await asyncio.gather(*tasks)


async def update_data(
    data: list[dict],
    timestamp: datetime.datetime,
    token_in: MainnetAddress,
    token_out: MainnetAddress,
    amount_stable_coin: float,
):
    to_add = await get_1inch_price(
        token_in=token_in,
        token_out=token_out,
        amount_in=amount_stable_coin,
    )
    elem = {
        "timestamp": timestamp,
        "platform": "1inch",
        "fromToken": token_in,  # TODO: serialize
        "toToken": token_out,  # TODO: serialize
        "chainId": "",
        "gasCost": "",
        "amountIn": amount_stable_coin,
        "amountOut": to_add["toTokenAmount"],
    }
    data.append(elem)


async def get_1inch_price(
    token_in: str,
    token_out: str,
    amount_in: float,
    method: str = "get",
    api_url: str = "https://api.1inch.dev/swap/v6.0/1/quote",
) -> dict:
    headers = {"Authorization": f"Bearer {ID1inch}"}
    body = {}
    params = {
        "src": token_in,
        "dst": token_out,
        "amount": amount_in,
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, headers=headers, params=params) as response:
                return await response.json()
        except asyncio.TimeoutError:
            print(f"Timeout error occurred while fetching {api_url}")
