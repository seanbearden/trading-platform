# Dispatcher Lambda
Lambda triggered by Telegram bot API post, triggering other lambdas

Create your own secret token.

## Set webhook with secret token

```bash
curl -X POST \
  -F "url=https://<ServerlessRestApi>.execute-api.<REGION>.amazonaws.com/Stage/telegram-bot" \
  -F "secret_token=secret_token" \
  https://api.telegram.org/bot<USER_ID>:<TOKEN>/setWebhook
```

## Get webhook info
```bash
curl https://api.telegram.org/bot<USER_ID>:<TOKEN>/getWebhookInfo
```

## Delete webhook and pending updates
Useful to clear pending updates when debugging.

```bash
curl -X POST \
  -F "drop_pending_updates=True" \
  https://api.telegram.org/bot<USER_ID>:<TOKEN>/deleteWebhook
```