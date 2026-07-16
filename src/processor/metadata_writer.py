from PIL import Image, PngImagePlugin
import os
from src.utils.logger import logger

def save_png_with_metadata(temp_img_path, final_img_path, metadata_dict):
    """
    Loads a PNG image from temp_img_path, injects provenance metadata
    into the PNG tEXt chunks, and saves it to final_img_path.
    Does not modify the pixel values of the original image.
    """
    logger.info(f"Injecting metadata into PNG: {final_img_path}")
    try:
        if not os.path.exists(temp_img_path):
            raise FileNotFoundError(f"Temporary image file not found at: {temp_img_path}")

        # Open the raw image
        with Image.open(temp_img_path) as img:
            # Create a PngInfo object to hold the metadata chunk
            png_info = PngImagePlugin.PngInfo()
            
            # Populate text chunks
            for key, val in metadata_dict.items():
                # PNG tEXt chunks only support string keys and values
                str_key = str(key)
                str_val = str(val)
                png_info.add_text(str_key, str_val)
                logger.debug(f"  Added metadata chunk: {str_key} = {str_val}")

            # Save the image with pnginfo argument
            img.save(final_img_path, "PNG", pnginfo=png_info)
            
        logger.info(f"Saved final PNG with embedded metadata: {final_img_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to inject PNG metadata: {e}")
        raise e

def read_png_metadata(img_path):
    """
    Reads and returns the embedded tEXt metadata from a PNG file.
    Useful for verification.
    """
    if not os.path.exists(img_path):
        logger.warning(f"File not found for metadata reading: {img_path}")
        return {}
        
    try:
        with Image.open(img_path) as img:
            # Png metadata is stored in img.info dict
            # Filter out standard non-text elements if any, return dictionary of text values
            text_metadata = {}
            for k, v in img.info.items():
                if isinstance(v, (str, bytes)):
                    # Decoding bytes if needed
                    val_str = v.decode("utf-8", errors="replace") if isinstance(v, bytes) else str(v)
                    text_metadata[k] = val_str
            return text_metadata
    except Exception as e:
        logger.error(f"Failed to read PNG metadata from {img_path}: {e}")
        return {}
