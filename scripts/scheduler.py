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
    
    data_path = 'assets/data/updates.json'
    
    def check_needs_fetch():
        if not os.path.exists(data_path):
            return True
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list) or len(data) == 0:
                    return True
        except Exception:
            return True # File corrupt or unreadable
        return False

    if check_needs_fetch():
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No data found. Running immediate fetch...")
        try:
            run_crawler()
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Initial fetch complete.")
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: {e}")
            traceback.print_exc()

    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Entering scheduled loop (fetching every 1 hour, monitoring file).")
    
    while True:
        # Sleep for 1 hour, but wake up every 10 seconds to check if data is missing
        iterations = interval_seconds // 10
        for _ in range(iterations):
            time.sleep(10)
            if check_needs_fetch():
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Missing or empty data detected! Fetching immediately...")
                try:
                    run_crawler()
                    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Emergency fetch complete.")
                except Exception as e:
                    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: {e}")
                    traceback.print_exc()

        # Regular scheduled fetch
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled crawl...")
        try:
            run_crawler()
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scheduled crawl complete.")
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error during scheduled crawl: {e}")
            traceback.print_exc()

if __name__ == '__main__':
    # When running normally in the terminal:
    # python scripts/scheduler.py
    #
    # To run in the background on Windows without a console window:
    # pythonw scripts/scheduler.py
    run_scheduler()
