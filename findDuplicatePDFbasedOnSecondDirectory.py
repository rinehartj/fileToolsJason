import os
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox
from send2trash import send2trash
from pathlib import Path

# --- Helper Functions ---
def get_pdf_hashes(folder):
    hashes = {}
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        hashes[file_hash] = filepath
                except Exception as e:
                    print(f"Error hashing {filepath}: {e}")
    return hashes

def find_duplicates(original_folder, reference_folder):
    reference_hashes = get_pdf_hashes(reference_folder)
    duplicates = []
    for root, _, files in os.walk(original_folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                orig_path = os.path.join(root, file)
                try:
                    with open(orig_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        if file_hash in reference_hashes:
                            duplicates.append((orig_path, reference_hashes[file_hash]))
                except Exception as e:
                    print(f"Error hashing {orig_path}: {e}")
    return duplicates

# --- GUI ---
class DuplicateFinderGUI:
    def __init__(self, root, original, reference):
        self.root = root
        self.root.title("PDF Duplicate Finder")

        self.duplicates = find_duplicates(original, reference)
        self.check_vars = []

        if not self.duplicates:
            messagebox.showinfo("No Duplicates", "No duplicate PDF files found.")
            self.root.destroy()
            return

        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        for i, (orig, ref) in enumerate(self.duplicates):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.scrollable_frame, variable=var)
            chk.grid(row=i, column=0, sticky='nw')
            tk.Label(self.scrollable_frame, text=f"Original: {orig}", wraplength=500, anchor='w', justify='left').grid(row=i, column=1, sticky='w')
            tk.Label(self.scrollable_frame, text=f"Reference: {ref}", wraplength=500, anchor='w', justify='left').grid(row=i, column=2, sticky='w')
            self.check_vars.append((var, orig))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.delete_button = ttk.Button(root, text="Delete Selected", command=self.delete_selected)
        self.delete_button.pack(pady=5)

    def delete_selected(self):
        deleted = 0
        for var, filepath in self.check_vars:
            if var.get():
                try:
                    send2trash(filepath)
                    deleted += 1
                except Exception as e:
                    print(f"Failed to delete {filepath}: {e}")

        messagebox.showinfo("Done", f"Deleted {deleted} file(s).")
        self.root.destroy()

# --- Main ---
def main():
    original_folder = "original"
    reference_folder = "reference"

    if not Path(original_folder).exists() or not Path(reference_folder).exists():
        print("Make sure 'original' and 'reference' folders exist in the current directory.")
        return

    root = tk.Tk()
    app = DuplicateFinderGUI(root, original_folder, reference_folder)
    root.mainloop()

if __name__ == "__main__":
    main()
