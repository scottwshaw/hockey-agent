"""Scraper for IceHQ website (icehq.com.au)."""

import logging
import time
import json
import html
from datetime import datetime
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from hockey_agent.config import (
    HEADLESS_BROWSER,
    BROWSER_WAIT_TIME,
    MONITOR_DAYS,
    MONITOR_DATES,
    MONITOR_SESSION_TYPES
)

logger = logging.getLogger(__name__)


def _setup_driver():
    """Set up Chrome WebDriver with appropriate options."""
    chrome_options = Options()

    if HEADLESS_BROWSER:
        chrome_options.add_argument('--headless=new')

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def _matches_filter(session_date_str: str) -> bool:
    """
    Check if a session date matches our monitoring criteria.

    Args:
        session_date_str: Date string from the website (e.g., "Tuesday 4th November 11:45am-12:45pm")

    Returns:
        True if session matches our filter criteria
    """
    try:
        session_date_lower = session_date_str.lower()

        # If monitoring specific dates
        if MONITOR_DATES:
            for target_date in MONITOR_DATES:
                # Try multiple matching strategies
                # 1. Direct substring match (e.g., "2025-11-04" in string)
                if target_date in session_date_str:
                    return True

                # 2. Parse the target date and match common formats
                # Handle formats like "4th November", "Nov 4", "November 4th", etc.
                try:
                    from dateutil import parser
                    parsed_target = parser.parse(target_date)

                    # Check for "4th November" format
                    day_with_suffix = f"{parsed_target.day}th"
                    if parsed_target.day == 1 or parsed_target.day == 21 or parsed_target.day == 31:
                        day_with_suffix = f"{parsed_target.day}st"
                    elif parsed_target.day == 2 or parsed_target.day == 22:
                        day_with_suffix = f"{parsed_target.day}nd"
                    elif parsed_target.day == 3 or parsed_target.day == 23:
                        day_with_suffix = f"{parsed_target.day}rd"

                    month_full = parsed_target.strftime("%B").lower()  # "november"
                    month_short = parsed_target.strftime("%b").lower()  # "nov"

                    # Check various combinations
                    if day_with_suffix.lower() in session_date_lower and month_full in session_date_lower:
                        return True
                    if day_with_suffix.lower() in session_date_lower and month_short in session_date_lower:
                        return True
                    if f"{parsed_target.day} {month_full}" in session_date_lower:
                        return True
                    if f"{parsed_target.day} {month_short}" in session_date_lower:
                        return True
                    if f"{month_full} {parsed_target.day}" in session_date_lower:
                        return True
                    if f"{month_short} {parsed_target.day}" in session_date_lower:
                        return True

                except:
                    # If dateutil is not available or parsing fails, continue
                    pass

        # If monitoring specific days of week (only check if specific dates didn't match)
        if MONITOR_DAYS:
            session_date_lower = session_date_str.lower()
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

            for day_num in MONITOR_DAYS:
                if day_names[day_num] in session_date_lower:
                    return True

        # If no filters configured, accept all
        if not MONITOR_DATES and not MONITOR_DAYS:
            return True

        return False

    except Exception as e:
        logger.warning(f"Error parsing date '{session_date_str}': {e}")
        return False


def scrape_icehq(url: str, name: str) -> List[Dict[str, str]]:
    """
    Scrape IceHQ website for available hockey sessions.

    Args:
        url: The URL to scrape
        name: The name of the site (for logging)

    Returns:
        List of session dictionaries with 'session_type', 'date_time', 'status', 'site', 'url' keys
    """
    sessions = []
    driver = None

    try:
        logger.info(f"Checking {name} with Selenium...")
        driver = _setup_driver()
        driver.get(url)

        # Wait for page to load and JavaScript to execute
        time.sleep(5)

        # Find all product blocks
        product_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.product-block')

        if not product_blocks:
            logger.warning(f"No product blocks found on {name}")
            return sessions

        logger.info(f"Found {len(product_blocks)} product block(s) on {name}")

        # Process each product block
        for idx, product_block in enumerate(product_blocks):
            try:
                # Get the session type from the heading
                session_type = "Unknown"
                try:
                    heading = product_block.find_element(By.CSS_SELECTOR, 'h1, h2, h3, .product-title')
                    session_type = heading.text.strip()
                except:
                    logger.debug(f"Could not find heading for product block {idx}")
                    pass

                # Check if this session type matches our filters
                session_type_lower = session_type.lower()
                if MONITOR_SESSION_TYPES:
                    if not any(monitored_type in session_type_lower for monitored_type in MONITOR_SESSION_TYPES):
                        logger.debug(f"Skipping '{session_type}' - not in monitored types")
                        continue

                # Get the data-product attribute
                data_product = product_block.get_attribute('data-product')
                if not data_product:
                    logger.warning(f"No data-product attribute found for '{session_type}'")
                    continue

                # Unescape HTML entities and parse JSON
                try:
                    # Unescape &quot; etc.
                    unescaped_json = html.unescape(data_product)
                    product_data = json.loads(unescaped_json)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON for '{session_type}': {e}")
                    logger.debug(f"Raw data: {data_product[:200]}...")
                    continue

                # Extract variants (each variant is a session date/time)
                variants = product_data.get('variants', [])
                logger.info(f"Processing '{session_type}' with {len(variants)} variant(s)")

                for variant in variants:
                    # Get the date/time from attributes
                    date_time = variant.get('attributes', {}).get('Date/time', '')
                    if not date_time:
                        logger.debug(f"Variant missing Date/time attribute: {variant}")
                        continue

                    # Get availability status
                    is_sold_out = variant.get('soldOut', False)
                    qty_in_stock = variant.get('qtyInStock', 0)

                    # Apply date/day filters
                    if not _matches_filter(date_time):
                        continue

                    status = 'SOLD OUT' if is_sold_out else 'AVAILABLE'

                    sessions.append({
                        'session_type': session_type,
                        'date_time': date_time,
                        'status': status,
                        'site': name,
                        'url': url,
                        'qty_in_stock': qty_in_stock
                    })

                    logger.debug(f"  {status} ({qty_in_stock} spots): {date_time}")

            except Exception as e:
                logger.error(f"Error processing product block {idx}: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                continue

        logger.info(f"Found {len(sessions)} matching sessions on {name}")

    except Exception as e:
        logger.error(f"Error scraping {name}: {e}")
        import traceback
        logger.debug(traceback.format_exc())

    finally:
        if driver:
            driver.quit()

    return sessions
