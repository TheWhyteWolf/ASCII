import tkinter as tk
from tkinter import filedialog
from ascii_magic import AsciiArt

window = tk.Tk()
selected_file = tk.StringVar()
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
    file_path = filedialog.askopenfilename()
    selected_file.set(file_path)  # Store the file path in the selected_file variable

def close_window():
    window.destroy()

def validate_input(new_value):
    if new_value.isdigit():
        value = int(new_value)
        if 50 <= value <= 300:
            return True
    return False

# Column entry Box
input_label = tk.Label(text="Enter the number of columns (50-300):")
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
    if selected_file.get():
        my_art = AsciiArt.from_image(selected_file.get())
        my_art.to_html_file(
            selected_file.get() + ".html",
            monochrome=monochrome.get(),
            columns=columns.get()
        )
        print("ASCII art generated and saved as", selected_file.get() + ".html")
    else:
        print("Please select a file before generating ASCII art.")

# Choose File
select_button = tk.Button(window, text="Select File", command=callback)
select_button.pack()

# Generate ASCII Button
generate_button = tk.Button(window, text="Generate ASCII Art", command=generate_ascii)
generate_button.pack()

close_button = tk.Button(window, text="Close Window", command=close_window)
close_button.pack()

window.mainloop()

# Now I can access the selected file path, the number of columns, and the monochrome option
print("Selected file path:", selected_file.get())
print("Number of columns:", columns.get())
print("Monochrome:", monochrome.get())
print("Full Color:", full_color.get())
