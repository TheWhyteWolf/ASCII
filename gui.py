import tkinter as tk
from tkinter import filedialog
from ascii_magic import AsciiArt

window = tk.Tk()
selected_files = []
columns = tk.IntVar()
monochrome = tk.BooleanVar()
full_color = tk.BooleanVar()

greeting = tk.Label(text="IMS + ASCII MAGIC converter")
greeting.pack()

# Create the Yes or No Options for Monochrome
YesNo = ["Yes", "No"]

# Create the 16/8-bit label for colour
BitDepth = ["16-bit", "8-bit"]

def callback():
    files = filedialog.askopenfilenames(filetypes=(("Image Files", (".png", ".jpg", ".tiff", ".jpeg", ".bmp", ".gif")),))
    selected_files.clear()  # Clear the previous list of selected files
    selected_files.extend(files) # Store the file paths in the selected_files list
    update_selected_files_listbox()

def close_window():
    window.destroy()

def validate_input(new_value):
    if new_value == "":
        return True  # Allow empty input
    if new_value.isdigit():
        value = int(new_value)
        if 50 <= value <= 300:
            return True
    return False


# Column entry Box
input_label = tk.Label(text="Enter the number of columns (50-300): default = 80")
input_label.pack()
input_entry = tk.Entry(window, textvariable=columns, validate="key", validatecommand=(window.register(validate_input), '%P'))
input_entry.pack()

# Monochrome yay or nay
monochrome_label = tk.Label(text="Monochrome:")
monochrome_label.pack()
monochrome_menu = tk.OptionMenu(window, monochrome, *YesNo)
monochrome_menu.pack()

# 16-bit or 8-bit colour
full_colour_label = tk.Label(text="16 Bit Colour")
full_colour_label.pack()
full_colour_menu = tk.OptionMenu(window, full_color, *BitDepth)

# Function to update the state of the full colour menu based on the monochrome option
def update_colour_menu_state(*args):
    if monochrome.get():
        full_colour_menu.config(state="disabled")
    else:
        full_colour_menu.config(state="normal")

monochrome.trace_add("write", update_colour_menu_state)

full_colour_menu = tk.OptionMenu(window, tk.StringVar(value="8-bit"), *BitDepth)
full_colour_menu.pack()

def generate_ascii():
    if selected_files:
        for file_path in selected_files:
            my_art = AsciiArt.from_image(file_path)
            my_art.to_html_file(
                file_path + ".html",
                monochrome=monochrome.get(),
                columns=int(columns.get()) if columns.get() else 80  # Provide a default value of 80 if the entry box is empty
            )
            print("ASCII art generated and saved as", file_path + ".html")
    else:
        print("Please select a file beforegenerating ASCII art.")

# Choose File
select_button = tk.Button(window, text="Select File(s)", command=callback)
select_button.pack()

# Selected File(s) listbox
selected_files_label = tk.Label(text="Selected File(s)")
selected_files_label.pack()

# Create a frame to contain the listbox and scrollbar
list_frame = tk.Frame(window)
list_frame.pack(fill=tk.BOTH, expand=True)

selected_files_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=len(selected_files))
selected_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
MAX_HEIGHT = 10 # Defines the maximum height for the listbox

# Scrollbar for the listbox
scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
selected_files_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=selected_files_listbox.yview)

def update_selected_files_listbox():
    selected_files_listbox.delete(0, tk.END)
    num_files = len(selected_files)
    for i in range(min(num_files, MAX_HEIGHT)): # Limit to Max height or the number of files, whichever is smaller
        selected_files_listbox.insert(tk.END, selected_files[i])
    if num_files > MAX_HEIGHT:
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    else:
        scrollbar.pack_forget()  # Hide the scrollbar if not needed

# Bind the listbox's yview() method to the scrollbar's set() method
selected_files_listbox.bind('<MouseWheel>', lambda event: selected_files_listbox.yview_scroll(int(-1*(event.delta/120)), "units"))

# Generate ASCII Button
generate_button = tk.Button(window, text="Generate ASCII Art", command=generate_ascii)
generate_button.pack()

close_button = tk.Button(window, text="Close Window", command=close_window)
close_button.pack()

window.mainloop()

# Now I can access the selected file path, the number of columns, and the monochrome option
print("Selected file path:", selected_files)
print("Number of columns:", columns.get())
print("Monochrome:", monochrome.get())
print("Full Color:", full_color.get())
