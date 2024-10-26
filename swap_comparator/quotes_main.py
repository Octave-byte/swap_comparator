#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 08:44:05 2024

@author: octave
"""

# main.py

from quote_utils import get_unified_quotes_for_routes

def main():
    # Define the amounts to query (in USD)
    amounts = [1000, 10000, 100000, 1000000]
    #amounts = [1000]
    
    # Define the networks to query
    networks = ['Base', 'Arbitrum', 'Optimism', 'Mainnet']
    #networks = ['Arbitrum']
    
    # Get quotes for all combinations
    get_unified_quotes_for_routes(amounts, networks)

if __name__ == "__main__":
    main()