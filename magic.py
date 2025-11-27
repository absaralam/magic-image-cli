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
import json
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
__version__ = "2.6"
CONFIG_FILE: str = ".magicrc"

LOG_FILE: str = "magick_log.txt"
SUPPORTED_EXTS: set = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif", ".ico"}

PRESETS: Dict[str, str] = {
    "720p": "x720",
    "1080p": "x1080",
    "1440p": "x1440",
    "2k": "x2160",
    "4k": "x3840",
    "8k": "x7680"
}

QUALITY_PRESETS: Dict[str, int] = {
    "max": 100, "best": 100, 
    "high": 90, 
    "medium": 75, "med": 75, 
    "low": 50
}

# Keywords that should be ignored if they don't match a file
SAFE_WORDS: List[str] = [
    "resize", "convert", "to", "save", "as", "format", "formats", "quality", 
    "high", "medium", "med", "low", "max", "best", "crop", 
    "clean", "remove", "metadata", "paste", "monitor", "stretch", "force", "watch", "clipboard"
]

# Gravity Mappings
COMPOUND_GRAVITY: Dict[str, str] = {
    "north-east": "NorthEast", "northeast": "NorthEast", "north_east": "NorthEast", "ne": "NorthEast",
    "north-west": "NorthWest", "northwest": "NorthWest", "north_west": "NorthWest", "nw": "NorthWest",
    "south-east": "SouthEast", "southeast": "SouthEast", "south_east": "SouthEast", "se": "SouthEast",
    "south-west": "SouthWest", "southwest": "SouthWest", "south_west": "SouthWest", "sw": "SouthWest"
}

GRAVITY_TERMS: List[str] = [
    "top", "upper", "north", "bottom", "lower", "south", 
    "left", "west", "right", "east", "center", "middle"
]

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

def load_config() -> Dict[str, Any]:
    """
    Loads configuration from .magicrc files.
    Priority:
    1. Internal Defaults (Empty dict here, handled in parse_arguments)
    2. Global Config (Same dir as magic.py)
    3. Local Config (Current working directory)
    
    Returns a merged dictionary of settings.
    """
    config = {}
    
    # 1. Global Config (App Directory)
    # When frozen with PyInstaller, sys.executable is the path.
    # When running as script, __file__ is the path.
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent
        
    global_config_path = app_dir / CONFIG_FILE
    
    # Auto-create global config if it doesn't exist
    if not global_config_path.exists():
        try:
            # We only try to create it if we have write permissions
            # We'll just try and catch the exception if it fails
            if create_default_config(global_config_path, silent=True):
                print(f"{Fore.CYAN}Welcome to Magic! Created a global config file for you at: {global_config_path}")
                print(f"{Fore.CYAN}You can edit this file to set your permanent defaults.")
        except Exception:
            pass # Fail silently if we can't write to the app dir (e.g. Program Files)

    if global_config_path.exists():
        try:
            with open(global_config_path, "r", encoding="utf-8") as f:
                config.update(json.load(f))
                # print(f"{Fore.CYAN}Loaded global config from {global_config_path}")
        except Exception as e:
            print(f"{Fore.RED}Error loading global config: {e}")

    # 2. Local Config (Current Directory)
    local_config_path = Path.cwd() / CONFIG_FILE
    # Avoid loading twice if we are running from the app dir
    if local_config_path.exists() and local_config_path.resolve() != global_config_path.resolve():
        try:
            with open(local_config_path, "r", encoding="utf-8") as f:
                config.update(json.load(f))
                # print(f"{Fore.CYAN}Loaded local config from {local_config_path}")
        except Exception as e:
            print(f"{Fore.RED}Error loading local config: {e}")
            
    return config

