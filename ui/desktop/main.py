import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

from app.scanner import scan_folder
from app.db_manager import create_table, insert_photo, search_photos_by_tag_or_face
from app.face_recognizer import load_known_faces

create_table()
known_encodings, known_names = load_known_faces()

class PhotoFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Photo Finder 📸")
        self.root.geometry("800x600")

        self.search_var = tk.StringVar()

        self.setup_widgets()

    def setup_widgets(self):
        tk.Label(self.root, text="Search Faces/Tags:").pack(pady=5)
        search_entry = tk.Entry(self.root, textvariable=self.search_var, width=50)
        search_entry.pack(pady=5)
        search_entry.bind("<Return>", lambda e: self.search_photos())

        tk.Button(self.root, text="🔍 Search", command=self.search_photos).pack(pady=5)
        tk.Button(self.root, text="📁 Scan New Folder", command=self.scan_new_folder).pack(pady=5)

        self.results_frame = tk.Frame(self.root)
        self.results_frame.pack(fill="both", expand=True)

    def scan_new_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        photos = scan_folder(folder)

        for photo in photos:
            insert_photo(photo)

        messagebox.showinfo("Done", f"Scanned and stored {len(photos)} images!")
        self.search_photos()

    def search_photos(self):
        keyword = self.search_var.get()
        results = search_photos_by_tag_or_face(keyword)

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not results:
            tk.Label(self.results_frame, text="No results found.").pack()
            return

        for photo in results:
            try:
                img = Image.open(photo[1])
                img.thumbnail((100, 100))
                photo_img = ImageTk.PhotoImage(img)

                frame = tk.Frame(self.results_frame, pady=5)
                frame.pack()

                label = tk.Label(frame, image=photo_img, cursor="hand2")
                label.image = photo_img
                label.pack(side="left")

                # Click to open full-size image
                label.bind("<Button-1>", lambda e, path=photo[1]: self.open_full_image(path))

                info = f"{photo[2]}\nFaces: {photo[5]}\nTags: {photo[4]}"
                tk.Label(frame, text=info, justify="left").pack(side="left", padx=10)

            except Exception as e:
                print(f"Error displaying image: {e}")
                continue

    def open_full_image(self, path):
        try:
            top = tk.Toplevel(self.root)
            top.title("Full Image View")

            img = Image.open(path)
            img = img.resize((800, 600))
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(top, image=photo)
            label.image = photo
            label.pack()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image.\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoFinderApp(root)
    root.mainloop()
