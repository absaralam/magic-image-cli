# Magic Image CLI

A small command-line helper built around **ImageMagick** and **Python** that makes common image-processing tasks—resizing, format conversion, quality adjustments—simpler and more repeatable.

This script is not an official ImageMagick product; it merely provides a convenient wrapper for users who prefer quick, local, and offline image operations without relying on web-based tools.

## Features

- **Resize easily:** Supports standard resolutions (720p, 1080p, 1440p, 2K, 4K, 8K) or any custom size (e.g., `1200x800`).  
- **Adjust quality:** Compress images using intuitive syntax such as `80%` or `q80`.  
- **Convert formats:** Switch between image formats (`jpg`, `png`, `webp`, etc.) in a single step.  
- **Multiple presets:** Apply several sizes or qualities in one command (`720p,1080p,q80`).  
- **Batch processing:** Use `*` to process all images in a folder automatically.  
- **Padding & stretching:** Fill background to match target dimensions or force aspect-ratio stretch.  
- **Flexible syntax:** Keywords like `format`, `pad`, `stretch`, `-o`, and `--no-logs` can appear in any order.  
- **Offline & private:** Runs entirely on your local machine — no uploads or third-party services.  
- **Simple logs:** Generates an optional `magic_log.txt` file with all processed outputs.

## Installation & Setup

### Requirements
- **Windows 10 or later**
- **Python 3.8+** (automatically handled by the setup script)
- **ImageMagick** command-line tools

### Quick Setup (Recommended)

Simply place the following files in one folder:
- `magic.py`
- `magic.bat`
- `setup_magic.bat`

Then, double-click **`setup_magic.bat`**.  
It will:
1. Ensure Python and ImageMagick are installed.  
2. Add the current folder to your system `PATH`.  
3. Allow the `magic` command to be used from any directory in Command Prompt or PowerShell.

After setup, you can open any folder in the terminal and run:
```bash
magic <arguments>
```

**Example:**
```bash
magic 1080p *.jpg
```
**Explanation:**

- `1080p` → Resize images to 1080 pixels in height (maintains aspect ratio unless forced).
- `*.jpg` → Process all JPEG files in the current folder.
- Processed images will be saved automatically in the `output/` subfolder.

## Usage Examples

### Resize a Single Image
```bash
magic Profile.jpg 1080p
```
- Resizes `Profile.jpg` to 1080p height (aspect ratio preserved).
- Output saved as `output/Profile_x1080.jpg.`

### Resize Multiple Images in a Folder
```bash
magic *.jpg 720p,1080p
```
- Resizes all `.jpg` files in the folder to 720p and 1080p.
- Each resized file is saved in the `output/` folder with appropriate suffixes.

### Adjust Quality
```bash
magic Profile.jpg 1080p q80
```
- Resizes to 1080p and compresses image to 80% quality.
- Output file: `Profile_x1080_Q80.jpg.`

### Convert Formats
```bash
magic *.jpg format png
```
- Converts all `.jpg` images to `.png` format while keeping original dimensions.
- Output saved in `output/` folder.

### Custom Size with Padding
```bash
magic Profile.jpg 1200x800 pad black
```
- Resizes to fit inside 1200x800 while preserving aspect ratio.
- Adds black padding to reach exact dimensions.
- Output: `Profile_1200x800_pad.jpg.`

### Force Stretch
```bash
magic Profile.jpg 1080p stretch
```
- Resizes image to exactly 1080p height ignoring aspect ratio.
- Output: `Profile_x1080_stretch.jpg.`

### Specify Output Folder
```bash
magic *.jpg 720p -o resized
```
- Saves all processed images to `resized/` folder instead of default `output/`.

## Argument Reference / Cheat Sheet

### Image Selection
- `image_name.jpg` → Process a single image
- `*` → Process all images in the current folder (`jpg`, `jpeg`, `png`)

### Resize / Presets
- Standard presets: `720p`, `1080p`, `1440p`, `2k`, `4k`, `8k`
- Custom size: `WIDTHxHEIGHT` (e.g., `1200x800`)
- Force stretch (ignore aspect ratio): `!` or `stretch`

### Quality
- JPEG quality: `q80` or `80%`
- Accepts values from `100%` down to `40%`

### Format Conversion
- `format jpg` or `format png`  
- Multiple formats: `format jpg,png`

### Padding / Filling
- Enable padding: `pad`, `padding`, `fill`, or `filled`
- Optional color: `pad black`, `white pad`, etc.

### Output Folder
- `-o folder_name`, `-output folder_name`, or `-folder folder_name`
- Default output folder: `output/`

### Logging
- Default: writes `magic_log.txt`
- Disable logging: `--no-logs` or `-no-logs`

### Notes
- Arguments can be combined and placed in **any order**:
```bash
magic 720p q80 black pad Profile.jpg -o results
magic q80 720p Profile.jpg pad white -o resized
```
- Multiple presets or formats can be separated by commas: `720p,1080p q80 format jpg,png`

## Contribution, Credits & License

### Contribution
Contributions are welcome! You can:
- Report issues or suggest features via GitHub Issues.
- Fork the repository and submit pull requests for bug fixes or improvements.

### Credits
- **ImageMagick** – Core image processing engine: [https://imagemagick.org](https://imagemagick.org)
- **Python** – Scripting language used for the wrapper: [https://www.python.org](https://www.python.org)

This project is a **convenience wrapper** around ImageMagick and is not affiliated with or endorsed by the ImageMagick team.

### License
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---
