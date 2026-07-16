import os
import sys
from datetime import datetime
from PIL import Image

# Setup path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.logger import logger, setup_file_logging
from src.utils import env_checker
from src.processor import metadata_writer, markdown_generator
from src.extractor import yt_client, ffmpeg_wrapper

def test_metadata_injection(output_dir):
    """
    Tests PNG metadata writing and reading with a dummy image.
    """
    logger.info("--- Testing PNG Metadata Injection ---")
    dummy_temp = os.path.join(output_dir, "temp_dummy.png")
    dummy_final = os.path.join(output_dir, "test_dummy.png")
    
    # 1. Create a simple white image
    img = Image.new("RGB", (100, 100), color="white")
    img.save(dummy_temp, "PNG")
    
    # 2. Inject custom metadata
    test_meta = {
        "Copyright": "Metadata Test Run",
        "Source": "https://www.youtube.com/watch?v=test_id",
        "ExtractionFrame": "12345",
        "ExtractionTimestamp": datetime.now().isoformat(),
        "ExtractionSoftware": "Test Framework v0.1"
    }
    
    metadata_writer.save_png_with_metadata(dummy_temp, dummy_final, test_meta)
    
    # 3. Read metadata back and verify
    read_meta = metadata_writer.read_png_metadata(dummy_final)
    logger.info(f"Read injected metadata: {read_meta}")
    
    # Clean up dummy files
    for p in [dummy_temp, dummy_final]:
        if os.path.exists(p):
            os.remove(p)
            
    # Verification assertions
    assert read_meta.get("Copyright") == test_meta["Copyright"], "Copyright mismatch!"
    assert read_meta.get("ExtractionFrame") == test_meta["ExtractionFrame"], "Frame mismatch!"
    logger.info("PNG metadata read/write test: PASSED")

def test_youtube_extraction(output_dir):
    """
    Tests fetching metadata and extracting a frame from a short public YouTube video.
    We will use a stable Blender Open Movie clip on YouTube for testing.
    """
    logger.info("--- Testing YouTube Video Extraction ---")
    test_url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"  # Big Buck Bunny 60fps clip
    target_frame = 120
    
    # 1. Fetch info
    video_info = yt_client.fetch_video_info(test_url)
    
    # 2. Setup output paths
    temp_png = os.path.join(output_dir, "temp_test_extraction.png")
    final_png = os.path.join(output_dir, "test_extraction.png")
    final_md = os.path.join(output_dir, "test_extraction.md")
    
    # 3. Extract Frame
    ffmpeg_wrapper.extract_frame_to_png(
        stream_url=video_info["stream_url"],
        frame_number=target_frame,
        fps=video_info["fps"],
        output_path=temp_png
    )
    
    # 4. Inject metadata
    metadata = {
        "Copyright": "YouTube Video Creator",
        "Source": test_url,
        "ExtractionFrame": str(target_frame),
        "ExtractionTimestamp": datetime.now().isoformat(),
        "ExtractionSoftware": "YouTube Frame Extractor Test Suite"
    }
    metadata_writer.save_png_with_metadata(temp_png, final_png, metadata)
    
    # Clean up temp
    if os.path.exists(temp_png):
        os.remove(temp_png)
        
    # 5. Generate Markdown
    video_info["frame_number"] = target_frame
    video_info["timestamp_seconds"] = target_frame / video_info["fps"]
    video_info["extraction_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    video_info["image_file_path"] = final_png
    
    env_info = env_checker.check_environment()
    markdown_generator.generate_metadata_markdown(final_md, video_info, env_info)
    
    # Verify outputs exist
    assert os.path.exists(final_png), "Output PNG does not exist!"
    assert os.path.exists(final_md), "Output Markdown does not exist!"
    logger.info(f"Extraction test outputs created successfully in: {output_dir}")
    
    # Read and print metadata of extracted image
    extracted_meta = metadata_writer.read_png_metadata(final_png)
    logger.info(f"Extracted image embedded metadata: {extracted_meta}")
    
    # Clean up outputs
    for p in [final_png, final_md]:
        if os.path.exists(p):
            os.remove(p)
            logger.info(f"Cleaned up test file: {p}")
            
    logger.info("YouTube video frame extraction test: PASSED")

def main():
    setup_file_logging(project_root)
    test_dir = os.path.join(project_root, "test_output")
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Run test 1: Local PIL tEXt writing
        test_metadata_injection(test_dir)
        
        # Run test 2: Full youtube metadata + ffmpeg extraction
        # Note: This will perform network request and call FFmpeg.
        test_youtube_extraction(test_dir)
        
        logger.info("ALL TESTS PASSED SUCCESSFULLY!")
        print("\n[SUCCESS] Extractor backend tests passed. Dependencies and FFmpeg are configured correctly.")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print(f"\n[FAILURE] Test suite error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clean up test output dir
        try:
            if os.path.exists(test_dir) and not os.listdir(test_dir):
                os.rmdir(test_dir)
        except:
            pass

if __name__ == "__main__":
    main()