def create_default_config(target_path: Path = None, silent: bool = False) -> bool:
    """
    Creates a default .magicrc file at the specified path.
    If no path is provided, creates it in the current directory.
    Returns True if successful, False otherwise.
    """
    if target_path is None:
        target_path = Path(CONFIG_FILE)
        
    defaults = {
        "output_folder": "output",
        "pad_color": "black",
        "log_enabled": False,
        "watermark": None,
        "gravity": "SouthEast",
        "default_quality": 100,
        "default_size": "x720"
    }
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(defaults, f, indent=4)
        if not silent:
            print(f"{Fore.GREEN}Created default configuration file: {target_path}")
        return True
    except Exception as e:
        # Only print error if we were explicitly asked to create it (CLI flag)
        if not silent:
            print(f"{Fore.RED}Error creating config file at {target_path}: {e}")
        return False

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
        self.output_folder = output_folder # Store as string initially to handle "__INPUT__" sentinel
        self.log_enabled = log_enabled
        if self.output_folder != "__INPUT__":
             Path(self.output_folder).mkdir(exist_ok=True)

    def process(self, image_path: Path, sizes: List[str] = None, qualities: List[int] = None, 
                formats: List[Optional[str]] = None, pad: bool = False, pad_color: str = "white", 
                force: bool = False, crop: bool = False, strip: bool = False, 
                watermark: str = None, gravity: str = "SouthEast") -> List[Tuple]:
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
            watermark (str): Path to watermark image.
            gravity (str): Gravity for watermark positioning.

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
                    tasks.append((image_path, size, quality, fmt, pad, pad_color, force, crop, strip, watermark, gravity))
        
        return tasks

    def execute_task(self, task: Tuple) -> Optional[Path]:
        """
        Executes a single processing task.

        Args:
            task (Tuple): The task parameters.

        Returns:
            Optional[Path]: The path to the generated file, or None if failed.
        """
        image_path, resize, quality, fmt, pad_mode, pad_color, force, crop, strip, watermark, gravity = task
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
        if watermark: suffix += "_wm"
        
        ext = f".{fmt}" if fmt else path.suffix
        
        # Determine output folder
        if self.output_folder == "__INPUT__":
            target_folder = path.parent
        else:
            target_folder = Path(self.output_folder)
            
        outfile = safe_filename(path.stem, suffix, ext, target_folder)

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
        
        # Watermark Composite
        if watermark:
            wm_path = Path(watermark)
            if wm_path.exists():
                # Syntax: magick input -resize ... watermark -gravity ... -composite output
                # We need to insert watermark args before the output file but after resize
                cmd.extend([str(wm_path), "-gravity", gravity, "-composite"])
            else:
                log(f"Watermark file not found: {watermark}", "warn")

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
# PDF Helper
# -------------------------------
def merge_images_to_pdf(images: List[Path], output_folder: str) -> None:
    """
    Merges multiple images into a single PDF file.
    """
    if not images: return
    
    # Determine output filename
    # If output_folder is a specific name (not 'output' or '__INPUT__'), use it as filename
    # Otherwise use 'merged_images.pdf'
    
    target_folder = Path(output_folder)
    if output_folder == "__INPUT__":
        target_folder = images[0].parent
    elif output_folder == "output":
         target_folder = Path("output")
         target_folder.mkdir(exist_ok=True)
    
    # Check if output_folder looks like a filename (ends in .pdf)
    if str(target_folder).lower().endswith(".pdf"):
        outfile = target_folder
        # Ensure parent dir exists
        if outfile.parent != Path("."):
            outfile.parent.mkdir(parents=True, exist_ok=True)
    else:
        # It's a folder, generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outfile = target_folder / f"merged_{timestamp}.pdf"
        if not target_folder.exists():
            target_folder.mkdir(parents=True, exist_ok=True)

    log(f"Merging {len(images)} images into {outfile}...", "info")
    
    # Command: magick convert img1 img2 ... output.pdf
    cmd = [get_magick_command()]
    cmd.extend([str(img) for img in images])
    cmd.append(str(outfile))
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        log(f"Successfully created PDF: {outfile}", "success")
    except subprocess.CalledProcessError as e:
        log(f"Error creating PDF: {e}", "error")

