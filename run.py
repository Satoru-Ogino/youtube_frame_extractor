import os
import sys

# Add project root directory to sys.path to allow absolute imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_dependencies():
    """
    Checks if the required python packages are installed.
    If missing, prompts the user and exits.
    """
    missing_packages = []
    
    # 1. yt-dlp
    try:
        import yt_dlp
    except ImportError:
        missing_packages.append("yt-dlp")
        
    # 2. Pillow
    try:
        import PIL
    except ImportError:
        missing_packages.append("Pillow")
        
    # 3. customtkinter
    try:
        import customtkinter
    except ImportError:
        missing_packages.append("customtkinter")
        
    # 4. imageio-ffmpeg
    try:
        import imageio_ffmpeg
    except ImportError:
        missing_packages.append("imageio-ffmpeg")
        
    if missing_packages:
        print("Error: Missing required Python packages.")
        print(f"Please install the missing dependencies: {', '.join(missing_packages)}")
        print("\nYou can run the following command to install them:")
        print(f"  pip install {' '.join(missing_packages)}")
        
        # Show graphic popup dialog if tkinter is available
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw() # hide main window
            messagebox.showerror(
                "Missing Dependencies",
                f"The following required Python packages are missing:\n"
                f"{', '.join(missing_packages)}\n\n"
                f"Please run the following command in terminal/powershell:\n"
                f"pip install {' '.join(missing_packages)}"
            )
        except Exception:
            pass
            
        sys.exit(1)

def main():
    # Verify environment dependencies
    check_dependencies()
    
    # Import and run GUI
    from src.gui.main_window import MainWindow
    
    print("Launching YouTube Frame Extractor...")
    # Initialize main window passing the project root directory
    app = MainWindow(project_root)
    app.mainloop()

if __name__ == "__main__":
    main()
