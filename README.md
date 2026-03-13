# 洛天依 · Luo Tianyi — 个人档案站
# Luo Tianyi Profile Site

> *"Fill the world with song"* — 洛天依 / Luo Tianyi

A bilingual (简体中文 / English) futuristic fan-tribute profile page for **Luo Tianyi (洛天依)**, China's first commercial VOCALOID virtual singer. Built with pure HTML · CSS · JavaScript in an ASCII-art terminal aesthetic.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎌 Bilingual | Full Chinese / English toggle, stored in localStorage |
| 🖥️ Futuristic ASCII UI | All decoration rendered with box-drawing characters |
| 🎬 Bilibili Videos | Live updates of latest 10 videos via automated crawler |
| 🎵 Local Music Player | Reads MP3s from `./music/`, parses `<title>-<artist>.mp3` filenames |
| 📱 Responsive | Portrait (mobile) + Landscape (desktop) optimised layouts |
| ⚡ Static Frontend | No frameworks, optimized for edge delivery |

---

## 🗂️ Project Structure

```
├── index.html                 # Main landing page
├── picture.html               # Image gallery / Databank
├── updates.html               # Bilibili video updates feed
├── generate_music_list.py     # Script: rebuild music/index.json
├── music/
│   ├── index.json             # Auto-generated track list
│   └── *.mp3                  # Your local music files
├── scripts/
│   ├── crawler.py             # Scraper for Bilibili video metadata
│   └── scheduler.py           # Hourly loop for the crawler
├── assets/
│   ├── data/
│   │   ├── updates.json       # Generated metadata for the video feed
│   │   └── images/            # Downloaded video thumbnails
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
└── requirements.txt           # Python dependencies (requests, bilibili-api-python)
```

---

## 🚀 Local Development

```bash
# Serve with Python (required — fetch() needs HTTP, can't open index.html directly)
python -m http.server 8712 --directory /path/to/120712.com

# Open browser
http://localhost:8712
```

---

## 🎵 Adding Music

1. Drop MP3 files into `./music/` using the naming convention:

   ```
   曲名-作者名.mp3
   # Examples:
   白鸟过河滩-ilem.mp3
   天上天下-Wowaka.mp3
   ```

2. Regenerate the track index:

   ```bash
   python generate_music_list.py
   ```

3. Commit and push:

   ```bash
   git add music/
   git commit -m "music: add new tracks"
   git push
   ```

---

The site is served as a static frontend. However, the Bilibili video feed requires a background Python service to keep the data fresh.

### Linux Server Deployment
1. **Install Prerequisites**:
   ```bash
   apt update
   apt install python3 python3-pip python3-venv
   ```
2. **Install Dependencies**:
   You have two options depending on your OS version:

   **Option A: Virtual Environment (Recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   *Note: If you use this, update your systemd `ExecStart` to point to `/path/to/venv/bin/python3`.*

   **Option B: System Override (Quickest)**
   ```bash
   pip3 install -r requirements.txt --break-system-packages
   ```

3. **Configure Services**:
   Follow the systemd instructions below to set up the web server and crawler as background services.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Server
Use any static file server (e.g., Python's built-in module):
```bash
# Serves the site at http://localhost:8712
python3 -m http.server 8712
```

### 3. Run the Hourly Crawler (Background)
The crawler fetches the latest 10 videos from Bilibili every hour.
```bash
# Windows
start /B pythonw scripts/scheduler.py

# Linux
nohup python3 scripts/scheduler.py > crawler.log 2>&1 &
```


---

## ⚖️ License & Credits

This project is a **non-commercial fan work** and is released under **[CC BY-NC-SA 4.0](LICENSE)**.

### Character & IP
- **洛天依 (Luo Tianyi)** is a VOCALOID™ character developed by **上海禾念信息科技 (Shanghai Henian Information Technology)**. All character rights belong to their respective owners.
- This site is an unofficial fan tribute and is **not affiliated with Shanghai Henian or Yamaha**.

### Text Content
- Lore and character information is adapted from **[萌娘百科 / Moegirlpedia](https://zh.moegirl.org.cn/洛天依)**.
- Moegirlpedia text is used under **[CC BY-NC-SA 3.0 CN](https://creativecommons.org/licenses/by-nc-sa/3.0/cn/)** as required.

### Images
- Character artwork sourced from official materials hosted on Moegirlpedia.
- No AI-generated images are used in this project.

### Code
- Original HTML / CSS / JavaScript code © the repository author, licensed under **CC BY-NC-SA 4.0**.
