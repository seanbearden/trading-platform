
## Set Webhook
```bash
curl -X POST -F "url=https://<ServerlessRestApi>.execute-api.<AWS_REGION>.amazonaws.com/Stage/telegram-bot" -F 
"secret_token=secret_token" https://api.telegram.org/bot<TOKEN>/setWebhook
```

## Delete Webhook and Pending Updates
```bash
curl -X POST -F "drop_pending_updates=True" https://api.telegram.org/bot<TOKEN>/deleteWebhook
```

## Get Info
```bash
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```