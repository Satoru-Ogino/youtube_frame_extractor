import os
import re
import sys
import threading
import queue
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

from src.gui.components import PathPicker, ConsoleView
from src.extractor import yt_client, ffmpeg_wrapper
from src.processor import metadata_writer, markdown_generator
from src.utils import env_checker
from src.utils.logger import logger, set_gui_callback, setup_file_logging

# Set default theme and appearance
ctk.set_appearance_mode("Dark")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class MainWindow(ctk.CTk):
    def __init__(self, base_dir):
        super().__init__()
        self.base_dir = base_dir
        
        # Configure Window
        self.title("YouTube Frame Extractor v1.0.0")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Initialize file logging
        setup_file_logging(self.base_dir)
        
        # Grid Layout: 1 column, multiple rows
        self.grid_rowconfigure(3, weight=1)  # Log output row gets the expansion
        self.grid_columnconfigure(0, weight=1)
        
        # Setup GUI callback for custom logger
        set_gui_callback(self._log_to_console)
        
        # Task Queue for thread-to-main communication
        self.task_queue = queue.Queue()
        
        # Construct UI Sections
        self._create_header()
        self._create_input_form()
        self._create_progress_area()
        self._create_log_console()
        
        # Detect environment
        self._async_env_check()
        
        # Start checking the task queue
        self.after(100, self._process_queue)
        
    def _create_header(self):
        """Creates the premium looking top header."""
        header_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="#1F2937")
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="YouTube Frame Extractor", 
            font=("Segoe UI", 20, "bold"),
            text_color="#60A5FA"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(12, 2), sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="Extract highest-quality frames and embed provenance metadata for academic research", 
            font=("Segoe UI", 11, "italic"),
            text_color="#9CA3AF"
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

    def _create_input_form(self):
        """Creates the input form containing URL, frame, output directory, and settings."""
        form_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E293B")
        form_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # 1. YouTube URL Input
        url_subframe = ctk.CTkFrame(form_frame, fg_color="transparent")
        url_subframe.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        url_subframe.grid_columnconfigure(1, weight=1)
        
        url_label = ctk.CTkLabel(url_subframe, text="YouTube URL:", width=120, anchor="w", font=("Segoe UI", 12, "bold"))
        url_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        
        self.url_entry = ctk.CTkEntry(url_subframe, placeholder_text="https://www.youtube.com/watch?v=xxxxxxxxxxx")
        self.url_entry.grid(row=0, column=1, padx=0, pady=5, sticky="ew")
        
        # 2. Target Frame Input
        frame_subframe = ctk.CTkFrame(form_frame, fg_color="transparent")
        frame_subframe.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        frame_subframe.grid_columnconfigure(1, weight=1)
        
        frame_label = ctk.CTkLabel(frame_subframe, text="Target Frame:", width=120, anchor="w", font=("Segoe UI", 12, "bold"))
        frame_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        
        self.frame_entry = ctk.CTkEntry(frame_subframe, placeholder_text="e.g. 500 (Enter frame index number)")
        self.frame_entry.grid(row=0, column=1, padx=0, pady=5, sticky="ew")
        
        # 3. Output Directory Picker (Default is workspace folder)
        self.output_picker = PathPicker(
            form_frame, 
            label_text="Output Folder:", 
            is_directory=True, 
            default_val=self.base_dir,
            placeholder="Select directory where PNG & Markdown will be saved"
        )
        self.output_picker.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        
        # 4. FFmpeg Settings Option (Accordion/Collapsible style frame)
        self.ffmpeg_picker = PathPicker(
            form_frame,
            label_text="FFmpeg Path:",
            is_directory=False,
            default_val=env_checker.get_default_ffmpeg_path(),
            placeholder="System FFmpeg default (or path to ffmpeg.exe)",
            file_types=[("FFmpeg Executable", "ffmpeg.exe;ffmpeg"), ("All Files", "*.*")]
        )
        self.ffmpeg_picker.grid(row=3, column=0, padx=15, pady=5, sticky="ew")
        
        # 5. Extraction Actions
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, padx=15, pady=15, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        
        self.extract_btn = ctk.CTkButton(
            btn_frame, 
            text="Extract Target Frame", 
            height=40,
            fg_color="#2563EB", 
            hover_color="#1D4ED8",
            font=("Segoe UI", 13, "bold"),
            command=self._start_extraction
        )
        self.extract_btn.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        
        self.clear_btn = ctk.CTkButton(
            btn_frame, 
            text="Clear Form", 
            height=40,
            width=120,
            fg_color="#4B5563", 
            hover_color="#374151",
            font=("Segoe UI", 12),
            command=self._clear_form
        )
        self.clear_btn.grid(row=0, column=1, padx=0, pady=5, sticky="e")

    def _create_progress_area(self):
        """Creates progress bar and status output."""
        self.progress_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E293B")
        self.progress_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame, 
            text="Status: Ready", 
            font=("Segoe UI", 12, "bold"),
            text_color="#E5E7EB"
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.progress_bar.set(0)

    def _create_log_console(self):
        """Creates the scrollable terminal-like log view."""
        log_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#0F172A")
        log_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        log_label = ctk.CTkLabel(
            log_frame, 
            text="Activity Logs", 
            font=("Segoe UI", 11, "bold"),
            text_color="#94A3B8"
        )
        log_label.grid(row=0, column=0, padx=15, pady=(8, 2), sticky="w")
        
        self.console = ConsoleView(log_frame)
        self.console.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def _log_to_console(self, message):
        """Thread-safe way to append logs to the UI textbox."""
        self.after(0, lambda: self.console.write_log(message))

    def _clear_form(self):
        """Resets the input fields and progress bar."""
        self.url_entry.delete(0, "end")
        self.frame_entry.delete(0, "end")
        self.progress_bar.set(0)
        self.status_label.configure(text="Status: Ready", text_color="#E5E7EB")
        logger.info("Form cleared.")

    def _async_env_check(self):
        """Runs the environmental check on a background thread to prevent UI lag on startup."""
        def run_check():
            ffmpeg_p = self.ffmpeg_picker.get_path()
            env = env_checker.check_environment(ffmpeg_p)
            self.task_queue.put(("ENV_CHECK_DONE", env))
            
        threading.Thread(target=run_check, daemon=True).start()

    def _start_extraction(self):
        """Validates input data and launches the extraction background thread."""
        url = self.url_entry.get().strip()
        frame_str = self.frame_entry.get().strip()
        out_dir = self.output_picker.get_path()
        ffmpeg_p = self.ffmpeg_picker.get_path()
        
        # 1. Validation
        if not url:
            messagebox.showerror("Input Error", "Please enter a YouTube video URL.")
            return
            
        if not re.search(r"(youtube\.com|youtu\.be)", url.lower()):
            messagebox.showerror("Input Error", "Invalid video link. Only YouTube links are supported.")
            return
            
        if not frame_str:
            messagebox.showerror("Input Error", "Please specify a target frame number.")
            return
            
        try:
            frame_number = int(frame_str)
            if frame_number < 0:
                raise ValueError("Frame index must be non-negative")
        except ValueError:
            messagebox.showerror("Input Error", "Target frame must be a positive integer (e.g., 0, 120, 500).")
            return
            
        if not os.path.exists(out_dir):
            messagebox.showerror("Path Error", f"The chosen output directory does not exist:\n{out_dir}")
            return

        # 2. Lock UI Elements during run
        self._toggle_ui_state("disabled")
        self.status_label.configure(text="Status: Processing...", text_color="#F59E0B")
        self.progress_bar.set(0.1)
        
        # 3. Launch processing thread
        extraction_thread = threading.Thread(
            target=self._run_extraction_process,
            args=(url, frame_number, out_dir, ffmpeg_p),
            daemon=True
        )
        extraction_thread.start()

    def _toggle_ui_state(self, state):
        """Toggles entry fields and buttons to prevent double-submits."""
        self.url_entry.configure(state=state)
        self.frame_entry.configure(state=state)
        self.extract_btn.configure(state=state)
        self.clear_btn.configure(state=state)
        self.output_picker.entry.configure(state=state)
        self.output_picker.browse_btn.configure(state=state)
        self.ffmpeg_picker.entry.configure(state=state)
        self.ffmpeg_picker.browse_btn.configure(state=state)

    def _run_extraction_process(self, url, frame_number, output_dir, ffmpeg_path):
        """Target for background thread. Executes full extraction workflow."""
        try:
            # Step 1: Environment diagnostics
            self.task_queue.put(("STATUS_UPDATE", ("Detecting software tools...", 0.15)))
            env_info = env_checker.check_environment(ffmpeg_path)
            
            # Double check ffmpeg status
            if "Not Found" in env_info["ffmpeg"] or "Unavailable" in env_info["ffmpeg"]:
                raise Exception("FFmpeg executable could not be verified. Please check FFmpeg Path settings.")

            # Step 2: Fetch video formats & metadata
            self.task_queue.put(("STATUS_UPDATE", ("Fetching YouTube metadata...", 0.3)))
            video_info = yt_client.fetch_video_info(url)
            
            fps = video_info["fps"]
            total_duration = video_info["duration"]
            title_sanitized = re.sub(r'[\\/*?:"<>|]', "", video_info["title"]) # sanitize filename chars
            title_sanitized = title_sanitized.replace(" ", "_")[:50] # replace spaces, limit length
            
            # Timestamp calculation
            timestamp_sec = frame_number / fps
            
            # Validate frame index doesn't exceed video length (if duration is known)
            if total_duration:
                total_frames = total_duration * fps
                if frame_number > total_frames:
                    logger.warning(f"Requested frame index {frame_number} exceeds estimated total frames ({total_frames:.1f}). Proceeding anyway.")
            
            # Step 3: Define file names
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_base = f"yt_{title_sanitized}_fr{frame_number}_{timestamp_str}"
            
            temp_png = os.path.join(output_dir, f"temp_{filename_base}.png")
            final_png = os.path.join(output_dir, f"{filename_base}.png")
            final_md = os.path.join(output_dir, f"{filename_base}.md")
            
            # Step 4: Extract the raw frame
            self.task_queue.put(("STATUS_UPDATE", ("Extracting frame from stream...", 0.6)))
            ffmpeg_wrapper.extract_frame_to_png(
                stream_url=video_info["stream_url"],
                frame_number=frame_number,
                fps=fps,
                output_path=temp_png,
                ffmpeg_path=ffmpeg_path
            )
            
            # Step 5: Embed PNG metadata chunk
            self.task_queue.put(("STATUS_UPDATE", ("Injecting chunk metadata...", 0.8)))
            
            # Prepare metadata keys
            metadata = {
                "Copyright": "YouTube Video Creator",
                "Source": url,
                "ExtractionFrame": str(frame_number),
                "ExtractionTimestamp": datetime.now().isoformat(),
                "ExtractionSoftware": "YouTube Frame Extractor v1.0.0",
                "VideoTitle": video_info["title"],
                "VideoCodec": video_info["vcodec"],
                "VideoResolution": f"{video_info['width']}x{video_info['height']}"
            }
            
            metadata_writer.save_png_with_metadata(
                temp_img_path=temp_png,
                final_img_path=final_png,
                metadata_dict=metadata
            )
            
            # Remove temp file
            if os.path.exists(temp_png):
                os.remove(temp_png)

            # Step 6: Generate Markdown metadata
            self.task_queue.put(("STATUS_UPDATE", ("Generating Markdown log...", 0.9)))
            
            # Enrich dict for md generator
            video_info["frame_number"] = frame_number
            video_info["timestamp_seconds"] = timestamp_sec
            video_info["extraction_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            video_info["image_file_path"] = final_png
            
            markdown_generator.generate_metadata_markdown(
                output_md_path=final_md,
                info_dict=video_info,
                env_info=env_info
            )
            
            self.task_queue.put(("STATUS_UPDATE", ("Success", 1.0)))
            self.task_queue.put(("SUCCESS_MESSAGE", f"Saved image and markdown successfully!\n\nImage: {os.path.basename(final_png)}\nMarkdown: {os.path.basename(final_md)}"))
            
        except Exception as e:
            logger.error(f"Execution Error: {e}")
            self.task_queue.put(("ERROR_OCCURRED", str(e)))
            
            # Clean up temp file if crashed
            try:
                if 'temp_png' in locals() and os.path.exists(temp_png):
                    os.remove(temp_png)
            except:
                pass

    def _process_queue(self):
        """Processes messages from background threads in the Tkinter main loop."""
        try:
            while True:
                msg_type, data = self.task_queue.get_nowait()
                
                if msg_type == "STATUS_UPDATE":
                    status_text, progress_val = data
                    self.status_label.configure(text=f"Status: {status_text}", text_color="#F59E0B")
                    self.progress_bar.set(progress_val)
                    
                elif msg_type == "SUCCESS_MESSAGE":
                    self.status_label.configure(text="Status: Completed", text_color="#10B981")
                    self.progress_bar.set(1.0)
                    self._toggle_ui_state("normal")
                    messagebox.showinfo("Extraction Success", data)
                    
                elif msg_type == "ERROR_OCCURRED":
                    self.status_label.configure(text="Status: Error Encountered", text_color="#EF4444")
                    self.progress_bar.set(0)
                    self._toggle_ui_state("normal")
                    messagebox.showerror("Extraction Error", f"An error occurred during frame extraction:\n\n{data}")
                    
                elif msg_type == "ENV_CHECK_DONE":
                    # Update FFmpeg version in settings picker label/placeholder
                    ffmpeg_version = data.get("ffmpeg", "Not Found")
                    logger.info(f"Verified environment. FFmpeg version detected: {ffmpeg_version}")
                    
                self.task_queue.task_done()
        except queue.Empty:
            pass
        finally:
            # Schedule next queue check
            self.after(100, self._process_queue)
