"""
AWS Lambda handler for hockey session checker.

This function is triggered by EventBridge (CloudWatch Events) on a schedule.
"""

import json
import logging
import os

# Set up logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Import after logger setup
from hockey_agent.scraper import check_all_sites


def lambda_handler(event, context):
    """
    Lambda handler function called by EventBridge scheduled rule.

    Args:
        event: EventBridge event (contains schedule info)
        context: Lambda context object

    Returns:
        Response with status code and message
    """
    logger.info("Hockey Agent Lambda function started")
    logger.info(f"Event: {json.dumps(event)}")

    try:
        # Run the scraper
        check_all_sites()

        logger.info("Hockey Agent Lambda function completed successfully")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Hockey session check completed successfully'
            })
        }

    except Exception as e:
        logger.error(f"Error in Lambda function: {e}", exc_info=True)

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error checking hockey sessions',
                'error': str(e)
            })
        }
