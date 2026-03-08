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
| 🎵 Local Music Player | Reads MP3s from `./music/`, parses `<title>-<artist>.mp3` filenames |
| 📱 Responsive | Portrait (mobile) + Landscape (desktop) optimised layouts |
| ⚡ Zero dependencies | No frameworks, no npm, just static files |

---

## 🗂️ Project Structure

```
120712.com/
├── index.html                 # Main page
├── generate_music_list.py     # Script: rebuild music/index.json
├── music/
│   ├── index.json             # Auto-generated track list
│   └── *.mp3                  # Your local music files (not in .gitignore)
├── assets/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
│       ├── lt_main.png        # Main hero image
│       ├── lt_v3.png          # V3 reference sheet
│       └── lt_v5_3view.jpg    # V5 three-view reference
└── .gitignore
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

## 🖥️ Deployment (VPS)

The site is fully static. Any web server can host it:

```bash
# On your VPS — just pull and the static server handles the rest
git pull
```

The music player reads `music/index.json` — **no directory listing (`autoindex`) needed**. Works with any Nginx / Apache / Caddy configuration.

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
