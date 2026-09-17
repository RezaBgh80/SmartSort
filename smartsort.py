"""
SmartSort - نرم‌افزار مرتب‌سازی خودکار فایل‌ها
نسخه بازنویسی‌شده با رفع ایرادها:
  1) باگ shadow شدن متغیر name (تداخل نام دسته‌بندی با نام فایل)
  2) فریز شدن رابط کاربری هنگام جابه‌جایی حجم زیاد فایل -> اجرا در Thread جدا
  3) امکان اجرای مجدد و کلیک‌های تکراری روی دکمه‌ها هنگام پردازش -> غیرفعال‌سازی موقت دکمه‌ها
  4) عدم نمایش جزئیات عملیات -> افزودن پنل لاگ
  5) استفاده از pathlib به‌جای رشته‌های خام برای مسیرها (پایدارتر و خواناتر)
  6) مدیریت خطا برای هر فایل به‌صورت جداگانه تا یک خطا کل عملیات را متوقف نکند
"""

import os
import shutil
import threading
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox

# -------------------------------------------------
# دسته‌بندی فایل‌ها بر اساس پسوند
# -------------------------------------------------
FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Music": [".mp3", ".wav", ".flac"],
    "Documents": [".txt", ".pdf", ".docx", ".doc", ".xlsx", ".xls"],
    "Archives": [".zip", ".rar", ".7z"],
    "Installers": [".exe", ".msi"],
}

# پوشه‌هایی که خودشان محصول این برنامه هستند؛ برای جلوگیری از مرتب‌سازی مجدد آن‌ها
CATEGORY_NAMES = set(FILE_TYPES.keys()) | {"Others"}


def get_category(extension: str) -> str:
    """نام دسته‌بندی متناظر با یک پسوند فایل را برمی‌گرداند."""
    extension = extension.lower()
    for category, extensions in FILE_TYPES.items():
        if extension in extensions:
            return category
    return "Others"


def unique_destination(folder: Path, filename: str) -> Path:
    """
    اگر فایلی با همین نام از قبل در مقصد وجود داشته باشد،
    یک نام جدید و یکتا (مثل file_1.txt) تولید می‌کند.
    """
    destination = folder / filename
    if not destination.exists():
        return destination

    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while True:
        candidate = folder / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


