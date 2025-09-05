# UI2Py – PySide6 Edition

[![PySide6](https://img.shields.io/badge/PySide6-6.7.3-blue?logo=qt)](https://www.pyside.org/docs/pyside6/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A simple yet powerful GUI tool to convert one or **multiple** Qt Designer `.ui` files into Python code using **PySide6**.

![Main Window - Empty](images/main_empty.png)

## ✨ Features

- **Batch Conversion:** Convert multiple `.ui` files to `.py` files at once.
- **Drag & Drop Support:** Simply drag your `.ui` files onto the application window.
- **Automatic Naming:** Output files are intelligently named `ui_<filename>.py`.
- **Customizable Output:** For single files, you can easily edit the output name.
- **Dark/Light Theme:** The application automatically adapts to your system's theme.
- **Real-time Status Updates:** Clear feedback during the conversion process.
- **Cross-Platform:** Works on Windows, macOS, and Linux.

## ⚡ Quick Setup

This project depends only on `PySide6`.

1. **Create and activate a virtual environment:**
   ```bash
   # Create
   python -m venv .venv
   # Activate (Windows)
   .venv\Scripts\activate
   # Activate (macOS/Linux)
   source .venv/bin/activate
   ```

2. **Install the dependency:**
   ```bash
   pip install PySide6
   ```

3. **Run the app:**
   ```bash
   python ui2py.py
   ```

## ▶️ Usage

1.  **Select File(s)** — Click *Select File* or drag & drop one or more `.ui` files into the window.
2.  **(Optional)** Select a destination folder. By default, it's the same folder as the input file(s).
3.  **(Optional, single file only)** Edit the output name.
4.  Click **Convert**. Status updates will appear at the bottom.

> 💡 *Tip:* When converting multiple files, each one is automatically named as `ui_<filename>.py`.

## 🖼 Screenshots

### After file selection (Prefix/Base/Suffix visible)
![File Selected](images/file_selected.png)

### Drag & drop success status message
![Drag & Drop Success](images/drag_drop_success.png)

### Editing the output name (focus underline)
![Editing Output Name](images/edit_name.png)

### Conversion completed message
![Conversion Completed](images/conversion_done.png)

### After conversion (file created in selected folder)
![After Conversion - File in Folder](images/after_conversion.png)

### After dropping multiple files
![Multi File Drop](images/multi_files.png)

### After conversion multiple files (file created in selected folder)
![After Conversion - File in Folder](images/after_multiple_conversion.png)

## 📝 Changelog
- **v1.4.1:** Added the ability to remove selected files from the multi-file list.
- **v1.4:** Added automatic dark/light theme support that adapts to the system in real time.
- **v1.3:** Introduced multi-file batch conversion and a dynamic UI that resizes to show a file list.
- **v1.2:** Implemented drag-and-drop support and a smarter, segmented output path editor.
- **v1.1:** Added better error handling and fixed taskbar visibility.
- **v1.0:** Initial release with basic single-file conversion.

## 🆘 Troubleshooting

- **`pyside6-uic not found on PATH`** Make sure PySide6 tools are installed and your terminal can run `pyside6-uic`.

- **No permission to write file** Choose a folder where you have write permissions (e.g., your home or desktop folder).

- **Wrong file type** Only `.ui` files are supported.

- **Mixed file types dropped** Only `.ui` files will be processed. Other file types will be ignored.

- **Duplicate output names** Output names are auto-generated as `ui_<filename>.py`. Ensure all input filenames are unique to avoid overwriting.

## 📄 License

[MIT © 2025 umitkrkmz](LICENSE)