import os
import re
import shutil

# GUID pattern: space + 32 hex characters
GUID_REGEX = re.compile(r'(?: ?)([a-fA-F0-9]{32})')

# To track seen names and avoid conflicts
name_map = {}
used_names = set()

def strip_guid(name):
    """Remove GUID (preceded by a space) from the name"""
    return GUID_REGEX.sub('', name).strip()

def unique_name(name, is_file=False, extension=''):
    """Return a unique name to avoid collisions"""
    base = name
    i = 1
    candidate = name
    while candidate + extension in used_names:
        candidate = f"{base}_{i}"
        i += 1
    used_names.add(candidate + extension)
    return candidate + extension

def rename_files_and_folders(root_dir):
    # Walk from the deepest folders up (bottom-up=True)
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Process files
        for filename in filenames:
            old_path = os.path.join(dirpath, filename)
            base, ext = os.path.splitext(filename)
            clean_base = strip_guid(base)
            if base != clean_base:
                new_name = name_map.get(clean_base, unique_name(clean_base, is_file=True, extension=ext))
                name_map[base] = new_name
                new_path = os.path.join(dirpath, new_name)
                print(f"Renaming file: {old_path} -> {new_path}")
                os.rename(old_path, new_path)

        # Process directories
        for dirname in dirnames:
            old_path = os.path.join(dirpath, dirname)
            clean_name = strip_guid(dirname)
            if dirname != clean_name:
                new_name = name_map.get(clean_name, unique_name(clean_name))
                name_map[dirname] = new_name
                new_path = os.path.join(dirpath, new_name)
                print(f"Renaming folder: {old_path} -> {new_path}")
                os.rename(old_path, new_path)

def fix_markdown_links(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.md'):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Replace %20 + GUID patterns
                updated_content = re.sub(r'%20[a-fA-F0-9]{32}', '', content)
                # Also catch plain space + GUID if they somehow got encoded incorrectly
                updated_content = re.sub(r' ?[a-fA-F0-9]{32}', '', updated_content)

                if content != updated_content:
                    print(f"Fixing markdown links in: {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Remove GUIDs from filenames and markdown links.")
    parser.add_argument("directory", help="Root directory to process")
    args = parser.parse_args()

    root = os.path.abspath(args.directory)
    rename_files_and_folders(root)
    fix_markdown_links(root)
    print("Processing complete.")
