import asyncio
import copy
from datetime import datetime
import json
import os

import boto3

from tools.ameritrade_helper import analyze_tda, get_specified_account_with_aws
from tools.aws_helper import safe_put_item
from tools.telegram_helper import send_alert


# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    # retrieve necessary ids, keys, and tokens
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    user_id = os.environ['TELEGRAM_USER_ID']

    # Create a datetime object to link all data retrieved below
    dataset_datetime = datetime.utcnow().isoformat()
    account = get_specified_account_with_aws()
    copied_dict = copy.deepcopy(account)
    account_analysis = analyze_tda(copied_dict)

    # DynamoDB table name
    table_name = 'Positions'
    table = dynamodb.Table(table_name)
    current_balances_table_name = 'CurrentBalances'
    current_balances_table = dynamodb.Table(current_balances_table_name)

    # Extract positions from the input account
    try:
        positions = account['securitiesAccount']['positions']
        current_balances = account['securitiesAccount']['currentBalances']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Account data was not structured as expected: {account.keys()}'),
            'function': 'PortfolioAlertFunction'
        }

    current_balances['type'] = account['securitiesAccount']['type']
    current_balances['accountId'] = account['securitiesAccount']['accountId']
    current_balances['roundTrips'] = account['securitiesAccount']['roundTrips']
    current_balances['isDayTrader'] = account['securitiesAccount']['isDayTrader']
    current_balances['isClosingOnlyRestricted'] = account['securitiesAccount']['isClosingOnlyRestricted']
    current_balances['accountId'] = account['securitiesAccount']['accountId']
    current_balances['storedTimestamp'] = dataset_datetime

    safe_put_item(current_balances_table, current_balances)

    # Process each position and store in DynamoDB
    for position in positions:
        # Flatten the instrument data into position
        instrument_data = position.pop('instrument', {})
        for key, value in instrument_data.items():
            position[key] = value

        # Add accountId and storedTimestamp to each position
        position['accountId'] = account['securitiesAccount']['accountId']
        position['storedTimestamp'] = dataset_datetime
        # position['storedTimestamp'] = datetime.utcnow().isoformat()

        # Ensure the symbol key exists
        if 'symbol' not in position:
            continue  # Skip positions without a symbol

        # Convert float values to Decimal
        safe_put_item(table, position)


    current_liquidation_value = account['securitiesAccount']['currentBalances']['liquidationValue']
    alert_message = f'Your portfolio has a liquidation value of ${current_liquidation_value:.2f}'
    # TECH DEBT: handle this error so long messages are broken into pieces: telegram.error.BadRequest: Text is too long
    # Run the async function
    asyncio.run(send_alert(bot_token, user_id, alert_message))

    return {
        'statusCode': 200,
        'body': json.dumps({'results': account_analysis}),
        'function': 'PortfolioAlertFunction'
    }


if __name__=='__main__':
    print(lambda_handler({},{}))




