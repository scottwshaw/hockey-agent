# Twilio SMS Setup Guide

## 1. Create a Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free trial account
3. Verify your phone number (this will be the number that receives SMS)

## 2. Get Your Credentials

After signing up, you'll need three pieces of information from your Twilio console (https://console.twilio.com):

### Account SID and Auth Token
- Found on your dashboard homepage
- Look for "Account Info" section
- Copy your **Account SID** and **Auth Token**

### Phone Numbers
- **From Phone**: Get a Twilio phone number
  - Go to Phone Numbers → Manage → Buy a number
  - For trial accounts, you get one free number
  - Must include country code (e.g., `+61412345678` for Australia, `+12025551234` for USA)

- **To Phone**: Your personal phone number
  - Must include country code (e.g., `+61412345678`)
  - For trial accounts, this must be the verified number you signed up with

## 3. Configure Your .env File

Edit your `.env` file and update these settings:

```bash
# Change notification method to SMS
NOTIFICATION_METHOD=sms

# Add your Twilio credentials
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_PHONE=+61412345678  # Your Twilio number
TWILIO_TO_PHONE=+61487654321    # Your personal number
```

## 4. Test It

Run the test scraper to make sure SMS works:

```bash
python test_scraper.py
```

If there are any new sessions, you should receive an SMS!

## Important Notes

### Trial Account Limitations
- **Free credits**: Trial accounts get some free credit (usually $15 USD)
- **Verified numbers only**: Can only send SMS to phone numbers you've verified
- **SMS cost**: Approximately $0.01-0.02 USD per message
- **Message prefix**: Trial messages start with "Sent from your Twilio trial account"

### Upgrading to Paid Account
Once you've used your trial credits or want to remove restrictions:
1. Go to https://console.twilio.com
2. Click "Upgrade" in the top navigation
3. Add payment method
4. No monthly fees - just pay per message

### Estimated Costs
If you check every 30 minutes:
- 48 checks per day
- If you get 1 notification per day = ~$0.01/day = $0.30/month
- If you get 5 notifications per week = ~$0.50/month

Very affordable! 💰

## Troubleshooting

### "Unable to create record: The 'To' number is not a valid phone number"
- Make sure your phone number includes the country code
- Format: `+61412345678` (not `0412345678`)

### "Authenticate"
- Double-check your Account SID and Auth Token
- Make sure there are no extra spaces in your .env file

### "Permission Denied" or "Trial account"
- You can only send to verified numbers with a trial account
- Verify your number at https://console.twilio.com/us1/develop/phone-numbers/manage/verified

### Not receiving SMS
- Check your phone can receive international SMS (if Twilio number is from different country)
- Check the Twilio console logs for delivery status
- Try sending a test message from the Twilio console first
