# fileToolsJason

This is a repository of custom-made Python scripts made to find duplicate files in specified directories.

__visualDuplicatesFinder.py__:
- A graphical interface that scans one or two directories for duplicates using open source software [difPy](https://github.com/elisemercury/Duplicate-Image-Finder). difPy uses OpenCV to detect duplicates—even when the resolution is different or the image is rotated.
- This program allows the user to mark individual files for deletion. For example, if duplicates were found at `C:\image.jpg` and `C:\somefolder\image.jpg`, the user could delete either image, or both right in the graphical user interface.

![visualDuplicatesFinder Homescreen.jpg](img/visualDuplicatesFinder%20Homescreen.jpg)

__renameGUIDsNotion__:

Assists in porting pages from Notion to file systems by removing GUIDs and fixing file paths in markdown (.md) files. This program has been tested as working on Windows 11.

- Removes GUIDs from file and folder names while keeping them paired in case of name collisions
- Adjusts contents of markdown files to remove all GUIDs from paths for media and hyperlinks.
- Pages are easily navigable __and modifiable__ in VSCode by enabling page preview. Exporting as HTML or PDF can make it more difficult to modify Notion pages after they have been exported.