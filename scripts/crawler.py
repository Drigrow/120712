import asyncio
import json
import os
import time
from urllib.parse import urlparse
from datetime import datetime
import requests
from bilibili_api import user, sync

# Setup directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets', 'data')
IMG_DIR = os.path.join(ASSETS_DIR, 'images')
OUT_FILE = os.path.join(ASSETS_DIR, 'updates.json')

os.makedirs(IMG_DIR, exist_ok=True)

# Common headers for downloads
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def download_image(url, prefix):
    """Downloads an image and returns the local relative path."""
    if not url: return None
    try:
        # Generate a safe filename
        ext = os.path.splitext(urlparse(url).path)[1]
        if not ext: ext = '.jpg'
        filename = f"{prefix}_{abs(hash(url))}{ext}"
        local_path = os.path.join(IMG_DIR, filename)
        rel_path = f"assets/data/images/{filename}"

        if os.path.exists(local_path):
            return rel_path

        print(f"Downloading {url}...")
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            f.write(r.content)
        return rel_path
    except Exception as e:
        print(f"Failed to download image {url}: {e}")
        return None

async def fetch_bilibili_videos():
    """Fetch recent Bilibili videos using the bilibili_api."""
    print("Fetching Bilibili videos...")
    results = []
    
    # Luo Tianyi account UID
    u = user.User(uid=36081646)
    
    try:
        # Fetching latest 10 videos
        resp = await u.get_videos(ps=10)
        vlist = resp.get('list', {}).get('vlist', [])
        
        for v in vlist:
            bvid = v.get('bvid')
            title = v.get('title')
            created = v.get('created')  # timestamp
            pic = v.get('pic')  # cover url
            author = v.get('author')
            
            pub_date = datetime.fromtimestamp(created)
            
            # Use https if not present
            if pic and pic.startswith('//'):
                pic = 'https:' + pic
                
            local_cover = download_image(pic, 'bili_vid')
            
            results.append({
                'id': f"bili_v_{bvid}",
                'platform': 'bilibili',
                'author': author,
                'date': pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': created,
                'content': title, # Treat title as content description
                'url': f"https://www.bilibili.com/video/{bvid}",
                'type': 'video',
                'media': [
                    {
                        'type': 'video', 
                        'cover_url': local_cover or pic, 
                        'title': title
                    }
                ]
            })
    except Exception as e:
         print(f"Failed to fetch Bilibili videos: {e}")
         
    return results

def main():
    print("Starting crawler (Bilibili Video Mode)...")
    
    all_data = sync(fetch_bilibili_videos())
    
    # Combined and sort
    all_data.sort(key=lambda x: x['timestamp'], reverse=True)
    
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
        
    print(f"Done. Saved {len(all_data)} items to {OUT_FILE}.")

if __name__ == '__main__':
    main()
