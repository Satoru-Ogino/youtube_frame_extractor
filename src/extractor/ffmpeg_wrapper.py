import subprocess
import os
import platform
from src.utils.logger import logger

def extract_frame_to_png(stream_url, frame_number, fps, output_path, ffmpeg_path="ffmpeg"):
    """
    Extracts exactly 1 frame at the target frame_number using FFmpeg.
    Converts frame_number to seconds: target_seconds = frame_number / fps.
    Uses hybrid seek for speed and accuracy.
    """
    if ffmpeg_path == "ffmpeg":
        from src.utils.env_checker import get_default_ffmpeg_path
        ffmpeg_path = get_default_ffmpeg_path()

    target_seconds = frame_number / fps
    logger.info(f"Target frame: {frame_number} at {fps} FPS -> Target timestamp: {target_seconds:.4f} seconds")

    # Construct seek options
    # Hybrid seek: fast-seek to 2 seconds before target, then slow-seek the remaining 2 seconds.
    if target_seconds > 2.0:
        fast_seek = target_seconds - 2.0
        slow_seek = 2.0
        # Command: ffmpeg -ss [fast] -i [url] -ss [slow] -vframes 1 ...
        cmd = [
            ffmpeg_path,
            "-ss", f"{fast_seek:.4f}",
            "-i", stream_url,
            "-ss", f"{slow_seek:.4f}",
            "-vframes", "1",
            "-f", "image2",
            "-vcodec", "png",
            "-y",
            output_path
        ]
    else:
        # Simple seek for short clips
        cmd = [
            ffmpeg_path,
            "-i", stream_url,
            "-ss", f"{target_seconds:.4f}",
            "-vframes", "1",
            "-f", "image2",
            "-vcodec", "png",
            "-y",
            output_path
        ]

    logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
    
    # Run FFmpeg process
    startupinfo = None
    if platform.system() == "Windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=startupinfo,
            check=False
        )
        
        # FFmpeg prints progress/logs to stderr
        if process.stderr:
            # Output last few lines of FFmpeg output to debugger log
            stderr_lines = process.stderr.strip().split("\n")
            logger.debug("--- FFmpeg stderr output ---")
            for line in stderr_lines[-10:]:  # Last 10 lines
                logger.debug(line)
            logger.debug("----------------------------")
            
        if process.returncode != 0:
            raise Exception(f"FFmpeg exited with error code {process.returncode}. Stderr: {process.stderr[-200:]}")
            
        # Verify the file was created and is non-empty
        if not os.path.exists(output_path):
            raise Exception("FFmpeg command finished, but output file was not created.")
            
        if os.path.getsize(output_path) == 0:
            raise Exception("FFmpeg output file is 0 bytes.")
            
        logger.info(f"Successfully extracted frame to temporary file: {output_path}")
        return True
        
    except FileNotFoundError:
        logger.error("FFmpeg executable not found. Please ensure FFmpeg is installed and path is correct.")
        raise Exception("FFmpeg executable not found. Check settings or PATH environment variable.")
    except Exception as e:
        logger.error(f"FFmpeg frame extraction failed: {e}")
        raise e
