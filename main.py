import os
import importlib
from tkinter import filedialog, messagebox


def _import_dependency(module_name, package_name=None):
    """Import an optional dependency while keeping editor diagnostics clean."""
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        package_name = package_name or module_name
        raise RuntimeError(
            f"Missing dependency '{package_name}'. Install it with "
            f"'python -m pip install {package_name}'."
        ) from exc


try:
    ctk = _import_dependency("customtkinter")
    tkinterdnd2 = _import_dependency("tkinterdnd2")
    DND_FILES = tkinterdnd2.DND_FILES
    TkinterDnD = tkinterdnd2.TkinterDnD
    Image = _import_dependency("PIL.Image", "Pillow")
    ImageTk = _import_dependency("PIL.ImageTk", "Pillow")
    ImageConverter = _import_dependency("converter").ImageConverter
except RuntimeError as exc:
    messagebox.showerror("Missing dependency", str(exc))
    raise SystemExit(1) from exc

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class FinalImageConverter:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Converter Pro")
        self.master.geometry("700x500")
        self.master.configure(bg="#1E1E1E")
        self.converter = ImageConverter()
        self.files = []

        # Drag & Drop область
        self.drop_area = ctk.CTkLabel(master, text="Перетащите файлы или папки сюда",
                                      width=650, height=80, fg_color="#2A2A2A", corner_radius=10)
        self.drop_area.pack(pady=10)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.drop_files)

        # Лог конвертации
        self.log = ctk.CTkTextbox(master, width=650, height=200, fg_color="#1C1C1C", text_color="white")
        self.log.pack(pady=10)
        self.log.configure(state="disabled")

        # Формат и кнопки
        self.format_var = ctk.StringVar(value="PNG")
        self.dropdown = ctk.CTkOptionMenu(master, variable=self.format_var,
                                          values=["PNG","JPEG","BMP","GIF"], fg_color="#2A2A2A", button_color="#3A3A3A")
        self.dropdown.pack(pady=5)

        btn_frame = ctk.CTkFrame(master, fg_color="#1C1C1C")
        btn_frame.pack(pady=10)

        # Иконки для кнопок (опционально - можно вставить свои PNG-файлы)
        self.add_icon = None
        self.clear_icon = None
        self.convert_icon = None
        
        try:
            self.add_icon = ImageTk.PhotoImage(Image.open("add.png").resize((24,24)))
        except FileNotFoundError:
            pass
        
        try:
            self.clear_icon = ImageTk.PhotoImage(Image.open("clear.png").resize((24,24)))
        except FileNotFoundError:
            pass
        
        try:
            self.convert_icon = ImageTk.PhotoImage(Image.open("convert.png").resize((24,24)))
        except FileNotFoundError:
            pass

        self.add_btn = ctk.CTkButton(btn_frame, text="Добавить файлы", image=self.add_icon, compound="left",
                                     command=self.add_files)
        self.add_btn.grid(row=0, column=0, padx=5)

        self.clear_btn = ctk.CTkButton(btn_frame, text="Очистить список", image=self.clear_icon, compound="left",
                                       command=self.clear_list)
        self.clear_btn.grid(row=0, column=1, padx=5)

        self.convert_btn = ctk.CTkButton(btn_frame, text="Конвертировать", image=self.convert_icon, compound="left",
                                         command=self.convert_files)
        self.convert_btn.grid(row=0, column=2, padx=5)

        # Прогрессбар
        self.progress = ctk.CTkProgressBar(master, width=650, fg_color="#2A2A2A", progress_color="#3A7FF6")
        self.progress.pack(pady=5)
        self.progress.set(0)

    def log_message(self, msg):
        self.log.configure(state="normal")
        self.log.insert(ctk.END, msg + "\n")
        self.log.see(ctk.END)
        self.log.configure(state="disabled")
        self.master.update()

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Images","*.png *.jpg *.jpeg *.bmp *.gif")])
        for f in files:
            if f not in self.files:
                self.files.append(f)
        self.log_message(f"[INFO] Добавлено {len(files)} файлов")

    def clear_list(self):
        self.files.clear()
        self.log_message("[INFO] Список очищен")

    def drop_files(self, event):
        paths = self.master.tk.splitlist(event.data)
        added = 0
        for path in paths:
            if os.path.isfile(path) or os.path.isdir(path):
                if path not in self.files:
                    self.files.append(path)
                    added += 1
        self.log_message(f"[INFO] Перетащено {added} файлов/папок")

    def convert_files(self):
        if not self.files:
            messagebox.showwarning("Внимание", "Сначала добавьте файлы или папки!")
            return
        output_folder = filedialog.askdirectory(title="Выберите папку для сохранения")
        if not output_folder:
            return

        # Собираем все файлы из папок
        full_list = []
        for f in self.files:
            if os.path.isfile(f):
                full_list.append(f)
            elif os.path.isdir(f):
                for root, dirs, files in os.walk(f):
                    for file in files:
                        if file.lower().endswith((".png",".jpg",".jpeg",".bmp",".gif")):
                            full_list.append(os.path.join(root, file))

        total_files = len(full_list)
        if total_files == 0:
            messagebox.showwarning("Внимание", "Нет файлов для конвертации")
            return

        self.progress.set(0)
        for i, file in enumerate(full_list):
            try:
                img = Image.open(file)
                output_ext = self.format_var.get().lower()
                name, _ = os.path.splitext(os.path.basename(file))
                output_path = os.path.join(output_folder, f"{name}.{output_ext}")

                if self.format_var.get().upper() == "JPEG" and img.mode == "RGBA":
                    img = img.convert("RGB")
                img.save(output_path, self.format_var.get())
                self.log_message(f"[OK] {file} → {output_path}")
            except Exception as e:
                self.log_message(f"[ERROR] {file}: {e}")
            self.progress.set((i+1)/total_files)

        self.log_message("[INFO] Конвертация завершена")
        messagebox.showinfo("Готово", "Конвертация завершена!")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FinalImageConverter(root)
    root.mainloop()