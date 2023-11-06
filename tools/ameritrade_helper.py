import boto3
import json
import logging
import os
import requests
# from selenium import webdriver
from tda import auth, client, orders
import tempfile
from tools.requests_helper import json_from_response
from tools.aws_helper import get_secret


def tda_auth(api_key,
             chrome_driver_path=None,
             token_path='./res/token.json',
             redirect_uri='https://localhost:8895'
             ):
    try:
        c = auth.client_from_token_file(token_path, api_key)
    except FileNotFoundError:
        # if chrome_driver_path:
        #     with webdriver.Chrome(executable_path=chrome_driver_path) as driver:
        #         c = auth.client_from_login_flow(
        #             driver, api_key, redirect_uri, token_path)
        # else:
        raise Exception('TD Ameritrade credentials cannot be found. Try using Chromedriver to generate them.')
    return c


def get_quote(symbol, tda_auth_func=tda_auth, **kwargs):
    client_ = tda_auth_func(**kwargs)
    response = client_.get_quote(symbol)
    data = json_from_response(response)
    return data


def get_quotes(symbols, tda_auth_func=tda_auth, **kwargs):
    tda_client = tda_auth_func(**kwargs)
    return get_quotes_with_client(tda_client, symbols)


def get_quotes_with_client(tda_client, symbols):
    resp = tda_client.get_quotes(symbols)
    return resp.json()


def get_accounts(tda_auth_func=tda_auth, **kwargs):
    client_ = tda_auth_func(**kwargs)
    response = client_.get_accounts()
    data = json_from_response(response)
    return data


def get_specified_account(account_id, tda_auth_func=tda_auth, **kwargs):
    client_ = tda_auth_func(**kwargs)
    response = client_.get_account(account_id, fields=client.Client.Account.Fields.POSITIONS)
    data = json_from_response(response)
    return data


def verify_entry(symbol, tda_api_key):
    symbol = symbol.upper()
    try:
        resp = get_quote(symbol, tda_api_key)
    except (requests.RequestException, Exception) as err:  # catch generic Exception here
        logging.error(f"Request failed: {err}")
        return False

    try:
        resp_json = resp.json()
    except ValueError as json_err:
        logging.error(f"JSON decoding failed: {json_err}")
        return False

    if symbol not in resp_json:
        logging.error(f"Symbol {symbol} not found in response")
        return False

    # If we reach this point, everything has gone well
    return True


def get_option_chain(symbol, contract_type, tda_api_key, tda_auth_func=tda_auth, **kwargs):
    client_ = tda_auth_func(tda_api_key)
    if contract_type == 'CALL':
        contract_type = client.Client.Options.ContractType.CALL
    elif contract_type == 'PUT':
        contract_type = client.Client.Options.ContractType.PUT
    else:
        raise ValueError('Invalid value for contract_type. Choose CALL or PUT.')

    underlying_upper = symbol.upper()

    resp = client_.get_option_chain(underlying_upper,
                                    contract_type=contract_type, **kwargs)

    return resp


def verify_contract(symbol, contract_type, tda_api_key, tda_auth_func=tda_auth, **kwargs):
    symbol = symbol.upper()
    try:
        resp = get_option_chain(symbol, contract_type, tda_api_key, tda_auth_func=tda_auth_func, **kwargs)
    except (requests.RequestException, Exception) as err:  # catch generic Exception here
        logging.error(f"Request failed: {err}")
        return False

    try:
        resp_json = resp.json()
    except ValueError as json_err:
        logging.error(f"JSON decoding failed: {json_err}")
        return False

    if symbol != resp_json['symbol']:
        logging.error(f"Symbol {symbol} not found in response")
        return False
    contract_date = kwargs['from_date'].strftime('%Y-%m-%d')
    strike = kwargs['strike']
    if contract_type == 'CALL':
        date_map = resp_json['callExpDateMap']
    elif contract_type == 'PUT':
        date_map = resp_json['putExpDateMap']

    date_keys = [key for key in date_map.keys() if contract_date in key]
    if len(date_keys) == 0:
        logging.error(f"Contract date {contract_date} not found in response")
        return False
    elif len(date_keys) > 1:
        logging.error(f"Contract date {contract_date} has multiple contracts in response")
        return False

    contracts_for_date = date_map[date_keys[0]]
    strike_keys = [key for key in contracts_for_date.keys() if strike == float(key)]

    if len(strike_keys) == 0:
        logging.error(f"Contract strike {strike} not found in response")
        return False
    elif len(strike_keys) > 1:
        logging.error(f"Contract strike {strike} has multiple contracts in response")
        return False

    contract_info = contracts_for_date[strike_keys[0]]
    if len(contract_info) != 1:
        logging.error(f"More than one contract for date and strike.")
        return False

    logging.info('Found matching contract: {}'.format(contract_info[0]['description']))

    # If we reach this point, everything has gone well
    return True


