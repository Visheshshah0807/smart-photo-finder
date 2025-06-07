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
        # Method 1: Use askdirectory with better error handling
        folder = filedialog.askdirectory(
            title="Select Photo Folder",
            mustexist=True
        )
        
        if not folder:
            return

        # Debug: Print folder path and check if it exists
        print(f"Selected folder: {folder}")
        print(f"Folder exists: {os.path.exists(folder)}")
        print(f"Folder is directory: {os.path.isdir(folder)}")

        # Check if folder is accessible and contains files
        try:
            files_in_folder = os.listdir(folder)
            print(f"Files in folder: {len(files_in_folder)}")
            
            # Check for image files specifically
            image_files = [f for f in files_in_folder if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'))]
            print(f"Image files found: {len(image_files)}")
            
            if len(image_files) == 0:
                # Check subdirectories
                subdirs = [d for d in files_in_folder if os.path.isdir(os.path.join(folder, d))]
                print(f"Subdirectories: {subdirs}")
                
                if subdirs:
                    messagebox.showinfo("Info", f"No images found in root folder, but found {len(subdirs)} subdirectories. Scanning will include subdirectories.")
                else:
                    messagebox.showwarning("Warning", "No image files found in the selected folder.")
                    return
            
        except PermissionError:
            messagebox.showerror("Error", "Permission denied. Cannot access the selected folder.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Error accessing folder: {e}")
            return

        # Show progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Scanning...")
        progress_window.geometry("300x100")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = tk.Label(progress_window, text="Scanning photos, please wait...")
        progress_label.pack(pady=20)
        
        # Update the UI
        self.root.update()

        try:
            photos = scan_folder(folder)
            progress_window.destroy()

            if not photos:
                messagebox.showwarning("Warning", "No photos were processed. Check if the folder contains valid image files.")
                return

            # Insert photos into database
            for photo in photos:
                insert_photo(photo)

            messagebox.showinfo("Done", f"Scanned and stored {len(photos)} images!")
            self.search_photos()
            
        except Exception as e:
            progress_window.destroy()
            messagebox.showerror("Error", f"Error during scanning: {e}")

    def search_photos(self):
        keyword = self.search_var.get()
        results = search_photos_by_tag_or_face(keyword)

        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not results:
            tk.Label(self.results_frame, text="No results found.").pack()
            return

        # Create scrollable frame for results
        canvas = tk.Canvas(self.results_frame)
        scrollbar = tk.Scrollbar(self.results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for photo in results:
            try:
                # Check if file still exists
                if not os.path.exists(photo[1]):
                    print(f"File not found: {photo[1]}")
                    continue

                img = Image.open(photo[1])
                img.thumbnail((100, 100))
                photo_img = ImageTk.PhotoImage(img)

                frame = tk.Frame(scrollable_frame, pady=5, relief="ridge", bd=1)
                frame.pack(fill="x", padx=5, pady=2)

                label = tk.Label(frame, image=photo_img, cursor="hand2")
                label.image = photo_img  # Keep a reference
                label.pack(side="left")

                # Click to open full-size image
                label.bind("<Button-1>", lambda e, path=photo[1]: self.open_full_image(path))

                info = f"File: {photo[2]}\nFaces: {photo[5] if photo[5] else 'None'}\nTags: {photo[4] if photo[4] else 'None'}"
                tk.Label(frame, text=info, justify="left", wraplength=500).pack(side="left", padx=10)

            except Exception as e:
                print(f"Error displaying image {photo[1]}: {e}")
                continue

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def open_full_image(self, path):
        try:
            if not os.path.exists(path):
                messagebox.showerror("Error", "Image file not found.")
                return

            top = tk.Toplevel(self.root)
            top.title(f"Full Image View - {os.path.basename(path)}")

            img = Image.open(path)
            
            # Resize image to fit screen while maintaining aspect ratio
            screen_width = top.winfo_screenwidth()
            screen_height = top.winfo_screenheight()
            max_width = int(screen_width * 0.8)
            max_height = int(screen_height * 0.8)
            
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(top, image=photo)
            label.image = photo  # Keep a reference
            label.pack()
            
            # Center the window
            top.geometry(f"{img.width}x{img.height}")
            top.update_idletasks()
            x = (screen_width - img.width) // 2
            y = (screen_height - img.height) // 2
            top.geometry(f"{img.width}x{img.height}+{x}+{y}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image.\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoFinderApp(root)
    root.mainloop()