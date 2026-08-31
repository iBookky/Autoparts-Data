import os
import sys
import asyncio
import datetime
import argparse
from backend.web_scraper import scrape_external_parts

# Recommended Crontab expression for Unix/macOS:
# 0 4 * * * /usr/bin/python3 /Users/ibookky/Autoparts/backend/cron_scheduler.py --now >> /Users/ibookky/Autoparts/cron.log 2>&1

async def run_daily_scrape():
    print(f"[{datetime.datetime.now().isoformat()}] Starting scheduled daily scraping task (04:00 AM job)...")
    # Sample queries to scrape daily to keep system updated
    sample_queries = ["04465-52260", "8-98079-104-0", "52610-TR7-B03"]
    for q in sample_queries:
        try:
            print(f"Scraping for query: {q}")
            results = await scrape_external_parts(q, source_type='SCRAPE_DAILY')
            print(f"Successfully scraped & saved {len(results)} items for query: {q}")
        except Exception as e:
            print(f"Error scraping query '{q}' in cron job: {e}")
    print(f"[{datetime.datetime.now().isoformat()}] Daily scraping task completed successfully.")

async def run_scheduler():
    print("Background scheduler daemon started. Waiting for 04:00 AM...")
    while True:
        now = datetime.datetime.now()
        # Check if it is exactly 04:00 AM
        if now.hour == 4 and now.minute == 0:
            await run_daily_scrape()
            # Sleep for 65 seconds to avoid double triggering within the same minute
            await asyncio.sleep(65)
        # Check every 30 seconds
        await asyncio.sleep(30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Task Scheduler for OEM vs Aftermarket Cross-Reference System")
    parser.add_argument("--now", action="store_true", help="Run the daily scrape task immediately and exit")
    parser.add_argument("--daemon", action="store_true", help="Start the scheduler daemon to run in background")
    args = parser.parse_args()

    if args.now:
        asyncio.run(run_daily_scrape())
    elif args.daemon:
        try:
            asyncio.run(run_scheduler())
        except KeyboardInterrupt:
            print("Scheduler daemon stopped by user.")
    else:
        print("OEM vs Aftermarket Cross-Reference Scheduler")
        print("---------------------------------------------")
        print("Usage:")
        print("  python backend/cron_scheduler.py --now      Run the task immediately")
        print("  python backend/cron_scheduler.py --daemon   Run scheduler daemon in background")
        print("\nTo setup a system cron job, add the following to your crontab (crontab -e):")
        script_path = os.path.abspath(__file__)
        python_executable = sys.executable
        print(f"0 4 * * * {python_executable} {script_path} --now >> {os.path.dirname(script_path)}/cron.log 2>&1")
