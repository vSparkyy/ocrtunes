import os
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image

root = tk.Tk()
root.withdraw()

def handle_image_change(username, base_dir, size):
    error = None
    user_dir = os.path.join(base_dir, username)
    os.makedirs(user_dir, exist_ok=True)
    file_path = filedialog.askopenfilename(title="Select an image file", 
                                           filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])

    if file_path:
        file_name = os.path.basename(file_path)
        destination_path = os.path.join(user_dir, file_name)

        try:
            with Image.open(file_path) as img:
                width, height = img.size
                if width > size[0] or height > size[1]:
                    error = f"Image dimensions ({width}x{height}) exceed the allowed size of {size}."
                else:
                    shutil.copy(file_path, destination_path)
        except Exception as e:
            error = f"Failed to process the image: {e}"

    return error if error else destination_path