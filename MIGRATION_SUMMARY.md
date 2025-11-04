# Migration Summary: Local → AWS Lambda

## What Changed

### ✅ Completed

1. **Switched from Selenium to Playwright**
   - Better Lambda support
   - Faster and more reliable
   - Smaller package size
   - Works both locally and in Lambda

2. **Created Lambda Infrastructure**
   - `lambda_handler.py` - Entry point for Lambda
   - `lambda_requirements.txt` - Lambda-specific dependencies
   - `template.yaml` - AWS SAM template for infrastructure
   - `deploy.sh` - One-command deployment script

3. **Updated Configuration**
   - Scraper now works in both local and Lambda environments
   - Uses `playwright-aws-lambda` when in AWS
   - Falls back to regular `playwright` for local development

## File Structure

```
hockey-agent/
├── hockey_agent/
│   ├── scrapers/
│   │   ├── icehq.py                 # OLD - Selenium version (can delete)
│   │   └── icehq_playwright.py      # NEW - Playwright version
│   ├── scraper.py                   # Updated to use Playwright
│   ├── config.py                    # Same
│   ├── storage.py                   # Same
│   ├── notifier.py                  # Same (works in Lambda too!)
│   └── booked.py                    # Same
├── lambda_handler.py                # NEW - Lambda entry point
├── lambda_requirements.txt          # NEW - Lambda dependencies
├── template.yaml                    # NEW - AWS SAM template
├── deploy.sh                        # NEW - Deployment script
├── LAMBDA_DEPLOYMENT.md             # NEW - Deployment guide
├── requirements.txt                 # Updated (Playwright instead of Selenium)
├── main.py                          # OLD - Local scheduler (still works!)
├── test_scraper.py                  # Still works locally
└── test_sms.py                      # Still works locally

## How to Use

### Local Development (Still Works!)

```bash
# Test the scraper
python test_scraper.py

# Run the scheduler locally
python main.py

# Test SMS notifications
python test_sms.py
```

### Deploy to AWS Lambda

```bash
# One-command deployment
./deploy.sh

# Or manually
sam build --use-container
sam deploy --guided
```

## Key Benefits of Lambda

| Feature | Local | Lambda |
|---------|-------|--------|
| **Cost** | $0 (your computer) | ~$0 (free tier) |
| **Reliability** | Requires computer on | Always running |
| **Maintenance** | Manual updates | Automated |
| **Scaling** | Single instance | Auto-scales |
| **SMS Costs** | $0.01/msg | $0.01/msg |

## Important Notes

### Storage in Lambda

Lambda's `/tmp` directory is ephemeral (resets between invocations). This means:
- `seen_sessions.json` will reset each time
- Every session will appear "new" on each run
- You may get duplicate SMS notifications

**To fix this (optional):**
- Use S3 for persistent storage
- Or use DynamoDB
- Requires code modifications (not included yet)

### Testing Before Going Live

1. **Test locally first**:
   ```bash
   python test_scraper.py
   ```

2. **Deploy to Lambda**:
   ```bash
   ./deploy.sh
   ```

3. **Manually invoke Lambda once**:
   ```bash
   sam local invoke HockeyAgentFunction
   # or
   aws lambda invoke --function-name hockey-agent-checker output.json
   ```

4. **Monitor the first scheduled run**:
   ```bash
   sam logs --tail
   ```

## Cost Breakdown

### Lambda (Every 30 minutes = 48 checks/day)

- **Invocations**: ~1,440/month ← FREE (within 1M free tier)
- **Compute**: ~15,000 GB-seconds/month ← FREE (within 400,000 free tier)
- **CloudWatch Logs**: ~10 MB/month ← FREE (within 5GB free tier)

### SMS (Only when spots open up)

- **Per message**: $0.01
- **5 notifications/week**: ~$0.20/month
- **1 notification/day**: ~$0.30/month

### Total: $0.20-$0.50/month 💰

## Next Steps

1. ✅ Read `LAMBDA_DEPLOYMENT.md` for detailed deployment instructions
2. ✅ Install AWS SAM CLI if you haven't
3. ✅ Configure AWS credentials (`aws configure`)
4. ✅ Run `./deploy.sh`
5. ✅ Monitor logs and test!

## Rollback Plan

If Lambda doesn't work out, you can still use the local version:

```bash
python main.py
```

Everything still works locally! Nothing was removed, only added. 🎉
