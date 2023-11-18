
## Set Webhook
```bash
curl -X POST -F "url=https://<ServerlessRestApi>.execute-api.<AWS_REGION>.amazonaws.com/Stage/telegram-bot" -F 
"secret_token=secret_token" https://api.telegram.org/bot<USER_ID>:<TOKEN>/setWebhook
```