
# SmartSort 📂

**SmartSort** is a lightweight Python desktop application that automatically organizes files into categorized folders based on their file extensions.

It was built as a practical Python project with a focus on a responsive user interface, safe file handling, and clear operation logging.

## ✨ Features

* 📁 Select any folder through a graphical interface
* 🗂️ Automatically categorize files by extension
* ⚡ Background processing using Python threads
* 📝 Real-time operation log
* 🛡️ Individual error handling for each file
* 🔄 Prevents duplicate filenames from being overwritten
* 🚫 Prevents repeated operations while sorting is in progress
* 🧪 Built-in test file generator
* 🐍 Uses Python standard libraries only

## 📂 Supported Categories

| Category   | File Types                                       |
| ---------- | ------------------------------------------------ |
| Images     | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`         |
| Videos     | `.mp4`, `.mkv`, `.avi`, `.mov`                   |
| Music      | `.mp3`, `.wav`, `.flac`                          |
| Documents  | `.txt`, `.pdf`, `.docx`, `.doc`, `.xlsx`, `.xls` |
| Archives   | `.zip`, `.rar`, `.7z`                            |
| Installers | `.exe`, `.msi`                                   |
| Others     | Other file types                                 |

## 🛠️ Technologies

* Python 3
* Tkinter
* pathlib
* threading
* shutil

No external Python packages are required.

## 🚀 How to Run

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/SmartSort.git
```

Open the project directory:

```bash
cd SmartSort
```

Run the application:

```bash
python SmartSort.py
```

## 🧪 Testing

SmartSort includes a **Create Test Files** button that generates sample files with different extensions.

This makes it possible to test the sorting functionality without using important personal files.

## 🔐 Safe File Handling

SmartSort does not overwrite existing files.

If a file with the same name already exists in the destination folder, SmartSort automatically creates a unique filename such as:

```text
Photo.jpg
Photo_1.jpg
Photo_2.jpg
```

Errors are also handled individually so that a problem with one file does not stop the entire sorting operation.

## 📌 Project Status

**Version:** 1.0

SmartSort is a learning and portfolio project focused on Python GUI development, file management, threading, and error handling.

## 👨‍💻 Author

**Reza Bagheriyan**
GitHub: @RezaBgh80
