# 🪄 Magick: Your Offline Image Superpower

**Stop uploading your photos to random websites just to resize them.**

**Magick** is a free, private, and offline tool that lives on your computer. It lets you resize, convert, and optimize images instantly—without ads, without waiting, and without losing quality.

---

---

## ⚡ Quick Start

### 1. Install (Windows)
Download **`install_magic.bat`** from the Releases page, right-click, and **Run as Administrator**.
*(This automatically installs the latest version and keeps it updated.)*

### 🐧 Linux / Raspberry Pi
Run this one-liner to install everything:
```bash
curl -sL https://raw.githubusercontent.com/absaralam/magic-image-cli/main/install_magic.sh | sudo bash
```
*(Installs ImageMagick, Python deps, and creates the `magic` command)*

### Option C: Developer Setup (Source)
If you downloaded the source code:
Right-click **`setup_magic.bat`** and choose **Run as Administrator**.

### 2. Use
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

### "I want to process an image from my Clipboard"
1. Copy an image (Ctrl+C) from a website or screenshot.
2. Run:
```bash
magic --clipboard 1080p
```
> **Result:** The image from your clipboard is saved and resized instantly.

### "I want a 'Magic Folder' that does it automatically"
```bash
magic --watch 1080p format png
```
> **Result:** The tool watches the folder. **Drag and drop** any file in, and it automatically converts it to a 1080p PNG.

---

## 🧩 Cheat Sheet

| Feature | Command Option | Example |
| :--- | :--- | :--- |
| **Resize (Preset)** | `720p`, `1080p`, `4k` | `magic photo.jpg 4k` |
| **Resize (Custom)** | `WxH` | `magic photo.jpg 800x600` |
| **Smart Crop** | `--crop` | `magic 500x500 --crop photo.jpg` |
| **Convert Format** | `format [png/jpg/ico]` | `magic *.png format jpg` |
| **Quality** | `q[40-100]` | `magic *.jpg q80` |
| **Privacy** | `--strip` | `magic *.jpg --strip` |
| **Watch Mode** | `--watch` | `magic --watch` |
| **Clipboard** | `--clipboard` | `magic --clipboard` |

---

## ❓ FAQ

**Q: Does this upload my photos?**
**A: No.** Everything happens 100% offline on your computer. Your photos never leave your drive.

**Q: What formats are supported?**
**A:** JPG, PNG, WebP, BMP, TIFF, GIF, and ICO.

---

**Made with ❤️ for efficiency.**