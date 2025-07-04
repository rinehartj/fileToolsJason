import os
import threading
from PIL import Image, ExifTags, ImageTk
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
from send2trash import send2trash
import cv2
import difPy

USE_DATE_TAKEN = True
USE_FILE_SIZE = True

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv"}


def get_date_taken(path):
    try:
        ext = os.path.splitext(path)[1].lower()
        if ext in {".jpg", ".jpeg", ".png", ".tiff"}:
            img = Image.open(path)
            exif = img._getexif()
            if not exif:
                return None
            for tag, value in exif.items():
                if ExifTags.TAGS.get(tag) == "DateTimeOriginal":
                    return value
        else:
            # Use last modified time as fallback
            return str(os.path.getmtime(path))
    except Exception:
        return None


def get_media_files(folder):
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv"}

    files = []
    for root, _, filenames in os.walk(folder):
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in image_exts or ext in video_exts:
                files.append(os.path.join(root, fname))
    return files


def get_file_info(path):
    size = os.path.getsize(path)
    ext = os.path.splitext(path)[1].lower()

    if ext in VIDEO_EXTS:
        return (size,)  # Only use file size for video
    elif ext in IMAGE_EXTS:
        date_taken = get_date_taken(path) if USE_DATE_TAKEN else None
        return (size, date_taken)
    else:
        return (size,)  # Fallback for unknown types


