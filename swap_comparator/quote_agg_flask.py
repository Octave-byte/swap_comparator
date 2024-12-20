

from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import base64
from datetime import datetime, timezone


app = Flask(__name__)


#########
## BRIDGES
##########

### RELAY

def relay_quote(originChain, destinationChain, originToken, destinationToken, amount):
    url = "https://api.relay.link/price"
    payload = {
        "user": "0xb29601eB52a052042FB6c68C69a442BD0AE90082",
        "originChainId": originChain,
        "destinationChainId": destinationChain,
        "originCurrency": originToken,# "<string>",
        "destinationCurrency": destinationToken, # "<string>",
        "amount": str(int(amount)), #"<string>",
        "tradeType": "EXACT_INPUT"
    }
    headers = {"Content-Type": "application/json"}
    relay_response = requests.request("POST", url, json=payload, headers=headers)

    if relay_response.status_code == 200:

        relay = relay_response.json()

        result = {
        "project": "Relay",
        "expectedAmount": float(relay["details"]["currencyOut"]["amountFormatted"]),
        "efficiency": 1 + float(relay["details"]["totalImpact"]["percent"])/100,
        "time": relay["details"]["timeEstimate"]}
        result['efficiency'] = f"{result['efficiency'] * 100:.4f}%"
        return result
    else:
        return {}

### Jumper

def jumper_quote(originChain, destinationChain, originToken, destinationToken, amount, LIFI_KEY, price_from_amount, price_to_amount):

    headers = {
        "accept": "application/json",
        "x-lifi-api-key": LIFI_KEY
        }

    payload = {
            "fromChain": originChain,
            "toChain": destinationChain,
            "fromToken": originToken,
            "toToken": destinationToken,
            "fromAddress": "0xb29601eB52a052042FB6c68C69a442BD0AE90082",
            "fromAmount": int(amount)
        }
    lifi_response = requests.get(
            "https://li.quest/v1/quote",
            headers=headers,
            params=payload)

    if lifi_response.status_code == 200:

        lifi = lifi_response.json()

        to_amount = int(lifi["estimate"]["toAmount"]) / (10 ** lifi["action"]["toToken"]["decimals"])
        to_amount_usd = to_amount * float(price_to_amount)
        from_amount_usd = float(price_from_amount) * int(lifi["estimate"]["fromAmount"]) / (10 ** lifi["action"]["fromToken"]["decimals"])
        result = {
            "project": "Jumper",
            "expectedAmount": to_amount,
            "efficiency": to_amount_usd / from_amount_usd,
            "time": lifi["estimate"]["executionDuration"]
            }
        result['efficiency'] = f"{result['efficiency'] * 100:.4f}%"
        return result
    else:
        return {}
    return result


### BUNGEE

