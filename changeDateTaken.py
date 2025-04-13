from PIL import Image
import piexif
import os
import tkinter as tk
from tkinter import filedialog

def add_date_taken(file_path, date_taken):
    """
    Adds or updates the "Date Taken" metadata for an image file without reducing quality.

    Args:
        file_path (str): The path to the image file.
        date_taken (str): The date to set in "YYYY:MM:DD HH:MM:SS" format.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return False

        # Ensure the date format is correct
        if len(date_taken) != 19 or date_taken[4] != ':' or date_taken[7] != ':' or date_taken[10] != ' ':
            print("Error: Date must be in the format 'YYYY:MM:DD HH:MM:SS'.")
            return False

        # Open the image
        img = Image.open(file_path)

        # Get existing EXIF data or create new EXIF data
        exif_data = piexif.load(img.info.get("exif", b""))

        # Set the DateTimeOriginal and DateTimeDigitized tags
        exif_data["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_taken.encode("utf-8")
        exif_data["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_taken.encode("utf-8")

        # Convert EXIF data back to bytes
        exif_bytes = piexif.dump(exif_data)

        # Preserve original quality by copying the original settings
        img.save(file_path, "jpeg", exif=exif_bytes, quality="keep", subsampling=0)

        print(f"Success: 'Date Taken' metadata added to '{file_path}'.")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def select_photos():
    """
    Opens a file dialog for the user to select photos.

    Returns:
        list: A list of selected file paths.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_paths = filedialog.askopenfilenames(title="Select Photos", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    return list(file_paths)


# Example usage
if __name__ == "__main__":
    # Prompt the user to select a folder and photos
    print("Please select the photos to update metadata.")
    selected_files = select_photos()

    if not selected_files:
        print("No photos were selected.")
    else:
        # Input the timestamp
        date_taken = input("Enter the date taken (YYYY:MM:DD HH:MM:SS): ").strip()

        # Update metadata for each selected photo
        for file_path in selected_files:
            add_date_taken(file_path, date_taken)
