#!/bin/bash

# Hockey Agent Lambda Deployment Script

set -e  # Exit on error

echo "========================================"
echo "Hockey Agent Lambda Deployment"
echo "========================================"
echo ""

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed."
    echo ""
    echo "Please install it first:"
    echo "  macOS: brew install aws-sam-cli"
    echo "  Other: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured."
    echo ""
    echo "Please run: aws configure"
    exit 1
fi

echo "✅ Prerequisites met"
echo ""

# Build
echo "📦 Building Lambda package..."
sam build --use-container

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Build successful"
echo ""

# Deploy
if [ -f samconfig.toml ]; then
    echo "📤 Deploying with saved configuration..."
    sam deploy
else
    echo "📤 First deployment - running guided deploy..."
    echo ""
    echo "You will be prompted for:"
    echo "  - Stack name (e.g., hockey-agent)"
    echo "  - AWS Region (e.g., us-east-1 or ap-southeast-2)"
    echo "  - Twilio credentials"
    echo "  - Phone numbers"
    echo ""
    sam deploy --guided
fi

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed"
    exit 1
fi

echo ""
echo "✅ Deployment successful!"
echo ""
echo "Next steps:"
echo "  1. View logs: sam logs --tail"
echo "  2. Test function: sam local invoke HockeyAgentFunction"
echo "  3. Monitor in AWS Console: https://console.aws.amazon.com/lambda"
echo ""
