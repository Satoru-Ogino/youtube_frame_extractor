import customtkinter as ctk
from tkinter import filedialog

class PathPicker(ctk.CTkFrame):
    """
    Compound component for picking a directory or a file path.
    Contains a label, an entry field, and a "Browse" button.
    """
    def __init__(self, master, label_text, is_directory=True, default_val="", placeholder="", file_types=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.is_directory = is_directory
        self.file_types = file_types or [("All Files", "*.*")]
        
        # Grid layout configuration
        self.grid_columnconfigure(1, weight=1)
        
        # Label
        self.label = ctk.CTkLabel(self, text=label_text, width=120, anchor="w", font=("Segoe UI", 12, "bold"))
        self.label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        
        # Entry field
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        self.entry.insert(0, default_val)
        self.entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ew")
        
        # Browse button
        self.browse_btn = ctk.CTkButton(
            self, 
            text="Browse...", 
            width=80, 
            command=self._browse_path,
            font=("Segoe UI", 11)
        )
        self.browse_btn.grid(row=0, column=2, padx=0, pady=5, sticky="e")
        
    def _browse_path(self):
        if self.is_directory:
            selected = filedialog.askdirectory(initialdir=self.get_path() or None)
        else:
            selected = filedialog.askopenfilename(
                initialdir=os.path.dirname(self.get_path()) if self.get_path() else None,
                filetypes=self.file_types
            )
            
        if selected:
            self.entry.delete(0, "end")
            self.entry.insert(0, selected)
            
    def get_path(self):
        return self.entry.get().strip()
        
    def set_path(self, path):
        self.entry.delete(0, "end")
        self.entry.insert(0, path)

class ConsoleView(ctk.CTkTextbox):
    """
    Custom textbox configured for displaying log streams.
    Auto-scrolls to the bottom on new writes.
    """
    def __init__(self, master, **kwargs):
        # Enforce read-only state for normal users, scrollable log console styling
        super().__init__(
            master, 
            wrap="word", 
            font=("Consolas", 11),
            fg_color="#1E1E1E",
            text_color="#D4D4D4",
            **kwargs
        )
        self.configure(state="disabled")
        
    def write_log(self, text):
        self.configure(state="normal")
        self.insert("end", text + "\n")
        self.see("end")
        self.configure(state="disabled")
        
    def clear_log(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")
