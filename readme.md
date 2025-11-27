# 🪄 Magick: Your Offline Image Superpower

**Stop uploading your photos to random websites just to resize them.**

**Magick** is a free, private, and offline tool that lives on your computer. It lets you resize, convert, and optimize images instantly—without ads, without waiting, and without losing quality.

---

---

## ⚡ Quick Start

### 1. Install (Windows)
Download **`install_magic.bat`** from the Releases page, right-click, and **Run as Administrator**.
*(This automatically installs the latest version and keeps it updated.)*

### 2. Python (Universal)
If you have Python installed, just run:
```bash
pip install magic-image-cli
```
*(Works on Windows, and Linux!)*

### 3. Linux / Raspberry Pi
Run this one-liner to install everything:
```bash
curl -sL https://raw.githubusercontent.com/absaralam/magic-image-cli/main/install_magic.sh | sudo bash
```
*(Installs ImageMagick, Python deps, and creates the `magic` command)*

### 4. Developer Setup (Source)
If you downloaded the source code:
Right-click **`setup_magic.bat`** and choose **Run as Administrator**.

### Use
Open any terminal and type:
```bash
magic photo.jpg 1080p
```
*Boom. Your photo is now 1080 pixels high.*

---

## 📖 The "How Do I...?" Guide

### "I want to resize images for social media"
```bash
magic *.jpg 1080p
```
> **Result:** All JPGs in the folder are resized to 1080p height.

### "I want to make a professional Windows Icon"
```bash
magic logo.png format ico
```
> **Result:** Creates a `logo.ico` with all the correct sizes (16x16 up to 256x256) embedded.

### "I want to convert WebP files to PNG"
```bash
magic *.webp format png
```
> **Result:** Converts all those annoying WebP files into usable PNGs.

### "I want to remove hidden data (GPS/Camera) before sharing"
```bash
magic photo.jpg --strip
```
> **Result:** A clean image with no personal metadata attached.

### "I want to watermark my photos"
```bash
magic *.jpg watermark bottom left
```
> **Result:** Adds `watermark.png` (from current folder) to the bottom-left of every image.
> *Note: You can also use `magic *.jpg --watermark logo.png` for specific files.*

### "I want to process an image from my Clipboard"
1. Copy an image (Ctrl+C) from a website or screenshot.

## 🧩 Cheat Sheet

| Feature | Command / Keyword | Example |
| :--- | :--- | :--- |
| **Resize** | `720p`, `1080p`, `WxH` | `magic photo.jpg 1080p` |
| **Force Resize** | `stretch`, `force`, `!` | `magic photo.jpg 100x100 stretch` |
| **Smart Crop** | `crop` | `magic photo.jpg 500x500 crop` |
| **Format** | `format [png/jpg/ico]` | `magic *.webp format png` |
| **Quality** | `quality [0-100]`, `high`, `best` | `magic *.jpg quality 80` |
| **Privacy** | `clean`, `remove metadata` | `magic *.jpg clean` |
| **Watermark** | `watermark`, `wm` | `magic *.jpg wm bottom right` |
| **Output Folder** | `to [folder]`, `to input` | `magic *.jpg to input` |
| **Watch Mode** | `watch`, `monitor` | `magic watch` |
| **Clipboard** | `paste`, `clipboard` | `magic paste` |

---

## ⚙️ Configuration
Want to set your own defaults? (e.g., always watermark, default quality 90)

1.  **Generate a config file:**
    ```bash
    magic --init-config
    ```
    This creates a `.magicrc` file in your current folder.

2.  **Edit `.magicrc`:**
    Open it in any text editor and change the values:
    ```json
    {
        "output_folder": "processed_images",
        "default_quality": 90,
        "watermark": "logo.png"
    }
    ```
    *Now `magic photo.jpg` will automatically use these settings!*

### 🧠 Smart Config Search
Magick looks for `.magicrc` in this order:
1.  **Current Folder:** Overrides everything (Great for specific projects).
2.  **Tool Folder:** Same folder as `magic.exe` or `magic.py` (Great for global defaults).

*Tip: Put a `.magicrc` next to the tool for global settings, and run `magic --init-config` in specific folders to override them.*

---

## 🗣️ Natural Language Examples
Magick understands you. Try these:
- `magic photo.jpg to input` (Save to same folder)
- `magic photo.jpg clean` (Remove metadata)
- `magic paste 1080p` (Paste from clipboard and resize)
- `magic watch format png` (Watch folder and convert new files to PNG)
- `magic photo.jpg 100x100 stretch` (Force exact size, ignore aspect ratio)

---

## ❓ FAQ

**Q: Does this upload my photos?**
**A: No.** Everything happens 100% offline on your computer. Your photos never leave your drive.

**Q: What formats are supported?**
**A:** JPG, PNG, WebP, BMP, TIFF, GIF, and ICO.

---


**Made with ❤️ for efficiency.**