def bungee_quote(fromChain, toChain, fromTokenAddress, toTokenAddress, amount, price_from_amount, price_to_amount,bungee_key ):
    if fromChain == toChain:
        return {}
    else:
        response = requests.get(
            "https://api.socket.tech/v2/quote",
            params={
                "fromChainId": fromChain,
                "fromTokenAddress": fromTokenAddress,
                "toChainId": toChain,
                "toTokenAddress": toTokenAddress,
                "fromAmount": int(amount),
                "userAddress": '0x98F0f120de21a90f220B0027a9c70029Df9BBde4',
            },
            headers={
                "API-KEY": bungee_key,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        bungee = response.json()
        to_amount = int(bungee["result"]["routes"][0]["toAmount"])/ (10 ** bungee["result"]["toAsset"]["decimals"])
        to_amount_usd = float(price_to_amount) * to_amount
        from_amount_usd = float(price_from_amount) * amount / (10 ** bungee["result"]["fromAsset"]["decimals"])
        time = int(bungee["result"]["routes"][0]["serviceTime"])

        result = {
            "project": "Bungee",
            "expectedAmount": to_amount,
            "efficiency": to_amount_usd / from_amount_usd,
            "time": time
            }
        result['efficiency'] = f"{result['efficiency'] * 100:.4f}%"
        return result

### OKX


def okx_quote(fromChain, toChain, fromTokenAddress, toTokenAddress, amount,  price_from_amount, price_to_amount,
              okx_project_key, okx_access_key, okx_secret_key, okx_passphrase, slippage=0.01):

    if fromChain == toChain:
        return {}
    else:
        amount = int(amount)

        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        request_path = f'/api/v5/dex/cross-chain/quote?amount={amount}&fromChainId={fromChain}&toChainId={toChain}&fromTokenAddress={fromTokenAddress}&toTokenAddress={toTokenAddress}&slippage={slippage}'
        url = f'https://www.okx.com{request_path}'

        signature = generate_okx_signature(
            timestamp,
            'GET',
            request_path,
            okx_secret_key
        )

        headers = {
        'Content-Type': 'application/json',
        'OK-ACCESS-KEY': okx_access_key,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': okx_passphrase
        }

        response = requests.get(url, headers=headers)

        # Process the response
        if response.status_code == 200:
            data = response.json()

            if data['code'] == '0' and data['data']:
                first_route = data['data'][0]

                to_amount = int(data["data"][0]["routerList"][0]["toTokenAmount"]) / (10 ** data["data"][0]["toToken"]["decimals"])
                to_amount_usd = float(price_to_amount) * to_amount
                from_amount_usd = float(price_from_amount) * int(data["data"][0]["fromTokenAmount"]) / (10 ** data["data"][0]["fromToken"]["decimals"])


                result = {
                    "project": "OKX",
                    "expectedAmount": to_amount,
                    "efficiency": to_amount_usd / from_amount_usd,
                    "time": int(first_route.get('routerList', [{}])[0].get('estimateTime', 0)),
                }

                result['efficiency'] = f"{result['efficiency'] * 100:.4f}%"

                return result
            else:
                return {}
        else:
            return {}



#########
### DEXES
#########

### ODOS

def odos_quote(fromChain, toChain, fromTokenAddress, toTokenAddress, amount, toTokenDecimals):
    if fromChain != toChain:
        return {}
    else:
        odos_data = {
                "chainId": fromChain,
                "compact": True,
                "gasPrice": 20,
                "inputTokens": [{"amount": str(int(amount)), "tokenAddress": fromTokenAddress}],
                "outputTokens": [{"proportion": 1, "tokenAddress": toTokenAddress}],
                "referralCode": 0,
                "slippageLimitPercent": 0.1,
                "sourceBlacklist": [],
                "sourceWhitelist": [],
                "userAddr": "0xb29601eB52a052042FB6c68C69a442BD0AE90082"
            }

        odos_response = requests.post(
                "https://api.odos.xyz/sor/quote/v2",
                headers={"Content-Type": "application/json"},
                json=odos_data
            )

        if odos_response.status_code == 200:
                odos = odos_response.json()
                to_amount = int(odos["outAmounts"][0]) / (10 ** toTokenDecimals)
                result = {
                    "project": "Odos",
                    "expectedAmount": to_amount,
                    "efficiency": 1 - odos["percentDiff"]/100,
                    "time": 15
                    }

                result['efficiency'] = f"{result['efficiency'] * 100:.4f}%"
                return result
        else:
                return {}
        return result

### 0x

def zero_quote(fromChain, toChain, fromTokenAddress, toTokenAddress, amount, price_from_amount, price_to_amount, fromTokenDecimals, toTokenDecimals,zero_x_api_key):
    if fromChain != toChain:
        return {}
    else:
        zero_x_params = {
                    "chainId": fromChain,
                    "sellToken": fromTokenAddress,
                    "buyToken": toTokenAddress,
                    "sellAmount": int(amount),
                    'taker': '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'
                }
        zero_x_response = requests.get(
                    "https://api.0x.org/swap/permit2/quote",
                    headers={
                        "0x-api-key": zero_x_api_key,
                        "0x-version": "v2"
                    },
                    params=zero_x_params
                )

        if zero_x_response.status_code == 200:
                zero = zero_x_response.json()
                to_amount = int(zero["buyAmount"]) / (10 ** toTokenDecimals)
                to_amount_usd = float(price_to_amount) * to_amount / (10 ** toTokenDecimals)
                from_amount_usd = float(price_from_amount) * int(amount) / (10 ** fromTokenDecimals)

                result = {
                    "project": "Odos",
                    "expectedAmount": to_amount,
                    "efficiency": 1- (to_amount_usd / from_amount_usd),
                    "time": 15
                    }

                result['efficiency'] = f"{result['efficiency'] * 100:.4f}%"


                return result
        else:
                return {}
        return result

### 1inch

def inch_quote(fromChain, toChain, fromTokenAddress, toTokenAddress, amount, price_from_amount, price_to_amount, fromTokenDecimals, toTokenDecimals, inch_api_key):
    if fromChain != toChain:
        return {}
    else:
       inch_params = {
                   "src": fromTokenAddress,
                   "dst": toTokenAddress,
                   "amount": str(int(amount)),
                   "fee": 0
               }
       inch_response = requests.get(
                   f"https://api.1inch.dev/swap/v6.0/{fromChain}/quote",
                   headers={
                       "Authorization": f"Bearer {inch_api_key}",
                       "accept": "application/json",
                       "content-type": "application/json"
                   },
                   params=inch_params
               )

       if inch_response.status_code == 200:

                inch = inch_response.json()
                to_amount = int(inch["dstAmount"]) / (10 ** toTokenDecimals)
                to_amount_usd = float(price_to_amount) * to_amount
                from_amount_usd = float(price_from_amount) * int(amount) / (10 ** fromTokenDecimals)

                result = {
                    "project": "1inch",
                    "expectedAmount": to_amount,
                    "efficiency": to_amount_usd / from_amount_usd,
                    "time": 15
                    }

                result['efficiency'] = f"{result['efficiency'] * 100:.4f}%"


                return result
       else:
                return {}
       return result

##########
### QUOTE FUNCTION
##########

def quote(originChainSymbol, destinationChainSymbol, originTokenSymbol, destinationTokenSymbol, amountRaw):

    lifi_key= "XXX"
    inch_api_key = "XXX"
    zero_x_api_key = "XXX"
    bungee_key = 'XXX'
    okx_project_key = 'XXX'
    okx_access_key = 'XXX'
    okx_secret_key = 'XXX'
    okx_passphrase = 'XXX'

    headers = {
        "accept": "application/json",
        "x-lifi-api-key": lifi_key
        }

    # MAP: Chain -> ChainId
    response = requests.get("https://li.quest/v1/chains?chainTypes=EVM", headers=headers)
    chains = response.json()
    name_to_chain_id = {item["name"]: item["id"] for item in chains["chains"]}
    originChain = name_to_chain_id.get(originChainSymbol, 1)
    destinationChain = name_to_chain_id.get(destinationChainSymbol, 8453)

    # MAP: symbolToken -> Decimals, Token

    if originTokenSymbol == 'ETH':
        originTokenSymbol = 'WETH'
    if destinationTokenSymbol == 'ETH':
        destinationTokenSymbol = 'WETH'

    response = requests.get(f"https://li.quest/v1/token?chain={originChain}&token={originTokenSymbol}", headers=headers)
    token_1 = response.json()
    amount = amountRaw * (10 ** token_1["decimals"])
    originToken = token_1["address"]
    price_from_amount = token_1["priceUSD"]
    fromTokenDecimals = token_1["decimals"]

    response = requests.get(f"https://li.quest/v1/token?chain={destinationChain}&token={destinationTokenSymbol}", headers=headers)
    token_2 = response.json()
    destinationToken = token_2["address"]
    price_to_amount = token_2["priceUSD"]
    toTokenDecimals = token_2["decimals"]


    jumper = jumper_quote(originChain, destinationChain, originToken, destinationToken, amount, lifi_key, price_from_amount, price_to_amount)
    relay = relay_quote(originChain, destinationChain, originToken, destinationToken, amount)
    odos = odos_quote(originChain, destinationChain, originToken, destinationToken, amount, toTokenDecimals)
    zero = zero_quote(originChain, destinationChain, originToken, destinationToken, amount, price_from_amount, price_to_amount, fromTokenDecimals, toTokenDecimals,zero_x_api_key)
    inch = inch_quote(originChain, destinationChain, originToken, destinationToken, amount, price_from_amount, price_to_amount, fromTokenDecimals, toTokenDecimals, inch_api_key)
    bungee = bungee_quote(originChain, destinationChain, originToken, destinationToken, amount, price_from_amount, price_to_amount, bungee_key)
    okx_bridge = okx_quote(originChain, destinationChain, originToken, destinationToken, amount,  price_from_amount, price_to_amount,okx_project_key, okx_access_key, okx_secret_key, okx_passphrase, slippage=0.01)

    if originChainSymbol== destinationChainSymbol:
        quotes = [jumper,relay,odos,zero,inch]
    else:
        quotes = [jumper,relay,bungee,okx_bridge]
    quotes = sorted(quotes, key=lambda x: x['expectedAmount'], reverse=True)
    return quotes

#########
## HELPERS
##########

def generate_okx_signature(timestamp, method, request_path, secret_key):
    message = f"{timestamp}{method}{request_path}"
    # Create HMAC-SHA256 signature
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

@app.route('/get_quote', methods=['GET'])
def get_quote():
    try:
        # Extract parameters from query string
        origin_chain = request.args.get('origin_chain')
        destination_chain = request.args.get('destination_chain')
        origin_token = request.args.get('origin_token')
        destination_token = request.args.get('destination_token')
        amount = float(request.args.get('amount'))


        # Call the quote function
        quotes = quote(origin_chain, destination_chain, origin_token, destination_token, amount)

        return jsonify({
            "status": "success",
            "quotes": quotes
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


# if __name__ == '__main__':
#     app.run(debug=True, port=5001)