# -------------------------------
# Argument Parsing Helpers
# -------------------------------
def _merge_spaced_args(args: List[str]) -> List[str]:
    """
    Merges spaced dimensions (e.g., '1920 x 1080' -> '1920x1080').
    """
    merged = []
    i = 0
    while i < len(args):
        current = args[i]
        # Check for pattern: Digit, x/X, Digit
        if i + 2 < len(args):
            next_arg = args[i+1]
            next_next_arg = args[i+2]
            if current.isdigit() and next_arg.lower() == "x" and next_next_arg.isdigit():
                merged.append(f"{current}x{next_next_arg}")
                i += 3
                continue
        merged.append(current)
        i += 1
    return merged

def _resolve_watermark(config: Dict[str, Any], watermark_keyword: bool) -> None:
    """
    Attempts to find a watermark file if the keyword was used but no file specified.
    """
    if watermark_keyword and not config["watermark"]:
        candidates = ["watermark.png", "logo.png"]
        for ext in SUPPORTED_EXTS:
            if ext == ".png": continue
            candidates.append(f"watermark{ext}")
            candidates.append(f"logo{ext}")
            
        for candidate in candidates:
            if Path(candidate).exists():
                config["watermark"] = candidate
                break
        
        if not config["watermark"]:
            print(f"{Fore.YELLOW}Warning: 'watermark' keyword used but no 'watermark' or 'logo' image found.")

def _resolve_gravity(config: Dict[str, Any], v_align: str, h_align: str, override: bool) -> None:
    """
    Resolves final gravity based on vertical/horizontal alignment or overrides.
    """
    if not override and (v_align or h_align):
        if v_align == "Center" and not h_align:
            config["gravity"] = "Center"
        else:
            g = ""
            if v_align: g += v_align
            if h_align: g += h_align
            if g: config["gravity"] = g

