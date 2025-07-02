import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox


def select_folder():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Select Folder Containing Numbered Files")


def reverse_rename(folder):
    pattern = re.compile(r"(\d+)\.(jpg|jpeg|png|gif|bmp)$", re.IGNORECASE)

    files = [f for f in os.listdir(folder) if pattern.match(f)]
    if not files:
        messagebox.showerror("Error", "No matching image files found.")
        return

    # Extract numbers and sort descending
    numbered_files = []
    for f in files:
        match = pattern.match(f)
        if match:
            number = int(match.group(1))
            ext = match.group(2)
            numbered_files.append((number, f, ext))

    numbered_files.sort(reverse=True)  # highest number first

    # Rename step 1: temp rename to avoid collisions
    temp_names = []
    for i, (_, filename, ext) in enumerate(numbered_files, start=1):
        temp_name = f"temp_rename_{i}.{ext}"
        os.rename(os.path.join(folder, filename), os.path.join(folder, temp_name))
        temp_names.append((temp_name, i, ext))

    # Rename step 2: to final names
    for temp_name, new_num, ext in temp_names:
        new_name = f"{new_num}.{ext.lower()}"
        os.rename(os.path.join(folder, temp_name), os.path.join(folder, new_name))

    messagebox.showinfo("Success", f"Renamed {len(temp_names)} files in reverse order.")


if __name__ == "__main__":
    folder_path = select_folder()
    if folder_path:
        reverse_rename(folder_path)
