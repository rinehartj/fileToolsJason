import os
import subprocess
import tkinter as tk
from tkinter import filedialog
import sys

# Path to local ExifTool executable and associated folder
TOOLS_DIR = os.path.join(os.path.dirname(__file__), "tools")
EXIFTOOL_PATH = os.path.join(TOOLS_DIR, "exiftool.exe")
EXIFTOOL_FILES_DIR = os.path.join(TOOLS_DIR, "exiftool_files")

def check_required_files():
    """
    Checks for the presence of exiftool.exe and exiftool_files directory.
    If missing, instructs the user and exits the program.
    """
    missing = []
    if not os.path.isfile(EXIFTOOL_PATH):
        missing.append("exiftool.exe")
    if not os.path.isdir(EXIFTOOL_FILES_DIR):
        missing.append("exiftool_files folder")

    if missing:
        print("\n=== Missing Required Files ===")
        print("The following item(s) are missing in the 'tools' folder:")
        for item in missing:
            print(f" - {item}")
        print("\nPlease do the following:")
        print("1. Download ExifTool from https://exiftool.org")
        print("2. Rename the downloaded file from 'exiftool(-k).exe' to 'exiftool.exe'")
        print("3. Place 'exiftool.exe' and the 'exiftool_files' folder into the 'tools' directory")
        print("4. Restart this application\n")
        sys.exit(1)

def add_date_taken_exiftool(file_path, date_taken):
    """
    Uses a local ExifTool executable to set 'DateTimeOriginal' and 'DateTimeDigitized'.
    """
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return False

        # Allow date with or without time
        if len(date_taken) == 10 and date_taken[4] == ':' and date_taken[7] == ':':
            date_taken += " 00:00:00"
        elif len(date_taken) != 19 or date_taken[4] != ':' or date_taken[7] != ':' or date_taken[10] != ' ':
            print("Error: Date must be in format 'YYYY:MM:DD' or 'YYYY:MM:DD HH:MM:SS'.")
            return False

        cmd = [
            EXIFTOOL_PATH,
            f"-DateTimeOriginal={date_taken}",
            f"-DateTimeDigitized={date_taken}",
            "-overwrite_original",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ExifTool stderr:\n{result.stderr}")
            return False

        print(f"Success: Metadata updated via ExifTool on '{file_path}'.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"ExifTool error on '{file_path}': {e}")
        return False

def select_photos():
    """
    Opens a file dialog for the user to select photos.
    """
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Select Photos",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.tif;*.tiff")]
    )
    return list(file_paths)

if __name__ == "__main__":
    check_required_files()

    print("Please select the photos to update metadata.")
    selected_files = select_photos()

    if not selected_files:
        print("No photos were selected.")
    else:
        date_taken = input("Enter the date taken (YYYY:MM:DD or YYYY:MM:DD HH:MM:SS): ").strip()
        for file_path in selected_files:
            add_date_taken_exiftool(file_path, date_taken)
