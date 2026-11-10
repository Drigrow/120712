import asyncio
import json
import os
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

def load_existing():
    if not os.path.exists(OUT_FILE):
        return []
    try:
        with open(OUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def extract_local_cover(item):
    media = item.get('media') or []
    for m in media:
        if m.get('type') == 'video' and isinstance(m.get('cover_url'), str):
            url = m['cover_url']
            if url.startswith('assets/data/images/'):
                local_path = os.path.join(BASE_DIR, url.replace('/', os.sep))
                if os.path.exists(local_path):
                    return url
    return None

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

async def fetch_bilibili_videos(existing_by_id):
    """Fetch recent Bilibili videos using the bilibili_api."""
    print("Fetching Bilibili videos...")
    results = []
    
    # Luo Tianyi account UID
    u = user.User(uid=36081646)
    
    try:
        # Fetching latest videos (slightly more for safety)
        resp = await u.get_videos(ps=12)
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
                
            item_id = f"bili_v_{bvid}"
            existing = existing_by_id.get(item_id)
            local_cover = extract_local_cover(existing) if existing else None
            if not local_cover:
                local_cover = download_image(pic, 'bili_vid')
            
            results.append({
                'id': item_id,
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

def cleanup_unused_images(kept_items):
    used = set()
    for item in kept_items:
        media = item.get('media') or []
        for m in media:
            if m.get('type') == 'video' and isinstance(m.get('cover_url'), str):
                url = m['cover_url']
                if url.startswith('assets/data/images/'):
                    used.add(url)
    for name in os.listdir(IMG_DIR):
        if not name.startswith('bili_vid_'):
            continue
        rel = f"assets/data/images/{name}"
        if rel in used:
            continue
        try:
            os.remove(os.path.join(IMG_DIR, name))
            print(f"Removed unused cover {name}")
        except Exception as e:
            print(f"Failed to remove {name}: {e}")

def main():
    print("Starting crawler (Bilibili Video Mode)...")

    existing = load_existing()
    existing_by_id = {item.get('id'): item for item in existing if isinstance(item, dict)}

    all_data = sync(fetch_bilibili_videos(existing_by_id))

    # Sort and keep latest 10
    all_data.sort(key=lambda x: x['timestamp'], reverse=True)
    all_data = all_data[:10]

    # Cleanup unused local covers for dropped items
    cleanup_unused_images(all_data)
    
    # Save JSON list (for potential future JS fallback)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    # Generate Static HTML Snippet
    snippet_file = os.path.join(ASSETS_DIR, 'updates_snippet.html')
    html_snippet = ""
    json_ld_videos = []

    for item in all_data:
        media_html = ""
        v = None
        if item.get('media'):
            v = next((m for m in item['media'] if m['type'] == 'video'), None)
            if v:
                cover = v.get('cover_url') or 'assets/images/lt_v5_3view.jpg'
                media_html = f"""
                <a href="{item['url']}" target="_blank" class="u-video-block">
                    <img src="{cover}" class="u-video-cover" alt="{v.get('title', 'video')}">
                    <div class="u-video-play">▶</div>
                    <div class="u-video-title" style="font-family:var(--font-sans)">{v.get('title', 'Video')}</div>
                </a>"""
        
        # Build JSON-LD VideoObject
        if v:
            json_ld_videos.append({
                "@context": "https://schema.org",
                "@type": "VideoObject",
                "name": v.get('title', item['content']),
                "description": item['content'],
                "thumbnailUrl": v.get('cover_url'),
                "uploadDate": datetime.fromtimestamp(item['timestamp']).isoformat(),
                "contentUrl": item['url'],
                "embedUrl": item['url']
            })

        # Build card HTML for ALL items (not just video ones)
        content_html = item['content'].replace('\n', '<br>')
        card_html = f"""
        <div class="u-card mono">
          <div class="u-head">
            <div class="u-meta">
              <span class="u-author">{item['author']}</span>
              <span class="u-plat">[ {item['platform'].upper()} ]</span>
            </div>
            <span class="u-date">{item['date']}</span>
          </div>
          <div class="u-body" style="font-family:var(--font-sans)">
            {content_html}
          </div>
          {media_html}
          <a href="{item['url']}" target="_blank" class="u-link">
            &gt;&gt; <span class="zh">查看原文</span><span class="en">Source Link</span>
          </a>
        </div>
        """
        html_snippet += card_html

    # Save HTML snippet
    with open(snippet_file, 'w', encoding='utf-8') as f:
        f.write(html_snippet)

    # Save JSON-LD
    schema_file = os.path.join(ASSETS_DIR, 'updates_schema.json')
    with open(schema_file, 'w', encoding='utf-8') as f:
        json.dump(json_ld_videos, f, ensure_ascii=False, indent=2)

    # ---------------------------------------------------------
    # Update updates.html with dynamic Twitter/OG cards
    # ---------------------------------------------------------
    updates_file = os.path.join(BASE_DIR, 'updates.html')
    if os.path.exists(updates_file):
        try:
            with open(updates_file, 'r', encoding='utf-8') as f:
                content = f.read()

            import re
            
            # Extract top 3 covers
            top_covers = []
            for item in all_data:
                if item.get('media'):
                    v = next((m for m in item['media'] if m['type'] == 'video'), None)
                    if v and v.get('cover_url'):
                        top_covers.append(v['cover_url'])
                if len(top_covers) >= 3:
                     break
                     
            if not top_covers:
                 top_covers = ['assets/images/lt_main.png']

            # Remove existing image tags
            content = re.sub(r'<meta property="og:image".*?>\n?', '', content)
            content = re.sub(r'<meta name="twitter:image".*?>\n?', '', content)

            # Build new tags
            new_tags = ""
            for cover in top_covers:
                 # Ensure we use an absolute URL if it's a local path
                 if cover.startswith(('assets/', 'images/')):
                     full_url = f"https://120712.com/{cover}"
                 else:
                     full_url = cover
                 new_tags += f'  <meta property="og:image" content="{full_url}" />\n'
                 new_tags += f'  <meta name="twitter:image" content="{full_url}" />\n'

            # Inject right before the video schema tag to maintain head structure
            content = content.replace('  <!-- Load VideoObject schema', new_tags + '  <!-- Load VideoObject schema')

            with open(updates_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Injected {len(top_covers)} dynamic meta images into updates.html.")
        except Exception as e:
            print(f"Failed to update updates.html meta tags: {e}")

    print(f"Done. Saved {len(all_data)} items (JSON, HTML snippet, Schema).")

if __name__ == '__main__':
    main()
