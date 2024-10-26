#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 08:42:42 2024

@author: octave
"""

# config.py

# API Keys
INCH_API_KEY = "XX"
ZERO_X_API_KEY =  "XX"

# URLs
COWSWAP_URL = "https://api.cow.fi/mainnet/api/v1/quote"
ODOS_URL = "https://api.odos.xyz/sor/quote/v2"
ZERO_X_URL = "https://api.0x.org/swap/permit2/quote"
LIFI_URL = "https://li.quest/v1/quote"
INCH_URL = "https://api.1inch.dev/swap/v6.0"

# Network Addresses
NETWORK_CONFIG = {
    'Base': {
        'chain_id': 8453,
        'USDC': '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913',
        'WETH': '0x4200000000000000000000000000000000000006'
    },
    'Arbitrum': {
        'chain_id': 42161,
        'USDC': '0xaf88d065e77c8cc2239327c5edb3a432268e5831',
        'WETH': '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
    },
    'Optimism': {
        'chain_id': 10,
        'USDC': '0x0b2c639c533813f4aa9d7837caf62653d097ff85',
        'WETH': '0x4200000000000000000000000000000000000006'
    },
    'Mainnet': {
        'chain_id': 1,
        'USDC': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
        'WETH': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
    }
}

# Default parameters
DEFAULT_USER_ADDRESS = "0xb29601eB52a052042FB6c68C69a442BD0AE90082"
DEFAULT_TAKER_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
