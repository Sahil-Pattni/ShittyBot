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
BASE = 'https://api.binance.com'


# Generate hash-signed request
def __signed_request(endpoint, additional_params=None) -> dict:
    # Timestamp preliminary for request params
    timestamp = int(requests.get(f'{BASE}/api/v1/time').json()['serverTime'])

    # Request parameters
    params = {'timestamp': timestamp}

    if additional_params is not None:
        params.update(additional_params)

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
def __convert_to_USDT(ticker, amount) -> float:
    # If already USDT, don't convert
    if ticker == 'USDT':
        return amount
    
    # Get conversion rate for ticker
    conv_rate = requests.get(
        f'{BASE}/api/v3/ticker/price',
        params={'symbol': f'{ticker}USDT'}
    ).json()

    # If USDT not available, convert to BNB first
    if 'code' in conv_rate:
        bnb_rate = requests.get(
            f'{BASE}/api/v3/ticker/price',
            params={'symbol': f'{ticker}BNB'}
        ).json()

        # ERROR
        if 'code' in bnb_rate:
            raise ApiError(f"{ticker}: {bnb_rate['msg']}")

        # Get BNB USDT conversion rate
        usdt_bnb = requests.get(
            f'{BASE}/api/v3/ticker/price',
            params={'symbol': f'BNBUSDT'}
        ).json()

        # Handle error
        if 'code' in usdt_bnb:
            raise ApiError(f"{ticker}: {usdt_bnb['msg']}")

        # Convert from TICKER to BNB to USDT, adjust for amount
        return amount * float(bnb_rate['price']) * float(usdt_bnb['price'])

    # Get converted rate if no error. Float wrapped just in case
    return float(conv_rate['price']) * amount
        



# Get account balances
def get_balances() -> Tuple[list, list]:
    # Endpoint for account info
    url = f'{BASE}/api/v3/account'
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


# Gets all trades for given ticker
def get_trades(ticker) -> dict:
    url = f'{BASE}/api/v3/allOrders'
    params = {'symbol': ticker}
    result = __signed_request(url, additional_params=params)

    # Handle error
    if ['code'] in result:
        raise ApiError(result['code'])

    return result
    

def profit():
    # Get tradable symbols
    symbols = requests.get(f'{BASE}/api/v3/exchangeInfo').json()['symbols']

    # Format: [FROM_TICKER, TO_TICKER, QTY, PRICE, TIMESTAMP]
    all_trades = []

    # Iterate through all pairs and add to trades if available
    for symb in symbols:
        from_ticker, to_ticker = symb['baseAsset'], symb['quoteAsset']
        trades = get_trades(symb)

        for trade in trades:
            all_trades.append([
                from_ticker,
                to_ticker,
                trade['executedQty'],
                trade['price'],
                trade['time']
            ])
    
    return all_trades