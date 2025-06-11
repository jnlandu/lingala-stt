#!/usr/bin/env python3
"""
Schedule regular downloads from Radio Okapi
Usage: python schedule_okapi.py --interval daily
"""
import subprocess
import time
import argparse
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_download():
    """Run the download script"""
    cmd = [
        'python', 'download_okapi.py',
        '--out', 'data/raw/radio_okapi',
        '--pages', '5',  # Check last 5 pages
        '--metadata',
        '--manifest', 
        '--incremental'  # Only download new files
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            logger.info("✅ Download completed successfully")
            logger.info(result.stdout)
        else:
            logger.error(f"❌ Download failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("❌ Download timed out after 5 minutes")
    except Exception as e:
        logger.error(f"❌ Download error: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', choices=['hourly', 'daily', 'weekly'], 
                       default='daily', help='Download interval')
    parser.add_argument('--once', action='store_true', 
                       help='Run once and exit')
    args = parser.parse_args()

    intervals = {
        'hourly': 3600,    # 1 hour
        'daily': 86400,    # 24 hours  
        'weekly': 604800   # 7 days
    }

    if args.once:
        logger.info("Running single download...")
        run_download()
        return

    interval_seconds = intervals[args.interval]
    logger.info(f"Starting scheduler with {args.interval} interval ({interval_seconds}s)")

    while True:
        logger.info(f"Starting scheduled download at {datetime.now()}")
        run_download()
        
        logger.info(f"Sleeping for {interval_seconds}s until next run...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()