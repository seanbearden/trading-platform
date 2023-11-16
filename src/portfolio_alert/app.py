from datetime import datetime
import json

import boto3

from tools.ameritrade_helper import get_specified_account_with_aws
from tools.aws_helper import convert_floats_to_decimals


# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    # Create a datetime object to link all data retrieved below
    dataset_datetime = datetime.utcnow().isoformat()
    account = get_specified_account_with_aws()

    # DynamoDB table name
    table_name = 'Positions'
    table = dynamodb.Table(table_name)

    # Extract positions from the input account
    try:
        positions = account['securitiesAccount']['positions']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps('No positions found in the input')
        }

    # Process each position and store in DynamoDB
    for position in positions:
        # Flatten the instrument data into position
        instrument_data = position.pop('instrument', {})
        for key, value in instrument_data.items():
            position[key] = value

        # Add accountId and storedTimestamp to each position
        # position['accountId'] = account['securitiesAccount']['accountId']
        position['storedTimestamp'] = dataset_datetime
        # position['storedTimestamp'] = datetime.utcnow().isoformat()

        # Ensure the symbol key exists
        if 'symbol' not in position:
            continue  # Skip positions without a symbol

        # Convert float values to Decimal
        position = convert_floats_to_decimals(position)

        # Store the position in DynamoDB
        try:
            table.put_item(Item=position)
        except Exception as e:
            print(f"Error storing position {position.get('symbol')}: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Positions stored successfully')
    }


if __name__ == '__main__':
    response = lambda_handler({}, {})
    print(response)


