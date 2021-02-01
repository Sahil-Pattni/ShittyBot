# ------- HANDLES ALL BINANCE TRADING / API INTERFACING ------- #

from urllib.parse import urlencode
from ApiError import ApiError # Custom Binance API Exception
import requests
import hashlib # SHA-256 Encryption for HMAC
import hmac # HMAC Encryption
import os


# Environment to access OS level variables
env = os.environ
# Base API endpoint
BASE = 'https://api.binance.com/api'


# Generate hash-signed request
def __signed_request(endpoint):
    # Timestamp preliminary for request params
    timestamp = int(requests.get(f'{BASE}/v1/time').json()['serverTime'])

    # Request parameters
    params = {'timestamp': timestamp}

    # HMAC SHA-256 encryption using secret key for payload
    hashsign = hmac.new(
        env.get('BINANCE_SECRET').encode('UTF-8'),
        urlencode(params).encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Add encrypted signature to headers
    params['signature'] = hashsign

    # Add public API key to request headers
    headers = {'X-MBX-APIKEY': env.get('BINANCE_KEY')} 

    # Return request json
    return requests.get(
        endpoint,
        params=params,
        headers=headers
    ).json()


# Returns the USDT equivalent of a crypto amount
def __convert_to_USDT(ticker, amount):
    # If already USDT, don't convert
    if ticker == 'USDT':
        return amount
    
    # Get conversion rate for ticker
    conv_rate = requests.get(
        f'{BASE}/v3/ticker/price',
        params={'symbol': f'{ticker}USDT'}
    ).json()

    # Raise Exception if API side error
    if 'code' in conv_rate:
        raise ApiError(f"{ticker}: {conv_rate['msg']}")

    # Get converted rate if no error. Float wrapped just in case
    return float(conv_rate['price']) * amount
        



# Get account balances
def get_balances():
    # Endpoint for account info
    url = f'{BASE}/v3/account'

    # Request resulting json
    result = __signed_request(url)

    # TODO: Universal return type to handle error
    # Handle error
    if 'code' in result:
        raise ApiError(result['msg'])

    # If no error, get balances
    result = result['balances']

    # ---- All coin balances stored here  ---- #
    # Format: [TICKER, AMOUNT, USDT EQUIV.] #
    # Locked assets are those that are locked in unfulfilled, open orders.
    free_assets = []
    locked_assets = []

    # Populate `assets`
    for coin in result:
        # Extract details
        symbol = coin['asset']
        free, locked = float(coin['free']), float(coin['locked'])   

        # Add to lists if non-empty
        if free != 0:
            free_assets.append([symbol, free, __convert_to_USDT(symbol, free)])
        if locked != 0:
            locked_assets.append([symbol, locked, __convert_to_USDT(symbol, locked)])
    
    # Key to sort by third element (i.e.)
    sort_key = lambda x: x[2]
    
    # Sort coins by highest USDT value
    free_assets.sort(key=sort_key, reverse=True)
    locked_assets.sort(key=sort_key, reverse=True)

    # Return both lists, sorted
    return free_assets, locked_assets