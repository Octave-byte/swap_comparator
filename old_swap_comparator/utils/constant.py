import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()
ID1inch = os.getenv("ID1inch")


@dataclass
class MainnetAddress:
    token_address: str
    decimals: int


# TODO: refactor
ARBISCAN_MAINNET_ADDRESS = {
    "WETH": MainnetAddress("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", 18),
    "WBTC": MainnetAddress("0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f", 8),
    "USDC": MainnetAddress("0xaf88d065e77c8cC2239327C5EDb3A432268e5831", 6),
    "USDT": MainnetAddress("0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", 6),
    "ARB": MainnetAddress("0x912CE59144191C1204E64559FE8253a0e49E6548", 18),
    "WSTETH": MainnetAddress("0x0fBcbaEA96Ce0cF7Ee00A8c19c3ab6f5Dc8E1921", 18),
}

ETHERSCAN_MAINNET_ADDRESS = {
    "WETH": MainnetAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 18),
    "WBTC": MainnetAddress("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", 8),
    "USDC": MainnetAddress("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
    "USDT": MainnetAddress("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
    "ARB": MainnetAddress("0xB50721BCf8d664c30412Cfbc6cf7a15145234ad1", 18),
    "WSTETH": MainnetAddress("0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0", 18),
    "MKR": MainnetAddress("0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2", 18),
}


class AmountCategory:
    stable_coin = [100, 1000, 10000, 100000, 1000000]
    WETH = [0.01, 0.1, 1, 10, 100, 1000, 10000]
    WBTC = [0.01, 0.1, 1, 10, 100, 1000, 10000]


@dataclass
class Chain_ID:
    ID: int


CHAIN_ID = {
    "ETH": Chain_ID(1),
    "BSC": Chain_ID(56),
    "ARBITRUM": Chain_ID(42161),
}
