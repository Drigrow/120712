import time
import datetime
import traceback
from crawler import main as run_crawler

def run_scheduler():
    print("Starting Bilibili Video Crawler Scheduler...")
    print("This script will automatically fetch new videos every hour.\n")
    
    interval_seconds = 3600 # 1 hour
    
    while True:
        now = datetime.datetime.now()
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled crawl...")
        
        try:
            run_crawler()
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Crawl complete. Sleeping for 1 hour.")
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error during crawl: {e}")
            traceback.print_exc()
            print("Will retry in 1 hour.")
            
        time.sleep(interval_seconds)

if __name__ == '__main__':
    # When running normally in the terminal:
    # python scripts/scheduler.py
    #
    # To run in the background on Windows without a console window:
    # pythonw scripts/scheduler.py
    run_scheduler()
