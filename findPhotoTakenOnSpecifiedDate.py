import os


def find_files_with_prefix(folder_path, prefix):
    """
    Search for files in the specified folder that start with the given prefix.

    Args:
        folder_path (str): The path to the folder to search.
        prefix (str): The prefix to match filenames against.

    Returns:
        List of matching file paths.
    """
    matching_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.startswith(prefix):
                full_path = os.path.join(root, file)
                matching_files.append(full_path)

    return matching_files


if __name__ == "__main__":
    folder = input("Enter the full path to the folder: ").strip()
    prefix = input("Enter the file prefix to search for: ").strip()

    if not os.path.isdir(folder):
        print(f"Error: '{folder}' is not a valid directory.")
    else:
        results = find_files_with_prefix(folder, prefix)

        if results:
            print("\nMatching files:")
            for f in results:
                print(f)
        else:
            print("No files found with the given prefix.")
