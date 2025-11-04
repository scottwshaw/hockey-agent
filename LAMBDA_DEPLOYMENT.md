# AWS Lambda Deployment Guide

This guide will help you deploy the Hockey Agent as an AWS Lambda function that runs on a schedule.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **AWS SAM CLI** installed (for easy deployment)
4. **Docker** installed (required by SAM for building)

### Install AWS SAM CLI

```bash
# macOS
brew install aws-sam-cli

# Or follow: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
```

### Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1 or ap-southeast-2 for Australia)
```

## Important: Playwright in Lambda

Playwright needs special handling in Lambda. You have two options:

### Option A: Use Playwright with Custom Layer (Recommended for production)

You'll need to create a Lambda Layer with Playwright browsers. This is complex but gives you full control.

### Option B: Use playwright-aws-lambda Package (Easier)

Update `lambda_requirements.txt` to use a pre-packaged Playwright for Lambda:

```txt
playwright-aws-lambda>=0.2.0
twilio>=8.0.0
python-dateutil>=2.8.0
python-dotenv>=1.0.0
```

And update `hockey_agent/scrapers/icehq_playwright.py` to use it:

```python
# At the top of the file
try:
    # Try to use playwright-aws-lambda if in Lambda environment
    from playwright_aws_lambda import sync_playwright
except ImportError:
    # Fall back to regular playwright for local development
    from playwright.sync_api import sync_playwright
```

## Deployment Steps

### Step 1: Update Lambda Requirements

Edit `lambda_requirements.txt` to use `playwright-aws-lambda`:

```txt
playwright-aws-lambda>=0.2.0
twilio>=8.0.0
python-dateutil>=2.8.0
python-dotenv>=1.0.0
```

### Step 2: Update the Scraper for Lambda

The scraper needs a small modification to work in Lambda. Edit `hockey_agent/scrapers/icehq_playwright.py`:

At the very top, change the import:

```python
try:
    from playwright_aws_lambda import sync_playwright
except ImportError:
    from playwright.sync_api import sync_playwright
```

### Step 3: Build and Deploy with SAM

```bash
# Build the Lambda package
sam build --use-container

# Deploy (first time - will prompt for parameters)
sam deploy --guided

# Follow the prompts:
# - Stack Name: hockey-agent
# - AWS Region: us-east-1 (or your preferred region)
# - Parameter CheckIntervalMinutes: 30
# - Parameter MonitorDays: 5,6
# - Parameter MonitorDates: 2025-11-04
# - Parameter MonitorSessionTypes: stick & puck,scrimmage
# - Parameter TwilioAccountSid: ACxxxxxxxxx
# - Parameter TwilioApiKey: SKxxxxxxxxx
# - Parameter TwilioApiSecret: your-secret
# - Parameter TwilioFromPhone: +12297570417
# - Parameter TwilioToPhone: +61402653576
# - Confirm changes before deploy: Y
# - Allow SAM CLI IAM role creation: Y
# - Save arguments to samconfig.toml: Y
```

### Step 4: Subsequent Deploys

After the first deployment, you can just run:

```bash
sam build --use-container
sam deploy
```

## Alternative: Manual Deployment (Without SAM)

If you don't want to use SAM, you can deploy manually:

### 1. Create Deployment Package

```bash
# Create a clean directory
mkdir lambda_package
cd lambda_package

# Install dependencies
pip install -r ../lambda_requirements.txt -t .

# Copy your code
cp -r ../hockey_agent .
cp ../lambda_handler.py .

# Create ZIP file
zip -r ../hockey-agent-lambda.zip .
cd ..
```

### 2. Create Lambda Function via AWS Console

1. Go to AWS Lambda Console
2. Click "Create function"
3. Choose "Author from scratch"
4. Function name: `hockey-agent-checker`
5. Runtime: Python 3.9
6. Architecture: x86_64
7. Click "Create function"

### 3. Upload Code

1. In the function page, go to "Code" tab
2. Click "Upload from" → ".zip file"
3. Upload `hockey-agent-lambda.zip`
4. Click "Save"

### 4. Configure Function

1. **Handler**: Set to `lambda_handler.lambda_handler`
2. **Timeout**: Set to 120 seconds (2 minutes)
3. **Memory**: Set to 1024 MB
4. **Environment variables**: Add all the variables from template.yaml

### 5. Create EventBridge Rule

1. Go to Amazon EventBridge Console
2. Click "Rules" → "Create rule"
3. Name: `hockey-agent-schedule`
4. Rule type: "Schedule"
5. Schedule pattern: "Rate-based schedule"
6. Rate: `30 minutes`
7. Target: Select your Lambda function
8. Click "Create"

## Monitoring

### View Logs

```bash
# Via SAM
sam logs --tail

# Via AWS CLI
aws logs tail /aws/lambda/hockey-agent-checker --follow
```

### Test the Function

```bash
# Invoke manually
sam local invoke HockeyAgentFunction

# Or via AWS CLI
aws lambda invoke --function-name hockey-agent-checker output.json
cat output.json
```

## Cost Estimate

With default settings (check every 30 minutes):
- **Lambda invocations**: ~1,440/month (48/day × 30 days)
- **Lambda duration**: ~10 seconds/invocation = 14,400 seconds/month
- **Lambda cost**: FREE (well within free tier of 400,000 GB-seconds)
- **EventBridge**: FREE (within free tier)
- **SMS costs**: ~$0.01 per message (only when spots open up)

**Total monthly cost**: Essentially just SMS costs (~$0.10-$0.50/month) 💰

## Troubleshooting

### Playwright Errors in Lambda

If you see errors about Chrome not being found:
- Make sure you're using `playwright-aws-lambda`
- Check that the import is correct in the scraper
- Increase memory to 1536 MB if needed

### Timeout Errors

- Increase Lambda timeout to 180 seconds
- Increase `BROWSER_WAIT_TIME` environment variable

### SMS Not Sending

- Check CloudWatch Logs for Twilio errors
- Verify Twilio credentials are correct
- Make sure phone numbers include country code

### Storage Issues

Lambda stores files in `/tmp/` which is ephemeral (resets between invocations). This means:
- `seen_sessions.json` will reset each time
- The function will think all sessions are "new" on each run
- You may get duplicate notifications

**Solution**: Use S3 or DynamoDB for persistent storage (requires code modification).

## Next Steps

1. Monitor logs after deployment
2. Test by manually invoking the function
3. Wait for the first scheduled run
4. Check your phone for SMS notifications!

## Updating the Function

To update after making code changes:

```bash
sam build --use-container
sam deploy
```

That's it! Your hockey agent is now running in the cloud! 🚀🏒
