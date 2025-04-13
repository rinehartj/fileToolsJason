import os
import hashlib
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def get_file_hash(filepath, hash_algorithm='sha256', chunk_size=4096):
    print("Called")
    hasher = hashlib.new(hash_algorithm)
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(parent_folder, child_folder, use_hash=False):
    file_map = {}  # Map of file sizes (and hashes if needed) to file paths
    duplicates = []  # List of duplicate file pairs

    # Function to traverse directories and store file sizes/hashes
    def index_files(folder, is_child=False):
        for root, _, files in os.walk(folder):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(filepath)
                    file_key = file_size
                    if use_hash:
                        file_key = (file_size, get_file_hash(filepath))

                    rel_path = os.path.relpath(filepath, parent_folder)

                    if file_key in file_map:
                        if is_child:
                            # Check if it's a duplicate of itself
                            if rel_path != file_map[file_key]:
                                duplicates.append((rel_path, file_map[file_key]))
                    else:
                        file_map[file_key] = rel_path
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    # Index parent files first
    index_files(parent_folder)
    # Then check child files for duplicates
    index_files(child_folder, is_child=True)

    return duplicates


def visualize_duplicates(duplicates):
    G = nx.Graph()

    for child, parent in duplicates:
        G.add_node(child, color='blue', shape='s')
        G.add_node(parent, color='red', shape='s')
        G.add_edge(child, parent)

    plt.figure(figsize=(10, 6), facecolor='black')
    pos = nx.spring_layout(G)
    colors = [G.nodes[node]['color'] for node in G.nodes]

    # Draw nodes with folder icon representation
    nx.draw_networkx_edges(G, pos, edge_color='gray')
    for node in G.nodes:
        x, y = pos[node]
        plt.scatter(x, y, color=G.nodes[node]['color'], s=500, marker='s')
        plt.text(x, y, node, fontsize=8, color='white', ha='right', va='center',
                 bbox=dict(facecolor='black', edgecolor='white', boxstyle='round,pad=0.3'))

    plt.title("Duplicate File Visualization", color='white')
    plt.axis('off')
    plt.show()


if __name__ == "__main__":
    parent_folder = input("Enter the parent folder path: ")
    child_folder = input("Enter the child folder path: ")
    use_hash = input("Use hash comparison? (y/n): ").strip().lower() == 'y'

    duplicates = find_duplicates(parent_folder, child_folder, use_hash)

    if duplicates:
        print("Found duplicate files:")
        for child, parent in duplicates:
            print(f"{child} <--> {parent}")

        perform_hash_check = input("Do you want to perform a hash check on the duplicates? (y/n): ").strip().lower()
        if perform_hash_check == 'y':
            new_duplicates = []
            for child, parent in duplicates:
                child_file_path = os.path.join(child_folder, child)
                parent_file_path = os.path.join(parent_folder, parent)

                # Ensure the file paths are correct for both child and parent directories
                if os.path.exists(child_file_path) and os.path.exists(parent_file_path):
                    child_hash = get_file_hash(child_file_path) if use_hash else None
                    parent_hash = get_file_hash(parent_file_path) if use_hash else None

                    if child_hash and parent_hash and child_hash == parent_hash:
                        print(f"Hash match found: {child} <--> {parent}")
                        new_duplicates.append((child, parent))
                    else:
                        print(f"Hash mismatch or no hash check performed: {child} <--> {parent}")

            if new_duplicates:
                visualize_duplicates(new_duplicates)
            else:
                print("No new hash matches.")
    else:
        print("No duplicates found.")
