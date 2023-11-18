import asyncio
import json
import os

import boto3

from tools.telegram_helper import send_alert

lambda_client = boto3.client('lambda')

command_mappings = {
    '/update': os.environ['PORTFOLIO_ALERT_FUNCTION_NAME']
    # Add more commands here
}


def lambda_handler(event, context):
    # Retrieve the secret token from the header
    secret_token = event['headers'].get('X-Telegram-Bot-Api-Secret-Token')
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    user_id = os.environ['TELEGRAM_USER_ID']

    # Verify the secret token
    if secret_token == os.environ['TELEGRAM_SECRET_TOKEN']:
        # Process the request
        # Preprocess and decide which Lambda to call
        print(event)
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', {}).get('text', 'NONE')
        if message[0] != '/':
            alert_message = 'Message commands must begin with "/"'
            asyncio.run(send_alert(bot_token, user_id, alert_message))
            return {
                'statusCode': 200,
                'body': alert_message
            }

        target_lambda = command_mappings.get(message.split()[0])  # Get the command part

        if not target_lambda:
            alert_message = f'Not a valid command. Try {", ".join(command_mappings.keys())}'
            asyncio.run(send_alert(bot_token, user_id, alert_message))
            return {
                'statusCode': 200,
                'body': alert_message
            }


        # Invoke the target Lambda function
        response = lambda_client.invoke(
            FunctionName=target_lambda,
            InvocationType='Event',  # Asynchronous invocation
            Payload=json.dumps(event)
        )
        return {
            'statusCode': 200,
            'body': 'Webhook received and verified successfully'
        }
    else:
        # If the token doesn't match, return an unauthorized response
        alert_message = 'Unauthorized Webhook'
        asyncio.run(send_alert(bot_token, user_id, alert_message))
        return {
            'statusCode': 403,
            'body': alert_message
        }

if __name__ == '__main__':
    response = lambda_handler(
        {
            'headers': {'X-Telegram-Bot-Api-Secret-Token': 'XXXXXXXXXXXX'},
            'body': '{"message": {"text": "/update"}}',
        }, {})
    response

# {'resource': '/telegram-bot', 'path': '/telegram-bot', 'httpMethod': 'POST', 'headers': {'Accept-Encoding': 'gzip,
# deflate', 'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true',
# 'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer':
# 'false', 'CloudFront-Viewer-ASN': '62041', 'CloudFront-Viewer-Country': 'NL', 'Content-Type': 'application/json',
# 'Host': '06q41xksjf.execute-api.us-east-1.amazonaws.com', 'User-Agent': 'Amazon CloudFront', 'Via': '1.1
# 8428d3ca0a47cd247ba9c371c08ccb6a.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id':
# '-dj0eysI2chFRAwBCVhCcRH_WnAlCxAQgXghEyHArMRQxnmyeO9u5w==', 'X-Amzn-Trace-Id':
# 'Root=1-65584343-79587d9a7fa03d991449ef9d', 'X-Forwarded-For': '91.108.6.114, 18.68.51.117', 'X-Forwarded-Port':
# '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept-Encoding': ['gzip, deflate'],
# 'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': [
# 'false'], 'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'],
# 'CloudFront-Viewer-ASN': ['62041'], 'CloudFront-Viewer-Country': ['NL'], 'Content-Type': ['application/json'],
#  'Host': ['06q41xksjf.execute-api.us-east-1.amazonaws.com'], 'User-Agent': ['Amazon CloudFront'], 'Via': ['1.1
#  8428d3ca0a47cd247ba9c371c08ccb6a.cloudfront.net (CloudFront)'], 'X-Amz-Cf-Id': [
#  '-dj0eysI2chFRAwBCVhCcRH_WnAlCxAQgXghEyHArMRQxnmyeO9u5w=='], 'X-Amzn-Trace-Id': [
#  'Root=1-65584343-79587d9a7fa03d991449ef9d'], 'X-Forwarded-For': ['91.108.6.114, 18.68.51.117'],
#  'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None,
#  'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': None, 'requestContext': {
#  'resourceId': 'nbf1iq', 'resourcePath': '/telegram-bot', 'httpMethod': 'POST', 'extendedRequestId':
#  'Ok9ypH4mIAMEoMA=', 'requestTime': '18/Nov/2023:04:53:23 +0000', 'path': '/Stage/telegram-bot', 'accountId':
#  '047672427450', 'protocol': 'HTTP/1.1', 'stage': 'Stage', 'domainPrefix': '06q41xksjf', 'requestTimeEpoch':
#  1700283203850, 'requestId': '28d92bfb-e8b8-4a2d-b2f2-453cf39b3ead', 'identity': {'cognitoIdentityPoolId': None,
#  'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '91.108.6.114', 'principalOrgId': None,
#  'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None,
#  'userAgent': 'Amazon CloudFront', 'user': None}, 'domainName': '06q41xksjf.execute-api.us-east-1.amazonaws.com',
#  'apiId': '06q41xksjf'}, 'body': '{"update_id":450909901,\n"message":{"message_id":17,"from":{"id":5906803458,
#  "is_bot":false,"first_name":"Sean","language_code":"en"},"chat":{"id":5906803458,"first_name":"Sean",
#  "type":"private"},"date":1700283203,"text":"Test"}}', 'isBase64Encoded': False}
