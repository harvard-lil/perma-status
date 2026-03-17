import requests
import os
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
import logging

logger = logging.getLogger(__name__)
load_dotenv()


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),  # min: min wait time in secs, max: max wait time in secs
    stop=stop_after_attempt(5),  # stop after 5 attempts (1 initial call + 4 retries)
    retry=retry_if_exception_type(requests.RequestException),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def fetch_daily_counts(endpoint, lookback):
    """GET daily link counts; retries on connection/HTTP errors"""
    params = {'lookback_period': lookback}
    headers = {'Authorization': f'ApiKey {os.getenv("PERMA_API_KEY")}', 'Content-Type': 'application/json'}
    timeout = int(os.getenv('REQUEST_TIMEOUT'))
    r = requests.get(endpoint, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()


def get_counts_for_days(days):
    """
    Get the number of captures per day for the given sequence of days.
    Calls the daily link counts endpoint with lookback_period.
    Days with no captures are omitted from the API response and filled as 0.
    """
    endpoint = os.getenv('PERMA_DAILY_LINK_COUNTS_ENDPOINT')
    lookback = len(days)

    data = fetch_daily_counts(endpoint, lookback)
    
    merged = {}
    
    for item in data.get('counts', []):
        merged.update(item)
    
    counts = dict.fromkeys(days, 0)
    
    for day in days:
        if day in merged:
            counts[day] = merged[day]
    return counts
