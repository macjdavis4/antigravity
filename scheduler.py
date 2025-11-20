#!/usr/bin/env python3
"""Daily data refresh scheduler for NFL Fantasy Agent."""
import schedule
import time
from datetime import datetime
from src.data_fetcher import NFLDataFetcher
import config


def daily_refresh():
    """Perform daily data refresh."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled data refresh...")

    try:
        fetcher = NFLDataFetcher()
        fetcher.full_data_refresh()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data refresh completed successfully!")

    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error during refresh: {e}")


def run_scheduler():
    """Run the scheduler continuously."""
    # Schedule daily refresh at configured time
    schedule.every().day.at(config.REFRESH_TIME).do(daily_refresh)

    print(f"NFL Fantasy Agent Scheduler started!")
    print(f"Data will refresh daily at {config.REFRESH_TIME}")
    print("Press Ctrl+C to stop the scheduler.\n")

    # Run immediately on startup
    daily_refresh()

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped.")
