# Generate a Daily Report
Using AWS SAM with Lambda.

Must use Python 3.8 for tda-api. 

## Outline
1. Store TDA_API_KEY and TDA_ACCOUNT_ID in parameter store.
2. Store td ameritrade token.json in AWS Secrets Manager as AMERITRADE_TOKEN_JSON. (Use client_from_login_flow or 
   easy_client to obtain.)