class SmartSortApp:
    def __init__(self, window: tk.Tk):
        self.window = window
        self.selected_folder: Path | None = None
        self.is_running = False

        self._build_ui()

    # -------------------------------------------------
    # ساخت رابط کاربری
    # -------------------------------------------------
    def _build_ui(self):
        w = self.window
        w.title("SmartSort")
        w.geometry("700x560")
        w.configure(bg="#181818")
        w.resizable(False, False)

        title = tk.Label(
            w, text="SmartSort", font=("Segoe UI", 30, "bold"),
            fg="white", bg="#181818"
        )
        title.pack(pady=(30, 5))

        subtitle = tk.Label(
            w, text="Organize your files automatically",
            font=("Segoe UI", 11), fg="#999999", bg="#181818"
        )
        subtitle.pack(pady=(0, 20))

        card = tk.Frame(w, bg="#242424")
        card.pack(padx=50, fill="x")

        folder_title = tk.Label(
            card, text="Selected Folder", font=("Segoe UI", 11, "bold"),
            fg="white", bg="#242424"
        )
        folder_title.pack(anchor="w", padx=25, pady=(25, 5))

        self.folder_label = tk.Label(
            card, text="No folder selected", font=("Segoe UI", 10),
            fg="#777777", bg="#242424", anchor="w"
        )
        self.folder_label.pack(fill="x", padx=25)

        self.choose_button = tk.Button(
            card, text="📁  Choose Folder", command=self.choose_folder,
            font=("Segoe UI", 11, "bold"), fg="white", bg="#0078D4",
            activebackground="#106EBE", activeforeground="white",
            relief="flat", cursor="hand2", padx=25, pady=12
        )
        self.choose_button.pack(pady=20)

        self.test_button = tk.Button(
            w, text="Create Test Files", command=self.create_test_files,
            font=("Segoe UI", 10), fg="white", bg="#333333",
            activebackground="#444444", relief="flat", cursor="hand2",
            padx=20, pady=10
        )
        self.test_button.pack(pady=(15, 10))

        self.organize_button = tk.Button(
            w, text="✨  Organize Files", command=self.start_organize,
            font=("Segoe UI", 12, "bold"), fg="white", bg="#107C10",
            activebackground="#0E6B0E", relief="flat", cursor="hand2",
            padx=35, pady=12
        )
        self.organize_button.pack()

        self.status_label = tk.Label(
            w, text="Select a folder to begin", font=("Segoe UI", 10),
            fg="#888888", bg="#181818"
        )
        self.status_label.pack(pady=15)

        # پنل لاگ برای نمایش جزئیات عملیات
        log_frame = tk.Frame(w, bg="#181818")
        log_frame.pack(padx=50, fill="both", expand=True)

        self.log_box = tk.Text(
            log_frame, height=8, bg="#101010", fg="#cccccc",
            font=("Consolas", 9), relief="flat", state="disabled"
        )
        self.log_box.pack(fill="both", expand=True)

    # -------------------------------------------------
    # کمک‌کننده‌ها برای بروزرسانی ایمن رابط کاربری از داخل Thread
    # -------------------------------------------------
    def _set_status(self, text: str, color: str = "#4CAF50"):
        self.window.after(0, lambda: self.status_label.config(text=text, fg=color))

    def _log(self, text: str):
        def append():
            self.log_box.config(state="normal")
            self.log_box.insert("end", text + "\n")
            self.log_box.see("end")
            self.log_box.config(state="disabled")
        self.window.after(0, append)

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    def _set_buttons_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.choose_button.config(state=state)
        self.test_button.config(state=state)
        self.organize_button.config(state=state)

    # -------------------------------------------------
    # انتخاب پوشه
    # -------------------------------------------------
    def choose_folder(self):
        folder = filedialog.askdirectory(parent=self.window, title="Select folder")
        if folder:
            self.selected_folder = Path(folder)
            self.folder_label.config(text=folder, fg="white")
            self.status_label.config(text="Folder selected ✓", fg="#4CAF50")

    # -------------------------------------------------
    # ساخت فایل‌های تست
    # -------------------------------------------------
    def create_test_files(self):
        if not self.selected_folder:
            messagebox.showwarning("SmartSort", "First choose a folder!")
            return

        files = [
            "Photo.jpg", "Picture.png", "Movie.mp4", "Film.mkv",
            "Song.mp3", "Music.wav", "Document.txt", "Book.pdf",
            "Backup.zip", "Program.exe",
        ]

        created = 0
        for filename in files:
            path = self.selected_folder / filename
            if not path.exists():
                path.write_bytes(b"SmartSort Test File")
                created += 1

        self.status_label.config(text=f"{created} test files created ✓", fg="#4CAF50")

    # -------------------------------------------------
    # مرتب‌سازی فایل‌ها (اجرا در Thread جدا تا UI فریز نشود)
    # -------------------------------------------------
    def start_organize(self):
        if not self.selected_folder:
            messagebox.showwarning("SmartSort", "First choose a folder!")
            return

        if self.is_running:
            return

        self.is_running = True
        self._set_buttons_enabled(False)
        self._clear_log()
        self._set_status("Organizing...", "#0078D4")

        thread = threading.Thread(target=self._organize_worker, daemon=True)
        thread.start()

    def _organize_worker(self):
        folder = self.selected_folder
        moved = 0
        skipped = 0

        try:
            entries = sorted(folder.iterdir())
        except Exception as error:
            self._log(f"خطا در خواندن پوشه: {error}")
            self._finish_organize(0)
            return

        for entry in entries:
            # فقط فایل‌های سطح بالای پوشه، نه زیرپوشه‌ها یا پوشه‌های دسته‌بندی‌شده قبلی
            if not entry.is_file():
                continue

            category = get_category(entry.suffix)
            category_folder = folder / category

            try:
                category_folder.mkdir(exist_ok=True)
                destination = unique_destination(category_folder, entry.name)
                shutil.move(str(entry), str(destination))
                moved += 1
                self._log(f"✓ {entry.name}  →  {category}/{destination.name}")
            except Exception as error:
                skipped += 1
                self._log(f"✗ {entry.name}  خطا: {error}")

        self._finish_organize(moved, skipped)

    def _finish_organize(self, moved: int, skipped: int = 0):
        summary = f"{moved} files organized ✓"
        if skipped:
            summary += f"  ({skipped} failed)"

        self._set_status(summary, "#4CAF50" if skipped == 0 else "#E5A000")

        def done():
            self.is_running = False
            self._set_buttons_enabled(True)
            messagebox.showinfo(
                "SmartSort",
                f"Done!\n\n{moved} files organized." + (f"\n{skipped} failed." if skipped else "")
            )

        self.window.after(0, done)


if __name__ == "__main__":
    window = tk.Tk()
    app = SmartSortApp(window)
    window.mainloop()
