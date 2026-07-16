import os
from src.utils.logger import logger

def generate_metadata_markdown(output_md_path, info_dict, env_info):
    """
    Generates a Markdown file containing all extraction metadata,
    video info, and environmental version data.
    """
    logger.info(f"Generating companion Markdown metadata file: {output_md_path}")
    
    file_basename = os.path.basename(info_dict.get("image_file_path", ""))
    
    md_content = f"""# YouTube Frame Extraction Metadata

This file contains provenance metadata for a frame extracted using the YouTube Frame Extractor.

## 1. Extraction Target Details

| Property | Value |
| :--- | :--- |
| **YouTube Video Link** | [{info_dict.get('url')}]({info_dict.get('url')}) |
| **Saved Image Filename** | `{file_basename}` |
| **Target Frame Number** | `{info_dict.get('frame_number')}` |
| **Timestamp (Calculated)** | `{info_dict.get('timestamp_seconds'):.4f} seconds` |
| **Data Extraction Date/Time** | `{info_dict.get('extraction_time')}` |

## 2. Video Stream Source Properties

| Property | Value |
| :--- | :--- |
| **Video Title** | {info_dict.get('title')} |
| **Video Upload / Published Date** | `{info_dict.get('published_date')}` |
| **Video Stream Resolution** | `{info_dict.get('width')} x {info_dict.get('height')}` |
| **Video Stream Codec** | `{info_dict.get('vcodec')}` |
| **Video Stream Framerate (FPS)** | `{info_dict.get('fps')} FPS` |
| **Selected Stream Format ID** | `{info_dict.get('format_id')}` |

## 3. Environment & Software Versions

| Component | Version |
| :--- | :--- |
| **Operating System (OS)** | `{env_info.get('os')}` |
| **Python Version** | `{env_info.get('python')}` |
| **yt-dlp Library** | `{env_info.get('yt_dlp')}` |
| **Pillow Library** | `{env_info.get('pillow')}` |
| **CustomTkinter UI Framework** | `{env_info.get('customtkinter')}` |
| **FFmpeg Binary** | `{env_info.get('ffmpeg')}` |
"""
    try:
        # Write markdown using UTF-8 to handle Japanese titles or non-ASCII chars
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        logger.info(f"Markdown metadata file created: {output_md_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write Markdown file: {e}")
        raise e
