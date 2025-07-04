import os
import filecmp
import tkinter as tk
from tkinter import filedialog, messagebox


def compare_directories(dir1, dir2):
    print("\nStarting recursive comparison...\n")

    comparison = filecmp.dircmp(dir1, dir2)

    # Report files only in one of the directories
    if comparison.left_only:
        print(f"Only in {dir1}:")
        for item in comparison.left_only:
            print(f"  {item}")

    if comparison.right_only:
        print(f"Only in {dir2}:")
        for item in comparison.right_only:
            print(f"  {item}")

    # Report files that exist in both but differ
    if comparison.diff_files:
        print(f"Files that differ in both directories:")
        for item in comparison.diff_files:
            print(f"  {item}")

    # Report funny files (errors)
    if comparison.funny_files:
        print("Problematic files that couldn't be compared:")
        for item in comparison.funny_files:
            print(f"  {item}")

    # Recurse into common subdirectories
    for common_dir in comparison.common_dirs:
        compare_directories(
            os.path.join(dir1, common_dir),
            os.path.join(dir2, common_dir)
        )

def main():
    print("Directory Comparison Tool")
    print("--------------------------")
    print("This tool recursively compares the contents of two directories.")
    print("It lists files unique to each directory, files that differ, and problematic files.\n")

    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask for first directory
    dir1 = filedialog.askdirectory(title="Select First Directory")
    if not dir1:
        messagebox.showerror("Error", "First directory not selected. Exiting.")
        return

    # Ask for second directory, opening one level up from dir1
    parent_dir = os.path.dirname(dir1)
    dir2 = filedialog.askdirectory(title="Select Second Directory", initialdir=parent_dir)
    if not dir2:
        messagebox.showerror("Error", "Second directory not selected. Exiting.")
        return

    print(f"\nSelected Directories:\n  1: {dir1}\n  2: {dir2}")
    compare_directories(dir1, dir2)

    print("\nDisclaimer:")
    print("This tool uses Python’s built-in filecmp module.")
    print("- It compares files by name and shallow content (metadata and size), not deep content by default.")
    print("- Symbolic links, permissions, timestamps, and file encoding differences are not checked.")
    print("- Hidden/system files may be skipped depending on OS or permissions.\n")
    print("For more robust comparison (e.g. hashing file contents), additional logic would be required.")

if __name__ == "__main__":
    main()
