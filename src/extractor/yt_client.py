import yt_dlp
from src.utils.logger import logger

def get_codec_priority(vcodec):
    """
    Returns a priority integer for the video codec.
    AV1 (av01...) > VP9 (vp9/vp09...) > H.264 (avc1...) > others
    Higher is better.
    """
    if not vcodec or vcodec == "none":
        return -1
    vcodec = vcodec.lower()
    if "av01" in vcodec:
        return 3
    elif "vp9" in vcodec or "vp09" in vcodec:
        return 2
    elif "avc" in vcodec or "h264" in vcodec:
        return 1
    return 0

def select_best_format(formats):
    """
    Selects the best format based on resolution (height) and codec priority.
    """
    video_formats = []
    for fmt in formats:
        # We need formats that contain video stream
        if fmt.get("vcodec") != "none" and fmt.get("url"):
            # Ensure height exists
            height = fmt.get("height") or 0
            width = fmt.get("width") or 0
            codec = fmt.get("vcodec") or ""
            tbr = fmt.get("tbr") or 0  # Total bitrate as fallback
            fps = fmt.get("fps") or 0
            
            video_formats.append({
                "format_id": fmt.get("format_id"),
                "url": fmt.get("url"),
                "height": height,
                "width": width,
                "vcodec": codec,
                "acodec": fmt.get("acodec") or "none",
                "fps": fps,
                "tbr": tbr,
                "ext": fmt.get("ext")
            })

    if not video_formats:
        return None

    # Sort key: Resolution (height) desc, Codec priority desc, Bitrate desc
    def sort_key(x):
        return (x["height"], get_codec_priority(x["vcodec"]), x["tbr"])

    video_formats.sort(key=sort_key, reverse=True)
    
    # Log choices for debugging
    logger.debug("Available video formats (top 5 sorted):")
    for i, fmt in enumerate(video_formats[:5]):
        logger.debug(
            f"  {i+1}: ID={fmt['format_id']} Res={fmt['width']}x{fmt['height']} "
            f"Codec={fmt['vcodec']} FPS={fmt['fps']} Bitrate={fmt['tbr']}"
        )
        
    return video_formats[0]

def fetch_video_info(url):
    """
    Fetches video metadata and selects the best format using yt-dlp.
    Returns a dictionary of relevant info or raises an Exception.
    """
    logger.info(f"Fetching video info for URL: {url}")
    
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        if not info:
            raise Exception("Failed to extract video information (empty response)")
            
        title = info.get("title", "Unknown Title")
        logger.info(f"Video Found: {title}")
        
        formats = info.get("formats", [])
        best_format = select_best_format(formats)
        
        if not best_format:
            raise Exception("No suitable video formats found.")
            
        logger.info(
            f"Selected Format: {best_format['width']}x{best_format['height']} "
            f"({best_format['vcodec']}) at {best_format['fps']} FPS"
        )
        
        # Parse upload date (Format: YYYYMMDD -> YYYY-MM-DD)
        raw_date = info.get("upload_date", "")
        published_date = "Unknown"
        if len(raw_date) == 8:
            published_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
            
        return {
            "title": title,
            "url": url,
            "published_date": published_date,
            "fps": best_format["fps"] or info.get("fps") or 30.0,
            "duration": info.get("duration"),
            "width": best_format["width"],
            "height": best_format["height"],
            "vcodec": best_format["vcodec"],
            "stream_url": best_format["url"],
            "format_id": best_format["format_id"],
            "raw_info": info  # keep for troubleshooting
        }
        
    except Exception as e:
        logger.error(f"yt-dlp extraction error: {e}")
        raise e
