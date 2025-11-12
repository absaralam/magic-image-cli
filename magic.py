import subprocess
import sys
from pathlib import Path
from datetime import datetime

# -------------------------------
# Preset mapping
# -------------------------------
PRESETS = {
    "720p": "x720",
    "1080p": "x1080",
    "1440p": "x1440",
    "2k": "x2160",
    "4k": "x3840",
    "8k": "x7680"
}

# Aliases
PAD_ALIASES = ["pad", "padding", "fill", "filled"]
STRETCH_ALIASES = ["!", "stretch"]
FORMAT_ALIASES = ["format", "formats"]
OUTPUT_ALIASES = ["-o", "-output", "-folder"]
NOLOG_ALIASES = ["--no logs", "-no logs"]

LOG_FILE = "magic_log.txt"

# -------------------------------
# Parse arguments
# -------------------------------
def parse_args():
    args = sys.argv[1:]
    if not args:
        print("Usage: magic <size(s)> <image(s)> [quality(s)] [format(s)] [pad/fill] [stretch] [-o folder] [--no logs]")
        sys.exit(1)

    sizes = []
    images = []
    qualities = [100]
    formats = []
    output_folder = "output"
    pad_mode = False
    pad_color = "white"
    force = False
    log_enabled = True

    for arg in args:
        larg = arg.lower()

        # Sizes / Presets
        if larg in PRESETS:
            sizes.append(larg)
        elif larg.isdigit():  # e.g., 720
            sizes.append(f"x{larg}")
        elif "x" in larg and all(p.isdigit() for p in larg.split("x")):
            sizes.append(larg)

        # Quality
        elif larg.startswith("q") and larg[1:].isdigit():
            qualities = [int(q[1:]) for q in arg.split(",")]
        elif larg.endswith("%") and larg[:-1].isdigit():
            qualities = [int(q[:-1]) for q in arg.split(",")]

        # Format
        elif larg in FORMAT_ALIASES:
            continue  # keyword itself, skip
        elif any(larg.startswith(f"{f},") or larg==f for f in ["jpg","jpeg","png","webp"]):
            formats = [f.strip() for f in arg.split(",")]

        # Pad / Fill
        elif larg in PAD_ALIASES:
            pad_mode = True
        elif any(pad in larg for pad in PAD_ALIASES):
            pad_mode = True
        elif arg not in args[0:1] and pad_mode == False and arg not in PRESETS:
            # Might be pad color
            pad_color = arg

        # Stretch / Force
        elif larg in STRETCH_ALIASES:
            force = True

        # Output folder
        elif larg in OUTPUT_ALIASES:
            continue  # handled next
        elif any(arg.startswith(alias) for alias in OUTPUT_ALIASES):
            continue

        # No logs
        elif larg in NOLOG_ALIASES:
            log_enabled = False

        # Else, assume image
        else:
            images.append(arg)

    if not images:
        images = ["*"]

    if not sizes:
        sizes = ["x720"]

    if not formats:
        formats = [None]  # keep original

    return sizes, images, qualities, formats, output_folder, pad_mode, pad_color, force, log_enabled

# -------------------------------
# Generate safe output filename
# -------------------------------
def safe_filename(base, suffix, ext, folder):
    out_path = Path(folder) / f"{base}{suffix}{ext}"
    counter = 1
    while out_path.exists():
        out_path = Path(folder) / f"{base}{suffix}_v{counter}{ext}"
        counter += 1
    return out_path

# -------------------------------
# Run ImageMagick
# -------------------------------
def run_imagemagick(image_path, resize, quality, fmt, output_folder, pad_mode=False, pad_color="white", force=False, log_enabled=True):
    path = Path(image_path)
    if not path.exists():
        print(f"File {image_path} not found!")
        return

    # Determine resize string
    resize_str = PRESETS.get(resize.lower(), resize)  # preset or WxH
    if force and not resize_str.endswith("!"):
        resize_str += "!"

    # Prepare output folder
    out_dir = Path(output_folder)
    out_dir.mkdir(exist_ok=True)

    # Build output filename
    suffix = f"_{resize_str}"
    if quality != 100:
        suffix += f"_Q{quality}"
    if pad_mode:
        suffix += f"_pad"
    ext = f".{fmt}" if fmt else path.suffix

    outfile = safe_filename(path.stem, suffix, ext, out_dir)

    # Build ImageMagick command
    if pad_mode:
        cmd = [
            "magick", str(path),
            "-resize", resize_str,
            "-background", pad_color,
            "-gravity", "center",
            "-extent", resize_str,
            "-quality", str(quality),
            str(outfile)
        ]
    else:
        cmd = ["magick", str(path), "-resize", resize_str, "-quality", str(quality), str(outfile)]

    print(f"Processing {path.name} -> {outfile.name}")
    subprocess.run(cmd)

    # Logging
    if log_enabled:
        try:
            size = outfile.stat().st_size
            log_file = Path(LOG_FILE)
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"Timestamp: {datetime.now()}\n")
                log.write(f"Input: {path.name}\n")
                log.write(f"Output: {outfile.name}\n")
                log.write(f"Resize: {resize_str}\n")
                log.write(f"Quality: {quality}\n")
                log.write(f"Pad Mode: {pad_mode}, Pad Color: {pad_color}\n")
                log.write(f"Size(Bytes): {size}\n")
                log.write("-" * 40 + "\n")
        except Exception as e:
            print("Logging failed:", e)

# -------------------------------
# Main
# -------------------------------
def main():
    sizes, images_arg, qualities, formats, output_folder, pad_mode, pad_color, force, log_enabled = parse_args()

    # Resolve images
    images = []
    for img in images_arg:
        if img == "*":
            images.extend(list(Path(".").glob("*.[jp][pn]g")))
        else:
            images.append(img)

    # Run all combinations
    for image in images:
        for size in sizes:
            for quality in qualities:
                for fmt in formats:
                    run_imagemagick(image, size, quality, fmt, output_folder, pad_mode, pad_color, force, log_enabled)

    print("All done!")

if __name__ == "__main__":
    main()
