"""
Magick Image CLI Tool
=====================

A powerful, offline command-line wrapper for ImageMagick and Python.
Handles resizing, format conversion, padding, cropping, and metadata stripping.
Supports clipboard processing and folder watching.

Usage:
    magic <image_path> <size> [options]
    magic --watch
    magic --clipboard

Author: absaralam
License: MIT
"""

import subprocess
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional, Dict, Any, Union

# Third-party imports
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    from PIL import Image, ImageGrab
    from colorama import init, Fore, Style
except ImportError:
    print("Missing dependencies! Please run 'setup_magic.bat' or 'pip install -r requirements.txt'")
    sys.exit(1)

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# -------------------------------
# Constants & Config
# -------------------------------
__version__ = "2.4"

PRESETS: Dict[str, str] = {
    "720p": "x720",
    "1080p": "x1080",
    "1440p": "x1440",
    "2k": "x2160",
    "4k": "x3840",
    "8k": "x7680"
}

LOG_FILE: str = "magick_log.txt"
SUPPORTED_EXTS: set = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif", ".ico"}

# -------------------------------
# Utils
# -------------------------------
def log(msg: str, type: str = "info") -> None:
    """
    Prints a formatted log message to the console with timestamp and color.

    Args:
        msg (str): The message to print.
        type (str): The type of message ('info', 'success', 'warn', 'error').
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN,
        "warn": Fore.YELLOW,
        "error": Fore.RED
    }
    color = colors.get(type, Fore.WHITE)
    print(f"{color}[{timestamp}] {Fore.WHITE}{msg}")

def safe_filename(base: str, suffix: str, ext: str, folder: Path) -> Path:
    """
    Generates a unique filename to avoid overwriting existing files.

    Args:
        base (str): The base filename (without extension).
        suffix (str): The suffix to append (e.g., '_x720').
        ext (str): The file extension (e.g., '.jpg').
        folder (Path): The target directory.

    Returns:
        Path: A unique file path.
    """
    out_path = folder / f"{base}{suffix}{ext}"
    counter = 1
    while out_path.exists():
        out_path = folder / f"{base}{suffix}_v{counter}{ext}"
        counter += 1
    return out_path

# -------------------------------
# Core Processor
# -------------------------------
def get_magick_command() -> str:
    """Detects the available ImageMagick command (magick vs convert)."""
    from shutil import which
    if which("magick"):
        return "magick"
    if which("convert"):
        return "convert"
    return "magick"  # Default fallback

# -------------------------------
# Core Processor
# -------------------------------
class MagickProcessor:
    """
    Handles image processing tasks using ImageMagick.
    """

    def __init__(self, output_folder: str = "output", log_enabled: bool = True):
        """
        Initialize the processor.

        Args:
            output_folder (str): Directory to save processed images.
            log_enabled (bool): Whether to write to the log file.
        """
        self.output_folder = Path(output_folder)
        self.log_enabled = log_enabled
        self.output_folder.mkdir(exist_ok=True)

    def process(self, image_path: Path, sizes: List[str] = None, qualities: List[int] = None, 
                formats: List[Optional[str]] = None, pad: bool = False, pad_color: str = "white", 
                force: bool = False, crop: bool = False, strip: bool = False) -> List[Tuple]:
        """
        Generates a list of processing tasks for a given image.

        Args:
            image_path (Path): Path to the input image.
            sizes (List[str]): List of target sizes (e.g., ['x720', '1080p']).
            qualities (List[int]): List of quality values (0-100).
            formats (List[str]): List of target formats (e.g., ['png']).
            pad (bool): Whether to pad the image to exact dimensions.
            pad_color (str): Color to use for padding.
            force (bool): Whether to force exact dimensions (ignoring aspect ratio).
            crop (bool): Whether to smart crop to fill dimensions.
            strip (bool): Whether to strip metadata.

        Returns:
            List[Tuple]: A list of task tuples to be executed.
        """
        if not sizes: sizes = ["x720"]
        if not qualities: qualities = [100]
        if not formats: formats = [None]

        tasks = []
        for size in sizes:
            for quality in qualities:
                for fmt in formats:
                    tasks.append((image_path, size, quality, fmt, pad, pad_color, force, crop, strip))
        
        return tasks

    def execute_task(self, task: Tuple) -> Optional[Path]:
        """
        Executes a single processing task.

        Args:
            task (Tuple): The task parameters.

        Returns:
            Optional[Path]: The path to the generated file, or None if failed.
        """
        image_path, resize, quality, fmt, pad_mode, pad_color, force, crop, strip = task
        path = Path(image_path)
        
        if not path.exists():
            log(f"File not found: {path}", "error")
            return None

        # Determine resize string
        resize_str = PRESETS.get(resize.lower(), resize)
        
        # Logic for resize/crop/pad
        if force and not resize_str.endswith("!") and not crop:
            resize_str += "!"

        # Build output filename
        suffix = f"_{resize_str}"
        if quality != 100: suffix += f"_Q{quality}"
        if pad_mode: suffix += "_pad"
        if crop: suffix += "_crop"
        if strip: suffix += "_clean"
        
        ext = f".{fmt}" if fmt else path.suffix
        outfile = safe_filename(path.stem, suffix, ext, self.output_folder)

        # Build Command
        magick_cmd = get_magick_command()
        cmd = [magick_cmd, str(path)]

        # Metadata Stripping
        if strip:
            cmd.append("-strip")

        # ICO Special Handling
        if ext.lower() == ".ico":
            # Auto-resize for multi-layer icons
            cmd.extend(["-define", "icon:auto-resize=256,128,64,48,32,16"])
        else:
            # Normal Resize Logic
            if crop:
                # Smart crop strategy: resize to fill (^) then crop center
                cmd.extend(["-resize", f"{resize_str}^", "-gravity", "center", "-extent", resize_str])
            elif pad_mode:
                cmd.extend(["-resize", resize_str, "-background", pad_color, "-gravity", "center", "-extent", resize_str])
            else:
                cmd.extend(["-resize", resize_str])

        cmd.extend(["-quality", str(quality), str(outfile)])

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            log(f"Processed: {path.name} -> {outfile.name}", "success")
            self._log_to_file(path, outfile, resize_str, quality)
            return outfile
        except subprocess.CalledProcessError as e:
            log(f"Error processing {path.name}: {e}", "error")
            return None

    def _log_to_file(self, input_path: Path, output_path: Path, resize: str, quality: int) -> None:
        """Writes the operation details to the log file."""
        if not self.log_enabled: return
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} | {input_path.name} -> {output_path.name} | {resize} Q{quality}\n")
        except Exception as e:
            print(f"Logging failed: {e}")

# -------------------------------
# Watch Mode
# -------------------------------
class WatchHandler(FileSystemEventHandler):
    """
    Watchdog handler to process new files in the directory.
    """
    def __init__(self, processor: MagickProcessor, options: Dict[str, Any]):
        self.processor = processor
        self.options = options
        self.last_processed = {}

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory: return
        
        path = Path(event.src_path)
        if path.suffix.lower() not in SUPPORTED_EXTS: return
        
        # Debounce: Avoid processing the same file multiple times in quick succession
        if path in self.last_processed and (time.time() - self.last_processed[path] < 2):
            return
        
        # Wait for file write to finish (simple heuristic)
        time.sleep(0.5)
        
        log(f"New file detected: {path.name}", "info")
        tasks = self.processor.process(path, **self.options)
        for task in tasks:
            self.processor.execute_task(task)
        
        self.last_processed[path] = time.time()

# -------------------------------
# Argument Parsing
# -------------------------------
def parse_arguments() -> Optional[Dict[str, Any]]:
    """
    Parses command line arguments into a configuration dictionary.
    Supports flexible argument ordering.
    """
    args = sys.argv[1:]
    if not args:
        return None

    config = {
        "sizes": [],
        "images": [],
        "qualities": [100],
        "formats": [],
        "output_folder": "output",
        "pad": False,
        "pad_color": "black",
        "force": False,
        "crop": False,
        "strip": False,
        "log_enabled": False,
        "watch": False,
        "clipboard": False
    }

    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
            
        larg = arg.lower()

        # Flags
        if larg in ["--version", "-v"]:
            print(__version__)
            sys.exit(0)

        if larg in ["--watch", "-w"]:
            config["watch"] = True
            continue
        if larg in ["--clipboard", "-c", "-clip"]:
            config["clipboard"] = True
            continue
        if larg in ["--crop", "-crop"]:
            config["crop"] = True
            continue
        if larg in ["--strip", "-strip", "-s"]:
            config["strip"] = True
            continue
        if larg in ["--no-logs", "-no-logs"]:
            config["log_enabled"] = False
            continue
        
        # Output folder
        if larg in ["-o", "-output", "-folder"]:
            if i + 1 < len(args):
                config["output_folder"] = args[i+1]
                skip_next = True
            continue

        # Presets / Sizes
        # Matches: "720p", "720", "1920x1080"
        if larg in PRESETS or (larg.isdigit()) or ("x" in larg and larg.replace("x","").isdigit()):
            if larg.isdigit(): config["sizes"].append(f"x{larg}")
            else: config["sizes"].append(larg)
            continue

        # Qualities
        # Matches: "q80", "80%"
        if larg.startswith("q") and larg[1:].isdigit():
            config["qualities"] = [int(q[1:]) for q in arg.split(",")]
            continue
        if larg.endswith("%") and larg[:-1].isdigit():
             config["qualities"] = [int(larg[:-1])]
             continue
        
        # Formats
        if larg in ["format", "formats"]: continue
        if larg in ["jpg", "jpeg", "png", "webp", "bmp", "ico", "tiff"]:
            config["formats"].append(larg)
            continue

        # Pad
        if "pad" in larg or "fill" in larg:
            config["pad"] = True
            continue
        if larg in ["black", "white", "transparent"] and not config["images"]: 
            # Heuristic: colors are usually pad colors if not images
            config["pad_color"] = larg
            continue

        # Stretch
        if larg in ["!", "stretch"]:
            config["force"] = True
            continue

        # Images
        config["images"].append(arg)

    if not config["sizes"]: config["sizes"] = ["x720"]
    if not config["formats"]: config["formats"] = [None]
    
    return config

# -------------------------------
# Main
# -------------------------------
def main():
    config = parse_arguments()
    if not config:
        print(f"{Fore.YELLOW}Usage: magic <image/wildcard> <size> [options]")
        print(f"Options: --watch, --clipboard, --crop, --strip, q80, format ico")
        return

    processor = MagickProcessor(config["output_folder"], config["log_enabled"])
    
    # Options dict for processor
    proc_options = {
        "sizes": config["sizes"],
        "qualities": config["qualities"],
        "formats": config["formats"],
        "pad": config["pad"],
        "pad_color": config["pad_color"],
        "force": config["force"],
        "crop": config["crop"],
        "strip": config["strip"]
    }

    # Mode 1: Watch
    if config["watch"]:
        log("Starting Watch Mode...", "info")
        log(f"Watching current directory for {SUPPORTED_EXTS}", "info")
        log("Press Ctrl+C to stop.", "warn")
        
        observer = Observer()
        handler = WatchHandler(processor, proc_options)
        observer.schedule(handler, ".", recursive=False)
        observer.start()
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        return

    # Mode 2: Clipboard
    if config["clipboard"]:
        log("Checking clipboard...", "info")
        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image):
            # Save temp file
            temp_path = Path("clipboard_temp.png")
            img.save(temp_path)
            log("Image found in clipboard!", "success")
            
            tasks = processor.process(temp_path, **proc_options)
            for task in tasks:
                outfile = processor.execute_task(task)
                if outfile:
                    # Optional: Copy back to clipboard could be added here
                    pass
            
            # Cleanup
            if temp_path.exists(): temp_path.unlink()
        else:
            log("No image found in clipboard.", "warn")
        return

    # Mode 3: Standard Batch
    images = []
    for img_arg in config["images"]:
        if "*" in img_arg:
            images.extend(list(Path(".").glob(img_arg)))
        else:
            p = Path(img_arg)
            if p.exists(): images.append(p)
            else: log(f"File not found: {img_arg}", "warn")

    if not images:
        log("No images found to process.", "warn")
        return

    log(f"Processing {len(images)} images...", "info")
    
    all_tasks = []
    for img in images:
        all_tasks.extend(processor.process(img, **proc_options))

    # Use ThreadPool for parallel processing
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(processor.execute_task, all_tasks)

    log("All done!", "success")

if __name__ == "__main__":
    main()