# -------------------------------
# Argument Parsing
# -------------------------------
def parse_arguments() -> Optional[Dict[str, Any]]:
    """
    Parses command line arguments into a configuration dictionary.
    Supports flexible argument ordering and natural language syntax.
    """
    args = sys.argv[1:]
    if not args:
        return None

    # Load defaults from config file
    file_config = load_config()

    config = {
        "sizes": [],
        "images": [],
        "qualities": [],
        "formats": [],
        "output_folder": file_config.get("output_folder", "output"),
        "pad": False,
        "pad_color": file_config.get("pad_color", "black"),
        "force": False,
        "crop": False,
        "strip": False,
        "log_enabled": file_config.get("log_enabled", False),
        "watch": False,
        "clipboard": False,
        "watermark": file_config.get("watermark", None),
        "watermark": file_config.get("watermark", None),
        "gravity": file_config.get("gravity", "SouthEast"),
        "pdf_merge": False
    }
    
    # Default values from config or hardcoded
    default_quality = file_config.get("default_quality", 100)
    default_size = file_config.get("default_size", "x720")

    # Pre-process args
    args = _merge_spaced_args(args)

    # Gravity State
    v_align = ""
    h_align = ""
    gravity_override = False
    
    # Check context
    watermark_context = any(a.lower() in ["--watermark", "-wm", "watermark", "wm"] for a in args)
    watermark_keyword = False

    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
            
        larg = arg.lower()

        # --- Explicit Flags ---

        # Input File
        if larg in ["--file", "-file", "-f", "--input", "-input", "-i"]:
            if i + 1 < len(args):
                config["images"].append(args[i+1])
                skip_next = True
            continue

        # Resize
        if larg in ["--resize", "-resize", "-r", "-res", "--res", "--size", "-size", "-s"]:
            if i + 1 < len(args):
                val = args[i+1]
                if val.isdigit(): config["sizes"].append(f"x{val}")
                else: config["sizes"].append(val)
                skip_next = True
            continue

        # Format
        if larg in ["--format", "-format", "-fmt", "--fmt"]:
            if i + 1 < len(args):
                config["formats"].append(args[i+1])
                skip_next = True
            continue

        # Quality
        if larg in ["--quality", "-quality", "-q", "--q"]:
            if i + 1 < len(args):
                val = args[i+1]
                if val.endswith("%"): val = val[:-1]
                if val.isdigit(): config["qualities"].append(int(val))
                skip_next = True
            continue

        # Output folder
        if larg in ["to", "into", "output", "-o", "--o", "-output", "--output", "--out", "-out"]:
            if i + 1 < len(args):
                next_arg = args[i+1]
                
                # Heuristics to avoid consuming keywords as folders
                is_size = next_arg in PRESETS or next_arg.isdigit() or ("x" in next_arg.lower() and next_arg.lower().replace("x","").isdigit())
                is_format = next_arg.lower() in ["jpg", "jpeg", "png", "webp", "bmp", "ico", "tiff"]
                is_explicit_flag = larg.startswith("-")
                
                if is_explicit_flag or (not is_size and not is_format):
                    if next_arg.lower() in ["i", "input", "."]:
                        config["output_folder"] = "__INPUT__"
                    else:
                        config["output_folder"] = next_arg
                    skip_next = True
                    continue

        # Watermark
        if larg in ["--watermark", "-watermark", "-wm"]:
            if i + 1 < len(args):
                config["watermark"] = args[i+1]
                skip_next = True
            continue
        if larg in ["watermark", "wm"]:
            watermark_keyword = True
            continue

        # Metadata
        if larg == "remove" and i + 1 < len(args) and args[i+1].lower() == "metadata":
            config["strip"] = True
            skip_next = True
            continue
            
        # Gravity
        if larg in ["--gravity", "-g"]:
            if i + 1 < len(args):
                config["gravity"] = args[i+1]
                skip_next = True
                gravity_override = True
            continue
        
        # Gravity Keywords
        if larg in GRAVITY_TERMS or larg in COMPOUND_GRAVITY:
            if watermark_context:
                if larg in COMPOUND_GRAVITY:
                    config["gravity"] = COMPOUND_GRAVITY[larg]
                    gravity_override = True
                elif larg in ["top", "upper", "north"]: v_align = "North"
                elif larg in ["bottom", "lower", "south"]: v_align = "South"
                elif larg in ["left", "west"]: h_align = "West"
                elif larg in ["right", "east"]: h_align = "East"
                elif larg in ["center", "middle"]: 
                    v_align = "Center"
                    h_align = ""
                continue 
            elif not Path(arg).exists():
                print(f"{Fore.YELLOW}Warning: Ignored ambiguous argument '{arg}'. Did you mean 'watermark {arg}'?")
                continue

        # Quality Presets & Values
        if larg == "quality":
            # Check next arg
            if i + 1 < len(args):
                next_arg = args[i+1]
                if next_arg.isdigit():
                    config["qualities"].append(int(next_arg))
                    skip_next = True
                    continue
                if next_arg.endswith("%") and next_arg[:-1].isdigit():
                    config["qualities"].append(int(next_arg[:-1]))
                    skip_next = True
                    continue
            # Check previous arg for preset (e.g. "high quality")
            if i > 0 and args[i-1].lower() in QUALITY_PRESETS:
                config["qualities"].append(QUALITY_PRESETS[args[i-1].lower()])
                continue

        # Flags (Boolean)
        if larg in ["--version", "-v"]:
            print(__version__)
            sys.exit(0)
        if larg == "--init-config":
            create_default_config()
            sys.exit(0)
        if larg in ["--watch", "-watch", "-w", "--monitor", "-monitor", "watch", "monitor"]:
            config["watch"] = True
            continue
        if larg in ["--clipboard", "-clipboard", "-c", "-clip", "--paste", "-paste", "clipboard", "paste"]:
            config["clipboard"] = True
            continue
        if larg in ["--crop", "-crop", "crop"]:
            config["crop"] = True
            continue
        if larg in ["--strip", "-strip", "-s", "--clean", "-clean", "--remove-metadata", "-remove-metadata", "clean"]:
            config["strip"] = True
            continue
        if larg in ["--no-logs", "-no-logs"]:
            config["log_enabled"] = False
            continue
        if larg in ["!", "--force", "-force", "--stretch", "-stretch", "--!", "-!", "stretch", "force"]:
            config["force"] = True
            continue

        # Formats
        if larg in ["format", "formats"]: continue
        if larg in ["jpg", "jpeg", "png", "webp", "bmp", "ico", "tiff"]:
            config["formats"].append(larg)
            continue
        
        # PDF Keyword (Merge Trigger vs Format)
        if larg in ["pdf", "--pdf", "-pdf"]:
            # Check if previous argument was "format"
            if i > 0 and args[i-1].lower() in ["format", "formats", "--format", "-fmt"]:
                config["formats"].append("pdf")
            else:
                config["pdf_merge"] = True
            continue

        # Pad
        if larg in ["pad", "fill", "--pad", "-pad"]:
            config["pad"] = True
            continue
        if larg in ["black", "white", "transparent"] and not config["images"]: 
            config["pad_color"] = larg
            continue

        # Safe Keywords (Filler)
        if larg in SAFE_WORDS:
            if Path(arg).exists(): pass 
            else: continue

        # Presets / Sizes
        if larg in PRESETS or (larg.isdigit()) or ("x" in larg and larg.replace("x","").isdigit()):
            if Path(arg).exists(): pass
            else:
                if larg.isdigit(): 
                    val = int(larg)
                    if 40 <= val <= 100:
                        print(f"{Fore.YELLOW}Warning: Ambiguous argument '{larg}'. Did you mean quality 'q{larg}'? Treating as size 'x{larg}'.")
                    config["sizes"].append(f"x{larg}")
                else: config["sizes"].append(larg)
                continue

        # Qualities (Short syntax)
        if larg.startswith("q") and larg[1:].isdigit():
            config["qualities"].extend([int(q[1:]) for q in arg.split(",")])
            continue
        if larg.endswith("%") and larg[:-1].isdigit():
             config["qualities"].append(int(larg[:-1]))
             continue

        # Images or Directories
        p = Path(arg)
        if p.is_dir():
            for ext in SUPPORTED_EXTS:
                config["images"].extend([str(f) for f in p.glob(f"*{ext}")])
        else:
            config["images"].append(arg)

    # Resolve Helpers
    _resolve_gravity(config, v_align, h_align, gravity_override)
    _resolve_watermark(config, watermark_keyword)

    if not config["sizes"]: config["sizes"] = [default_size]
    if not config["qualities"]: config["qualities"] = [default_quality]
    if not config["formats"]: config["formats"] = [None]
    
    return config

# -------------------------------
# Main
# -------------------------------
def main():
    config = parse_arguments()
    if not config:
        print(f"{Fore.YELLOW}Usage: magic <image/wildcard> <size> [options]")
        print(f"Options: --watch, --clipboard, --crop, --strip, --watermark logo.png, q80, format ico")
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
        "strip": config["strip"],
        "watermark": config["watermark"],
        "gravity": config["gravity"]
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
        # Implicit selection for PDF Merge
        if config.get("pdf_merge"):
            log("No files specified. Selecting all images in current directory...", "info")
            for ext in SUPPORTED_EXTS:
                images.extend(list(Path(".").glob(f"*{ext}")))
        
        if not images:
            log("No images found to process.", "warn")
            return

    # PDF Merge Mode
    if config.get("pdf_merge"):
        merge_images_to_pdf(images, config["output_folder"])
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
