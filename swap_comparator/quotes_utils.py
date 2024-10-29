#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 08:43:11 2024

@author: octave
"""

# quote_utils.py

import pandas as pd
import requests
import time
from typing import Optional, Dict
from quotes_config import (
    INCH_API_KEY, ZERO_X_API_KEY, COWSWAP_URL, ODOS_URL,
    ZERO_X_URL, LIFI_URL, INCH_URL, DEFAULT_USER_ADDRESS,
    DEFAULT_TAKER_ADDRESS
)

def extract_quote_lifi(df: pd.DataFrame) -> Dict:
    """Extract quote data from LiFi response"""
    return {
        'minAmount': df['estimate.toAmountMin'].iloc[0],
        'Amount': df['estimate.toAmount'].iloc[0]
    }

def extract_quote_zerox(df: pd.DataFrame) -> Dict:
    """Extract quote data from 0x response"""
    return {
        'minAmount': df['minBuyAmount'].iloc[0],
        'Amount': df['buyAmount'].iloc[0]
    }

def extract_quote_oneinch(df: pd.DataFrame) -> Dict:
    """Extract quote data from 1inch response"""
    return {
        'minAmount': None,
        'Amount': df['dstAmount'].iloc[0]
    }

def extract_quote_odos(df: pd.DataFrame) -> Dict:
    """Extract quote data from Odos response"""
    return {
        'minAmount': None,
        'Amount': float(df['outAmounts'].iloc[0][0])
    }

def extract_quote_data(quote: Dict[str, pd.DataFrame], sellToken: str, buyToken: str, sellAmount: str) -> pd.DataFrame:
    """Combine quote data from all sources into a single DataFrame"""
    extracted_data = []
    
    extractors = {
        'lifi': extract_quote_lifi,
        'zero_x': extract_quote_zerox,
        '1inch': extract_quote_oneinch,
        'odos': extract_quote_odos
    }
    
    for protocol, df in quote.items():
        if df is not None and protocol in extractors:
            extracted = extractors[protocol](df)
            extracted.update({
                'protocol': protocol,
                'sellToken': sellToken,
                'buyToken': buyToken,
                'sellAmount': float(sellAmount)
            })
            extracted_data.append(extracted)

    return pd.DataFrame(extracted_data)

def get_odos_quote(chain_id: int, sellToken: str, buyToken: str, amount: str) -> Optional[pd.DataFrame]:
    """Get quote from Odos"""
    try:
        odos_data = {
            "chainId": chain_id,
            "compact": True,
            "gasPrice": 20,
            "inputTokens": [{"amount": amount, "tokenAddress": sellToken}],
            "outputTokens": [{"proportion": 1, "tokenAddress": buyToken}],
            "referralCode": 0,
            "slippageLimitPercent": 0.3,
            "sourceBlacklist": [],
            "sourceWhitelist": [],
            "userAddr": "0xb29601eB52a052042FB6c68C69a442BD0AE90082"
        }
        
        response = requests.post(ODOS_URL, headers={"Content-Type": "application/json"}, json=odos_data)
        return pd.json_normalize(response.json()) if response.status_code == 200 else None
    except Exception as e:
        print(f"Odos error: {str(e)}")
        return None

def get_zerox_quote(chain_id: int, sellToken: str, buyToken: str, amount: str) -> Optional[pd.DataFrame]:
    """Get quote from 0x"""
    try:
        params = {
            "chainId": chain_id,
            "sellToken": sellToken,
            "buyToken": buyToken,
            "sellAmount": float(amount),
            'taker': DEFAULT_TAKER_ADDRESS
        }
        
        response = requests.get(
            ZERO_X_URL,
            headers={"0x-api-key": ZERO_X_API_KEY, "0x-version": "v2"},
            params=params
        )
        return pd.json_normalize(response.json()) if response.status_code == 200 else None
    except Exception as e:
        print(f"0x error: {str(e)}")
        return None

def get_lifi_quote(chain_id: int, sellToken: str, buyToken: str, amount: str) -> Optional[pd.DataFrame]:
    """Get quote from Li.Fi"""
    try:
        params = {
            "fromChain": chain_id,
            "toChain": chain_id,
            "fromToken": sellToken,
            "toToken": buyToken,
            "fromAddress": DEFAULT_USER_ADDRESS,
            "fromAmount": amount
        }
        
        response = requests.get(LIFI_URL, headers={"accept": "application/json"}, params=params)
        return pd.json_normalize(response.json()) if response.status_code == 200 else None
    except Exception as e:
        print(f"Li.Fi error: {str(e)}")
        return None

def get_oneinch_quote(chain_id: int, sellToken: str, buyToken: str, amount: str) -> Optional[pd.DataFrame]:
    """Get quote from 1inch"""
    try:
        params = {
            "src": sellToken,
            "dst": buyToken,
            "amount": amount,
            "fee": 0
        }
        
        response = requests.get(
            f"{INCH_URL}/{chain_id}/quote",
            headers={
                "Authorization": f"Bearer {INCH_API_KEY}",
                "accept": "application/json",
                "content-type": "application/json"
            },
            params=params
        )
        return pd.json_normalize(response.json()) if response.status_code == 200 else None
    except Exception as e:
        print(f"1inch error: {str(e)}")
        return None

def get_unified_quotes(
    chain_id: int,
    sellToken: str,
    buyToken: str,
    amount: str
) -> pd.DataFrame:
    """Get quotes from all aggregators and combine them"""
    quotes = {
        'odos': get_odos_quote(chain_id, sellToken, buyToken, amount),
        'zero_x': get_zerox_quote(chain_id, sellToken, buyToken, amount),
        'lifi': get_lifi_quote(chain_id, sellToken, buyToken, amount),
        '1inch': get_oneinch_quote(chain_id, sellToken, buyToken, amount)
    }
    
    return extract_quote_data(quotes, sellToken, buyToken, amount)

def get_unified_quotes_for_routes(amounts: list, networks: list) -> None:
    """Get quotes for multiple amounts across multiple networks"""
    from config import NETWORK_CONFIG
    
    for network in networks:
        if network not in NETWORK_CONFIG:
            print(f"Skipping unknown network: {network}")
            continue

        time.sleep(0.3)
            
        network_data = NETWORK_CONFIG[network]
        chain_id = network_data['chain_id']
        usdc_address = network_data['USDC']
        weth_address = network_data['WETH']
        
        for amount in amounts:
            # Adjust amount based on USDC decimals (6)
            adjusted_amount = str(int(amount * (10 ** 6)))
            
            df = get_unified_quotes(
                chain_id,
                usdc_address,
                weth_address,
                adjusted_amount
            )
            
            print(f"\nQuotes for {network} for amount ${amount}:")
            print(df)
            print("\n" + "="*50)
