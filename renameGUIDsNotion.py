import os
import re
import shutil
from typing import Dict, List, Tuple

# Regular expression to match GUIDs in filenames (preceded by a space)
GUID_PATTERN = re.compile(r' ([a-f0-9]{32})(?=\.[^.]+|$)')
# Regular expression to match GUIDs in markdown paths (with %20 before)
MD_GUID_PATTERN = re.compile(r'%20([a-f0-9]{32})')


def remove_guids_in_directory(root_dir: str):
    # First pass: collect all GUIDs and their new names
    guid_map: Dict[str, List[Tuple[str, str]]] = {}

    # Walk through the directory to collect all GUIDs
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Process files first
        for filename in filenames:
            process_guid_in_name(filename, guid_map, dirpath, is_file=True)

        # Then process directories
        for dirname in dirnames:
            process_guid_in_name(dirname, guid_map, dirpath, is_file=False)

    # Second pass: rename files and folders
    rename_files_and_folders(root_dir, guid_map)

    # Third pass: process markdown files
    process_markdown_files(root_dir)


def process_guid_in_name(name: str, guid_map: Dict[str, List[Tuple[str, str]]], dirpath: str, is_file: bool):
    match = GUID_PATTERN.search(name)
    if not match:
        return

    guid = match.group(1)
    new_name = GUID_PATTERN.sub('', name)

    if guid not in guid_map:
        guid_map[guid] = []

    full_path = os.path.join(dirpath, name)
    guid_map[guid].append((full_path, new_name, is_file))


def rename_files_and_folders(root_dir: str, guid_map: Dict[str, List[Tuple[str, str]]]):
    # Process GUIDs that appear multiple times first
    for guid, entries in guid_map.items():
        if len(entries) > 1:
            # These need to be renamed with numbers to avoid collisions
            for i, (old_path, new_name, is_file) in enumerate(entries, 1):
                dirname = os.path.dirname(old_path)
                base, ext = os.path.splitext(new_name) if is_file else (new_name, '')

                # Try the name without number first
                if i == 1:
                    candidate = new_name
                else:
                    candidate = f"{base} {i}{ext}" if is_file else f"{new_name} {i}"

                # Ensure the new name doesn't collide with existing files
                counter = i
                while True:
                    new_path = os.path.join(dirname, candidate)
                    if not os.path.exists(new_path) or new_path == old_path:
                        break
                    counter += 1
                    candidate = f"{base} {counter}{ext}" if is_file else f"{new_name} {counter}"

                # Perform the rename
                if old_path != new_path:
                    os.rename(old_path, new_path)
        else:
            # Single occurrence - just remove the GUID
            old_path, new_name, is_file = entries[0]
            dirname = os.path.dirname(old_path)
            new_path = os.path.join(dirname, new_name)

            # Check for name collisions
            if os.path.exists(new_path) and new_path != old_path:
                base, ext = os.path.splitext(new_name) if is_file else (new_name, '')
                counter = 1
                while True:
                    candidate = f"{base} {counter}{ext}" if is_file else f"{new_name} {counter}"
                    candidate_path = os.path.join(dirname, candidate)
                    if not os.path.exists(candidate_path):
                        break
                    counter += 1
                new_path = candidate_path

            if old_path != new_path:
                os.rename(old_path, new_path)


def process_markdown_files(root_dir: str):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.md'):
                filepath = os.path.join(dirpath, filename)
                process_guid_in_markdown(filepath)


def process_guid_in_markdown(filepath: str):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = MD_GUID_PATTERN.sub('', content)

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
    except (IOError, UnicodeDecodeError) as e:
        print(f"Error processing {filepath}: {str(e)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python remove_guids.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)

    remove_guids_in_directory(directory)
    print("GUID removal completed.")