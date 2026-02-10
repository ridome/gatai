
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import sys
import os

# Import our modules
try:
    from input_parser import InputExcelParser
    from excel_manager import ExcelManager
except ImportError as e:
    print(f"Import Error: {e}")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Merge Tool")
        self.root.geometry("600x500")

        # Variables
        self.input_path = tk.StringVar()
        self.excel_path = tk.StringVar()

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Input Selection
        tk.Label(self.root, text="Step 1: Select Input Excel (Weekly Report)").pack(pady=5)
        frame_input = tk.Frame(self.root)
        frame_input.pack(fill=tk.X, padx=20)
        tk.Entry(frame_input, textvariable=self.input_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_input, text="Browse...", command=self.browse_input).pack(side=tk.LEFT)

        # Output Selection
        tk.Label(self.root, text="Step 2: Select Target Excel (Master Table)").pack(pady=5)
        frame_excel = tk.Frame(self.root)
        frame_excel.pack(fill=tk.X, padx=20)
        tk.Entry(frame_excel, textvariable=self.excel_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_excel, text="Browse...", command=self.browse_output).pack(side=tk.LEFT)

        # Action
        tk.Button(self.root, text="Start Merge", command=self.start_conversion_thread, bg="#4CAF50", fg="white", height=2).pack(pady=20, fill=tk.X, padx=50)

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

    def browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
        if filename:
            self.input_path.set(filename)

    def browse_output(self):
        # Allow selecting existing or creating new
        # Usually users want to pick an existing one to update, or type a new name
        # askopenfilename is better for "Select Target" if it exists.
        # But if they want to create new, they might need asksaveasfilename.
        # Let's provide a generic file dialog or just askopenfilename and if they want new they can type path manually?
        # A safer bet for "Target" which *usually* exists is askopenfilename, but let's stick to user choice.
        # I'll use askopenfilename but if they cancel, they can paste path.
        filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if filename:
            self.excel_path.set(filename)
        else:
            # If they want to create new, maybe offer saveas?
            # Let's add a small "New File" button? Or just let them browse save as if they click browse?
            # Simpler: Browse for existing. If they want new, they type it or we add a "Create New" button.
            # For now, let's assume update existing is primary. If they want new, they can use the entry box.
            pass

    def start_conversion_thread(self):
        if not self.input_path.get() or not self.excel_path.get():
            messagebox.showerror("Error", "Please select both input and target excel paths.")
            return

        threading.Thread(target=self.run_conversion, daemon=True).start()

    def run_conversion(self):
        inp_p = self.input_path.get()
        out_p = self.excel_path.get()

        self.log("Initializing...")
        try:
            parser = InputExcelParser()

            self.log(f"Parsing Input Excel: {inp_p}")
            data = parser.parse(inp_p)

            if not data:
                self.log("Warning: No valid data found in input file.")
                return

            self.log(f"Found {len(data)} task rows. Updating Target Excel...")

            manager = ExcelManager(out_p)
            manager.update_or_create(data)

            self.log("Done! Success.")
            self.root.after(0, lambda: messagebox.showinfo("Success", "Merge Completed Successfully!"))

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
