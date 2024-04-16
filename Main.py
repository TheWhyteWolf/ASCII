import tkinter as tk
import os
from tkinter import filedialog
from ascii_magic import AsciiArt
from PIL import ImageEnhance

DEFAULT_COLUMNS = 80
MAX_COLUMNS = 800

window = tk.Tk()

# Initialize variables
selected_files = []
columns = tk.IntVar()
monochrome = tk.BooleanVar()
brightness = tk.DoubleVar(value=1.0)  # Default brightness is 1.0
IEBright = ImageEnhance.Brightness

# Constants
YesNo = ["Yes", "No"]
BitDepth = ["16-bit", "8-bit"]

def create_widgets():
    tk.Label(window, text="IMS + ASCII MAGIC converter").pack()
    create_input_widgets()
    create_options_widgets()
    create_listbox_and_scrollbar()
    create_buttons()

def create_input_widgets():
    tk.Label(window, text="Enter the number of columns (50-800): default = {}".format(DEFAULT_COLUMNS)).pack()
    tk.Entry(window, textvariable=columns, validate="key", validatecommand=(window.register(validate_input), '%P')).pack()
    tk.Label(window, text="Brightness 0 to 5: Default is 1").pack()
    tk.Entry(window, textvariable=brightness, validate="key", validatecommand=(window.register(validate_brightness_input), '%P')).pack()

def create_options_widgets():
    tk.Label(window, text="Monochrome:").pack()
    tk.OptionMenu(window, monochrome, *YesNo).pack()
    tk.Label(window, text="Color Depth:").pack()
    colour_var = tk.StringVar(value="8-bit")
    tk.OptionMenu(window, colour_var, *BitDepth).pack()

def create_listbox_and_scrollbar():
    selected_files_label = tk.Label(window, text="Selected File(s)")
    selected_files_label.pack()
    list_frame = tk.Frame(window)
    list_frame.pack(fill=tk.BOTH, expand=True)
    global selected_files_listbox
    selected_files_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=len(selected_files))
    selected_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    selected_files_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=selected_files_listbox.yview)
    selected_files_listbox.bind('<MouseWheel>', lambda event: selected_files_listbox.yview_scroll(int(-1*(event.delta/120)), "units"))

def create_buttons():
    tk.Button(window, text="Select File(s)", command=callback).pack()
    tk.Button(window, text="Generate ASCII Art", command=generate_ascii).pack()
    tk.Button(window, text="Close Window", command=close_window).pack()

def callback():
    files = filedialog.askopenfilenames(filetypes=(("Image Files", (".png", ".jpg", ".tif", ".tiff", ".jpeg", ".bmp", ".gif")),))
    selected_files.clear()  
    selected_files.extend(files)
    update_selected_files_listbox()

def close_window():
    window.destroy()

def validate_input(new_value):
    if new_value == "":
        return True
    if new_value.isdigit():
        value = int(new_value)
        if 50 <= value <= MAX_COLUMNS:
            return True
    return False

def validate_brightness_input(new_value):
    if new_value == "":
        return True
    try:
        value = float(new_value)
        if 0 <= value <= 5:
            return True
    except ValueError:
        pass
    return False

def generate_ascii():
    if selected_files:
        for file_path in selected_files:
            my_art = AsciiArt.from_image(file_path)
            my_art.image = IEBright(my_art.image).enhance(brightness.get())
            file_name_without_extension = os.path.splitext(file_path)[0]
            my_art.to_html_file(
                file_name_without_extension + ".html",
                monochrome=monochrome.get(),  
                columns=columns.get() or DEFAULT_COLUMNS
            )
            print("ASCII art generated and saved as", file_name_without_extension + ".html")
    else:
        print("Please select a file before generating ASCII art.")

def update_selected_files_listbox():
    selected_files_listbox.delete(0, tk.END)
    num_files = len(selected_files)
    for i in range(min(num_files, MAX_HEIGHT)):
        selected_files_listbox.insert(tk.END, selected_files[i])

# Main
if __name__ == "__main__":
    MAX_HEIGHT = 10
    create_widgets()
    window.mainloop()