def place_order(account_id, symbol):
    # Build the order spec and place the order
    order = orders.equities.equity_buy_market(symbol, 1)

    r = client.place_order(account_id, order)
    # assert r.status_code == httpx.codes.OK, r.raise_for_status()


def analyze_tda(account):
    investments = {
        'OPTION': {'positions': []},
        'EQUITY': {'positions': []},
        # 'CASH': {'positions': []}
    }

    # sort investments
    for investment in account['securitiesAccount']['positions']:
        asset_type = investment['instrument']['assetType']
        if asset_type in ['OPTION', 'EQUITY']:
            investments[asset_type]['positions'].append(investment)
        else:
            raise Exception(f"Unknown asset type {asset_type}")

    # analyze investments
    for asset_type, details in investments.items():
        total_market_value = sum([investment['marketValue'] for investment in details['positions']])

        if asset_type == 'OPTION':
            long_market_value = sum(
                [investment['marketValue'] for investment in details['positions'] if
                 investment['instrument']['putCall'] == 'CALL'])
            current_day_long_pnl = sum(
                [investment['currentDayProfitLoss'] for investment in details['positions'] if
                 investment['instrument']['putCall'] == 'CALL'])
            short_market_value = sum(
                [investment['marketValue'] for investment in details['positions'] if
                 investment['instrument']['putCall'] == 'PUT'])
            current_day_short_pnl = sum(
                [investment['currentDayProfitLoss'] for investment in details['positions'] if
                 investment['instrument']['putCall'] == 'PUT'])
        elif asset_type == 'EQUITY':
            long_market_value = sum(
                [investment['marketValue'] for investment in details['positions'] if investment['longQuantity'] > 0])
            current_day_long_pnl = sum(
                [investment['currentDayProfitLoss'] for investment in details['positions'] if
                 investment['longQuantity'] > 0])
            short_market_value = sum(
                [investment['marketValue'] for investment in details['positions'] if investment['shortQuantity'] > 0])
            current_day_short_pnl = sum(
                [investment['currentDayProfitLoss'] for investment in details['positions'] if
                 investment['shortQuantity'] > 0])
        # elif asset_type == "CASH":
        #     pass
        else:
            raise Exception(f"Unknown asset type {asset_type}")

        investments[asset_type]['total_market_value'] = total_market_value
        investments[asset_type]['long_market_value'] = long_market_value
        investments[asset_type]['current_day_long_pnl'] = current_day_long_pnl
        investments[asset_type]['short_market_value'] = short_market_value
        investments[asset_type]['current_day_short_pnl'] = current_day_short_pnl
    return investments


def get_specified_account_with_aws():
    secret_name = "AMERITRADE_TOKEN_JSON"
    token_dict, temp_file_path = load_token(secret_name)

    # get api keys
    tda_api_key = os.environ['TDA_API_KEY']
    tda_account_id = os.environ['TDA_ACCOUNT_ID']
    # Now you have a temporary file holding your token.
    # Call the function with the path to this temporary file
    account = get_specified_account(account_id=tda_account_id,
                                    api_key=tda_api_key,
                                    chrome_driver_path=None,
                                    token_path=temp_file_path)

    cleanup_token(temp_file_path, secret_name, token_dict)

    return account


def get_quotes_with_aws(symbols):
    secret_name = "AMERITRADE_TOKEN_JSON"
    token_dict, temp_file_path = load_token(secret_name)

    # get api keys
    tda_api_key = os.environ['TDA_API_KEY']

    # Now you have a temporary file holding your token.
    # Call the function with the path to this temporary file
    quotes = get_quotes(
        symbols,
        api_key=tda_api_key,
        token_path=temp_file_path)

    cleanup_token(temp_file_path, secret_name, token_dict)

    return quotes


def load_token(secret_name, region_name="us-east-1"):
    secret_str = get_secret(secret_name, region_name=region_name)
    token_dict = json.loads(secret_str)

    # Create a temporary file to hold the token
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp_file_path = temp.name
        temp.write(json.dumps(token_dict).encode())
    return token_dict, temp_file_path


def cleanup_token(temp_file_path, secret_name, token_dict):
    # If the function updates the token, save it back to AWS Secrets Manager
    with open(temp_file_path, 'r') as temp:
        updated_token_dict = json.load(temp)
        if updated_token_dict != token_dict:
            boto3_client = boto3.client('secretsmanager')
            boto3_client.put_secret_value(
                SecretId=secret_name,
                SecretString=json.dumps(updated_token_dict)
            )

    # Ensure to delete the temporary file after use
    os.unlink(temp_file_path)
