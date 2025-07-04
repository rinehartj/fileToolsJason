import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
from send2trash import send2trash
from collections import defaultdict


def calculate_file_hash(filepath, block_size=65536):
    """Calculate SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read(block_size)
        while buf:
            hasher.update(buf)
            buf = f.read(block_size)
    return hasher.hexdigest()


def get_files_with_hashes(folder):
    """Return a dictionary of {hash: [(filepath, size)]}"""
    files_info = defaultdict(list)
    for root, _, files in os.walk(folder):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                file_hash = calculate_file_hash(filepath)
                file_size = os.path.getsize(filepath)
                files_info[file_hash].append((filepath, file_size))
            except (IOError, OSError):
                continue  # Skip unreadable files
    return files_info


def compare_and_clean(folder1, folder2):
    """Compare two folders and move matching duplicates from folder2 to Recycle Bin."""
    print("Calculating hashes for folder 1...")
    folder1_data = get_files_with_hashes(folder1)

    print("Calculating hashes for folder 2...")
    folder2_data = get_files_with_hashes(folder2)

    folder1_hash_map = {hash_: {size for _, size in paths} for hash_, paths in folder1_data.items()}

    duplicates_to_remove = []
    for hash_val, file_list in folder2_data.items():
        if hash_val in folder1_hash_map:
            folder1_sizes = folder1_hash_map[hash_val]
            for filepath, size in file_list:
                if size in folder1_sizes:
                    duplicates_to_remove.append(filepath)

    if duplicates_to_remove:
        print(f"Found {len(duplicates_to_remove)} duplicate file(s) in folder2.")
        for filepath in duplicates_to_remove:
            norm_path = os.path.normpath(filepath)
            try:
                print(f"Moving to recycle bin: {norm_path}")
                send2trash(norm_path)
            except Exception as e:
                print(f"Error moving {norm_path} to recycle bin: {str(e)}")
        print("Duplicate files moved to recycle bin.")
    else:
        print("No duplicate files found in folder2.")


def select_folder(title):
    """Open a folder selection dialog."""
    return filedialog.askdirectory(title=title)


if __name__ == "__main__":
    print("This program compares two folders, identifies files in the second folder that are exact duplicates "
          "(based on SHA-256 hash AND file size) of files in the first folder, and moves those duplicates to the Recycle Bin.\nWarning: May ignore some metadata, including \"Comments\" in Properties>Details diaglog on Windows.")

    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    # Select first folder
    folder1 = select_folder("Select the first folder (reference folder)")
    if not folder1:
        messagebox.showerror("Error", "Reference folder selection was canceled.")
        exit()

    # Suggest parent directory when picking second folder
    parent_dir = os.path.dirname(folder1)
    folder2 = filedialog.askdirectory(
        title="Select the second folder (folder to clean duplicates from)",
        initialdir=parent_dir
    )

    if not folder2:
        messagebox.showerror("Error", "Target folder selection was canceled.")
    elif not os.path.isdir(folder1) or not os.path.isdir(folder2):
        messagebox.showerror("Error", "One or both folder paths are invalid.")
    else:
        compare_and_clean(folder1, folder2)
        messagebox.showinfo("Done", "Duplicate cleanup completed. See console output for details.")

