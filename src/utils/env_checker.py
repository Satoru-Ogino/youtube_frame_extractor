import sys
import os
import platform
import subprocess
from importlib.metadata import version, PackageNotFoundError
from src.utils.logger import logger

def get_default_ffmpeg_path():
    """
    Returns the path to the portable FFmpeg executable provided by imageio-ffmpeg if available,
    otherwise returns 'ffmpeg'.
    """
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and os.path.exists(path):
            return path
    except ImportError:
        pass
    return "ffmpeg"

def get_package_version(package_name):
    """
    Returns the version of a python package if installed, else 'Not Installed'.
    """
    try:
        # Standard approach for python 3.8+
        return version(package_name)
    except PackageNotFoundError:
        # Fallback to importing and checking __version__
        try:
            mod = __import__(package_name)
            return getattr(mod, "__version__", "Unknown Version")
        except ImportError:
            return "Not Installed"

def get_ffmpeg_version(ffmpeg_path="ffmpeg"):
    """
    Attempts to get the ffmpeg version by running the executable.
    Returns the version string or 'Not Found'.
    """
    try:
        # Run ffmpeg -version
        # Using startupinfo on Windows to prevent console window popup
        startupinfo = None
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=startupinfo,
            check=False
        )
        if result.returncode == 0:
            first_line = result.stdout.split("\n")[0]
            # Standard output starts with "ffmpeg version x.x.x"
            return first_line.strip()
        else:
            return f"Error (code {result.returncode})"
    except FileNotFoundError:
        return "Not Found"
    except Exception as e:
        return f"Unavailable ({e})"

def check_environment(ffmpeg_path="ffmpeg"):
    """
    Compiles a dictionary of environment info for logging and markdown metadata.
    """
    if ffmpeg_path == "ffmpeg":
        test_ver = get_ffmpeg_version("ffmpeg")
        if "Not Found" in test_ver or "Unavailable" in test_ver:
            ffmpeg_path = get_default_ffmpeg_path()
            logger.info(f"System FFmpeg not found, falling back to portable path: {ffmpeg_path}")

    env_info = {
        "os": f"{platform.system()} {platform.release()} ({platform.architecture()[0]})",
        "python": sys.version.split("\n")[0].strip(),
        "yt_dlp": get_package_version("yt-dlp"),
        "pillow": get_package_version("Pillow"),
        "customtkinter": get_package_version("customtkinter"),
        "ffmpeg": get_ffmpeg_version(ffmpeg_path)
    }
    
    logger.info("=== Environment Check ===")
    for k, v in env_info.items():
        logger.info(f"{k.upper()}: {v}")
    logger.info("==========================")
    
    return env_info
