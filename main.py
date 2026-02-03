
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import sys
import os

# Import our modules
# Note: In the final EXE, we need to handle paths correctly.
try:
    from ocr_processor import OCRProcessor
    from excel_manager import ExcelManager
except ImportError as e:
    # Fallback for dev environment if needed, but usually imports work
    print(f"Import Error: {e}")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR to Excel Converter")
        self.root.geometry("600x500")

        # Variables
        self.image_path = tk.StringVar()
        self.excel_path = tk.StringVar()

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Image Selection
        tk.Label(self.root, text="Step 1: Select Input Image (Weekly Report)").pack(pady=5)
        frame_img = tk.Frame(self.root)
        frame_img.pack(fill=tk.X, padx=20)
        tk.Entry(frame_img, textvariable=self.image_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_img, text="Browse...", command=self.browse_image).pack(side=tk.LEFT)

        # Excel Selection
        tk.Label(self.root, text="Step 2: Select Target Excel (Existing or New)").pack(pady=5)
        frame_excel = tk.Frame(self.root)
        frame_excel.pack(fill=tk.X, padx=20)
        tk.Entry(frame_excel, textvariable=self.excel_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_excel, text="Browse...", command=self.browse_excel).pack(side=tk.LEFT)

        # Action
        tk.Button(self.root, text="Start Conversion", command=self.start_conversion_thread, bg="#4CAF50", fg="white", height=2).pack(pady=20, fill=tk.X, padx=50)

        # Logs
        tk.Label(self.root, text="Logs:").pack(anchor=tk.W, padx=20)
        self.log_area = scrolledtext.ScrolledText(self.root, height=15)
        self.log_area.pack(fill=tk.BOTH, padx=20, pady=5, expand=True)

    def log(self, message):
        # Ensure UI updates happen on the main thread
        self.root.after(0, lambda: self._update_log(message))

    def _update_log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def browse_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if filename:
            self.image_path.set(filename)

    def browse_excel(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        # If user picks an existing file, asksaveasfilename asks to overwrite?
        # Actually for 'updating' we might want askopenfilename?
        # But user might want to create NEW.
        # Let's verify if file exists in logic.
        if filename:
            self.excel_path.set(filename)

    def start_conversion_thread(self):
        if not self.image_path.get() or not self.excel_path.get():
            messagebox.showerror("Error", "Please select both image and excel paths.")
            return

        threading.Thread(target=self.run_conversion, daemon=True).start()

    def run_conversion(self):
        img_p = self.image_path.get()
        exc_p = self.excel_path.get()

        self.log("Initializing OCR Engine (PaddleOCR)... Please wait.")
        try:
            # We initialize OCR here to avoid UI freeze during startup
            processor = OCRProcessor()

            self.log(f"Processing Image: {img_p}")
            data = processor.process_image(img_p)

            if not data:
                self.log("Warning: No valid data found in image.")
                return

            self.log(f"Found {len(data)} task rows. Updating Excel...")

            manager = ExcelManager(exc_p)
            manager.update_or_create(data)

            self.log("Done! Success.")
            self.root.after(0, lambda: messagebox.showinfo("Success", "Conversion Completed Successfully!"))

        except Exception as e:
            self.log(f"Error: {str(e)}")
            import traceback
            tb = traceback.format_exc()
            self.log(tb)
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