class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Duplicate Finder")
        self.setup_gui()

    def setup_gui(self):
        self.root.geometry("1100x700")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        # Top controls
        top = tk.Frame(self.root)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        tk.Button(top, text="Select Folder1", command=self.select_folder1).grid(row=0, column=0)
        tk.Button(top, text="Select Folder2", command=self.select_folder2).grid(row=0, column=1)
        self.folder1_label = tk.Label(top, text="Folder1: Not selected")
        self.folder1_label.grid(row=1, column=0, columnspan=2, sticky="w")
        self.folder2_label = tk.Label(top, text="Folder2: Not selected")
        self.folder2_label.grid(row=2, column=0, columnspan=2, sticky="w")
        self.batch_button = tk.Button(top, text="Run Batch Mode", command=self.batch_mode)
        self.batch_button.grid(row=0, column=2)

        self.search_mode = tk.StringVar(value="two_folders")
        mode_frame = tk.Frame(top)
        mode_frame.grid(row=0, column=3, padx=10)
        tk.Radiobutton(mode_frame, text="Compare two folders", variable=self.search_mode, value="two_folders").pack(
            anchor="w")
        tk.Radiobutton(mode_frame, text="Find duplicates in one folder", variable=self.search_mode,
                       value="single_folder").pack(anchor="w")

        # Preview
        self.preview_frame = tk.Frame(self.root)
        self.preview_frame.grid(row=1, column=0, sticky="ew")
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.columnconfigure(1, weight=1)

        self.img1_label = tk.Label(self.preview_frame)
        self.img2_label = tk.Label(self.preview_frame)
        self.img1_label.grid(row=0, column=0)
        self.img2_label.grid(row=0, column=1)

        # Treeview with checkboxes
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.grid(row=2, column=0, sticky="nsew")

        self.tree = ttk.Treeview(self.tree_frame, columns=("file1", "file2", "date", "size", "del1", "del2"),
                                 show="headings")
        for col in ["file1", "file2", "date", "size", "del1", "del2"]:
            self.tree.heading(col, text=col)
        self.tree.column("del1", width=100, anchor="center")
        self.tree.column("del2", width=100, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.update_preview)

        # Select All Checkboxes - replaced with buttons
        bottom = tk.Frame(self.root)
        bottom.grid(row=3, column=0, sticky="ew")

        tk.Button(bottom, text="Select All Folder1", command=self.select_all_folder1).pack(side=tk.LEFT)
        tk.Button(bottom, text="Select All Folder2", command=self.select_all_folder2).pack(side=tk.LEFT)
        tk.Button(bottom, text="Deselect All Folder1", command=self.deselect_all_folder1).pack(side=tk.LEFT)
        tk.Button(bottom, text="Deselect All Folder2", command=self.deselect_all_folder2).pack(side=tk.LEFT)

        tk.Button(bottom, text="Apply Deletions", command=self.apply_deletions).pack(side=tk.RIGHT)

        self.folder1 = None
        self.folder2 = None
        self.duplicates = []
        self.delete_flags = {}

    def select_folder1(self):
        self.folder1 = filedialog.askdirectory()
        self.folder1_label.config(text=f"Folder1: {self.folder1}")

    def select_folder2(self):
        self.folder2 = filedialog.askdirectory()
        self.folder2_label.config(text=f"Folder2: {self.folder2}")

    def select_all_folder1(self):
        for iid in self.delete_flags:
            self.delete_flags[iid][0] = True
            self.refresh_tree_item(iid)

    def select_all_folder2(self):
        for iid in self.delete_flags:
            self.delete_flags[iid][1] = True
            self.refresh_tree_item(iid)

    def deselect_all_folder1(self):
        for iid in self.delete_flags:
            self.delete_flags[iid][0] = False
            self.refresh_tree_item(iid)

    def deselect_all_folder2(self):
        for iid in self.delete_flags:
            self.delete_flags[iid][1] = False
            self.refresh_tree_item(iid)

    def batch_mode(self):
        if self.search_mode.get() == "two_folders":
            if not self.folder1 or not self.folder2:
                messagebox.showwarning("Folders missing", "Please select both folders first.")
                return
        else:  # single folder mode
            if not self.folder1:
                messagebox.showwarning("Folder missing", "Please select a folder first.")
                return

        threading.Thread(target=self.find_duplicates).start()

    def find_duplicates(self):
        self.tree.delete(*self.tree.get_children())
        self.duplicates.clear()
        self.delete_flags.clear()

        if self.search_mode.get() == "single_folder":
            # Single folder mode - find duplicates within one folder
            dif = difPy.build(self.folder1)
        else:
            # Two folder mode - compare between folders
            dif = difPy.build([self.folder1, self.folder2])

        search = difPy.search(dif)
        image_duplicates = search.result

        # Process duplicates (same as before but without the folder comparison logic)
        seen_pairs = set()
        for img1, matches in image_duplicates.items():
            for match in matches:
                img2 = match[0]

                # Skip if the files are actually the same file
                try:
                    if os.path.samefile(img1, img2):
                        continue
                except:
                    pass

                pair_key = tuple(sorted((os.path.abspath(img1), os.path.abspath(img2))))
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)

                    # Get file info for both files
                    size1 = os.path.getsize(img1)
                    size2 = os.path.getsize(img2)
                    date1 = get_date_taken(img1)
                    date2 = get_date_taken(img2)

                    # Format size and date for display
                    size_str = f"{size1} bytes"
                    if size1 != size2:
                        size_str = f"{size1} vs {size2} bytes (DIFFERENT)"

                    date_str = str(date1) if date1 else "N/A"
                    if date1 != date2:
                        date_str = f"{date1} vs {date2} (DIFFERENT)"

                    self.duplicates.append((img1, img2, date_str, size_str))
                    iid = f"{img1}|{img2}"
                    self.tree.insert("", tk.END, iid=iid, values=(img1, img2, date_str, size_str, "", ""))
                    self.delete_flags[iid] = [False, False]

        # Video duplicate detection remains the same but needs to handle single folder mode
        if self.search_mode.get() == "single_folder":
            files = get_media_files(self.folder1)
            info_map = {}
            for path in files:
                ext = os.path.splitext(path)[1].lower()
                if ext in VIDEO_EXTS:
                    info = get_file_info(path)
                    info_map.setdefault(info, []).append(path)

            for info, paths in info_map.items():
                if len(paths) > 1:  # Only show groups with duplicates
                    for i in range(len(paths)):
                        for j in range(i + 1, len(paths)):
                            f1 = paths[i]
                            f2 = paths[j]
                            pair_key = tuple(sorted((os.path.abspath(f1), os.path.abspath(f2))))
                            if pair_key not in seen_pairs:
                                seen_pairs.add(pair_key)
                                date = info[1] if len(info) > 1 else ""
                                size = info[0]
                                self.duplicates.append((f1, f2, date, f"{size} bytes"))
                                iid = f"{f1}|{f2}"
                                self.tree.insert("", tk.END, iid=iid, values=(f1, f2, date, f"{size} bytes", "", ""))
                                self.delete_flags[iid] = [False, False]
        else:
            # Original two-folder video comparison logic
            files1 = get_media_files(self.folder1)
            files2 = get_media_files(self.folder2)
            info_map2 = {}
            for path in files2:
                ext = os.path.splitext(path)[1].lower()
                if ext in VIDEO_EXTS:
                    info = get_file_info(path)
                    info_map2.setdefault(info, []).append(path)

            for f1 in files1:
                ext = os.path.splitext(f1)[1].lower()
                if ext in VIDEO_EXTS:
                    info = get_file_info(f1)
                    if info in info_map2:
                        for f2 in info_map2[info]:
                            try:
                                if os.path.samefile(f1, f2):
                                    continue
                            except Exception:
                                pass

                            pair_key = tuple(sorted((os.path.abspath(f1), os.path.abspath(f2))))
                            if pair_key not in seen_pairs:
                                seen_pairs.add(pair_key)
                                date = info[1] if len(info) > 1 else ""
                                size = info[0]
                                self.duplicates.append((f1, f2, date, f"{size} bytes"))
                                iid = f"{f1}|{f2}"
                                self.tree.insert("", tk.END, iid=iid, values=(f1, f2, date, f"{size} bytes", "", ""))
                                self.delete_flags[iid] = [False, False]

        self.tree.bind("<ButtonRelease-1>", self.on_checkbox_click)

        if not self.duplicates:
            messagebox.showinfo("No duplicates", "No duplicate files were found.")
            return

        self.tree.bind("<ButtonRelease-1>", self.on_checkbox_click)

    def on_checkbox_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return

        col = self.tree.identify_column(event.x)
        if col == "#5":  # del1
            self.delete_flags[item][0] = not self.delete_flags[item][0]
        elif col == "#6":  # del2
            self.delete_flags[item][1] = not self.delete_flags[item][1]

        self.refresh_tree_item(item)

    def toggle_all1(self):
        for iid in self.delete_flags:
            self.delete_flags[iid][0] = bool(self.select_all1.get())
            self.refresh_tree_item(iid)

    def toggle_all2(self):
        for iid in self.delete_flags:
            self.delete_flags[iid][1] = bool(self.select_all2.get())
            self.refresh_tree_item(iid)

    def refresh_tree_item(self, iid):
        f1, f2, date, size = iid.split("|")[0], iid.split("|")[1], "", ""
        for tup in self.duplicates:
            if tup[0] == f1 and tup[1] == f2:
                date, size = tup[2], tup[3]
                break
        d1, d2 = ("🗑️" if self.delete_flags[iid][0] else ""), ("🗑️" if self.delete_flags[iid][1] else "")

        self.tree.item(iid, values=(f1, f2, date, size, d1, d2))

    def apply_deletions(self):
        deleted_count = 0
        items_to_remove = []

        for iid, (del1, del2) in self.delete_flags.items():
            f1, f2 = iid.split("|")
            f1 = os.path.normpath(f1)
            f2 = os.path.normpath(f2)

            if del1 and os.path.exists(f1):
                try:
                    send2trash(f1)
                    deleted_count += 1
                    # Mark this item for removal if either file was deleted
                    items_to_remove.append(iid)
                except Exception as e:
                    print(f"Error deleting {f1}: {e}")
            if del2 and os.path.exists(f2):
                try:
                    send2trash(f2)
                    deleted_count += 1
                    # Mark this item for removal if either file was deleted
                    items_to_remove.append(iid)
                except Exception as e:
                    print(f"Error deleting {f2}: {e}")

        # Remove the rows for deleted items
        for iid in set(items_to_remove):  # Use set to avoid duplicates
            if iid in self.delete_flags:
                del self.delete_flags[iid]
            self.tree.delete(iid)

            # Also remove from duplicates list
            self.duplicates = [dup for dup in self.duplicates
                               if not (dup[0] == iid.split("|")[0] and dup[1] == iid.split("|")[1])]

        messagebox.showinfo("Done", f"{deleted_count} files were moved to the Recycle Bin.")

    def update_preview(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        iid = selected[0]
        f1, f2 = self.tree.item(iid)["values"][:2]
        self.show_preview(f1, f2)

    def show_preview(self, file1, file2):
        img1 = self.load_preview(file1)
        img2 = self.load_preview(file2)
        self.img1_label.configure(image=img1)
        self.img1_label.image = img1
        self.img2_label.configure(image=img2)
        self.img2_label.image = img2

    def load_preview(self, path):
        try:
            ext = os.path.splitext(path)[1].lower()
            if ext in {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}:
                img = Image.open(path)
                img.thumbnail((250, 250))
                return ImageTk.PhotoImage(img)
            elif ext in {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv"}:
                cap = cv2.VideoCapture(path)
                success, frame = cap.read()
                cap.release()
                if success:
                    # Convert BGR to RGB and then to PIL
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    img.thumbnail((250, 250))
                    return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Preview load error: {e}")
            return None


if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()