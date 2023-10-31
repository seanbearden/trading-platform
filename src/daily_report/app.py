# from alpha_vantage.techindicators import TechIndicators
# from alpha_vantage.timeseries import TimeSeries
import boto3
# from email import encoders
# from email.mime.base import MIMEBase
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
import json
import os
import tempfile
from tools import get_secret, get_specified_account_with_aws


def lambda_handler(event, context):
    # Parse input
    body = event.get('body', '{}')
    if isinstance(body, str):
        body = json.loads(body)

    account = get_specified_account_with_aws()

    if body:
        return {'statusCode': 200, 'body': 'Report created successfully, but not sent!'}
    else:
        return {
            'statusCode': 400,
            'body': 'ERROR'
        }


if __name__ == '__main__':
    response = lambda_handler(
        {"body": {"report_type": "stock_analysis", "send_email": True, "symbol": "COE"}},
        {})
    response
