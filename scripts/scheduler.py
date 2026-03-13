import time
import datetime
import traceback
import os
import json
from crawler import main as run_crawler

def run_scheduler():
    print("Starting Bilibili Video Crawler Scheduler...")
    print("This script will automatically fetch new videos every hour.\n")
    
    interval_seconds = 3600 # 1 hour
    
    # Check if we need an immediate initial fetch
    data_path = 'assets/data/updates.json'
    needs_initial_fetch = True
    
    if os.path.exists(data_path):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    needs_initial_fetch = False
        except Exception:
            pass # File might be corrupt or unreadable, do fetch
            
    if needs_initial_fetch:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No data found. Running immediate fetch...")
        try:
            run_crawler()
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Initial fetch complete.")
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error during initial fetch: {e}")
            traceback.print_exc()
            
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Entering scheduled loop. Next run in 1 hour.")
    
    while True:
        time.sleep(interval_seconds)
        now = datetime.datetime.now()
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled crawl...")
        
        try:
            run_crawler()
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Crawl complete.")
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error during crawl: {e}")
            traceback.print_exc()
            print("Will retry in 1 hour.")

if __name__ == '__main__':
    # When running normally in the terminal:
    # python scripts/scheduler.py
    #
    # To run in the background on Windows without a console window:
    # pythonw scripts/scheduler.py
    run_scheduler()
