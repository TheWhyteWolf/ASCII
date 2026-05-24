import tkinter as tk
import os
from tkinter import filedialog
from ascii_magic import AsciiArt
from PIL import ImageEnhance
import ascii_magic
from ascii_magic.constants import CHARS_BY_DENSITY as DEFAULT_CHARS

# ── Constants ─────────────────────────────────────────────────────────────────

DEFAULT_COLUMNS = 80
MAX_COLUMNS     = 800
MAX_HEIGHT      = 10

YesNo    = ["Yes", "No"]
BitDepth = ["16-bit", "8-bit"]

CHAR_SETS = {
    "Standard":
        None,
    "Blocks":
        " .·∙▏▁▔▎▂▍▃▐▌▄▅▋▆▊▇▉▀▖▗▘▝○□▭▯⬜▱◇◊△▲⬡⬠▽▼◔◐◑◒◓◫░◰◱◲◳▚▞▒▛▙▜▟▢▣⊞⊟▤▥▦▧▨▩▓◍◎⊕⊙⊚⊛⊜⊗⊘⊡◆◉⬟⬢⊠●▪▰▮▬■◼⬤⬛█",
    "Alphanumeric":
        " .'`^\"-_~:;=!*+<>/\\|()[]{}?1iljftrzJcvLIseao27YuZnTxCkwqm3hSbdgp4VXFGE59OAUBPRHKD6NM0W8Q@#$%&",
    "Numerals":
        " ⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉1234567890⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅪⅫ⓪⓫⓬⓭⓮⓯⓰⓱⓲⓳",
    "Japanese Kana":
        " へにこくつういのもしあかきけさすせそたちてとなぬねはひふほまみむめゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽアイウエオカキクケコサシスセソタチツテトガギグゲ",
}

# ── Window & variables ────────────────────────────────────────────────────────

window = tk.Tk()
window.title("IMS + ASCII MAGIC Converter")
window.minsize(420, 540)

selected_files = []

columns      = tk.IntVar()
monochrome   = tk.StringVar(value="No")   # StringVar so OptionMenu returns "Yes"/"No" correctly
brightness   = tk.DoubleVar(value=1.0)
saturation   = tk.DoubleVar(value=1.0)
colour_depth = tk.StringVar(value="8-bit")
char_set_var = tk.StringVar(value="Standard")

IEBright = ImageEnhance.Brightness
IESat    = ImageEnhance.Color

# Populated during create_*; declared here so all functions can reference them
selected_files_listbox = None
scrollbar              = None
status_label           = None

# ── UI builders ───────────────────────────────────────────────────────────────

def create_widgets():
    tk.Label(window, text="IMS + ASCII MAGIC Converter",
             font=("", 12, "bold")).pack(pady=(10, 4))
    create_input_widgets()
    create_options_widgets()
    create_listbox_and_scrollbar()
    create_buttons()
    create_status_bar()


def create_input_widgets():
    tk.Label(window, text=f"Columns (50–{MAX_COLUMNS}):  default = {DEFAULT_COLUMNS}").pack()
    tk.Entry(window, textvariable=columns, validate="key",
             validatecommand=(window.register(validate_column_input), '%P')).pack()

    tk.Label(window, text="Brightness (0–5):  default = 1.0").pack()
    tk.Entry(window, textvariable=brightness, validate="key",
             validatecommand=(window.register(validate_float_input), '%P')).pack()

    tk.Label(window, text="Saturation (0–5):  default = 1.0").pack()
    tk.Entry(window, textvariable=saturation, validate="key",
             validatecommand=(window.register(validate_float_input), '%P')).pack()


def create_options_widgets():
    tk.Label(window, text="Monochrome:").pack()
    tk.OptionMenu(window, monochrome, *YesNo).pack()

    tk.Label(window, text="Colour Depth:").pack()
    tk.OptionMenu(window, colour_depth, *BitDepth).pack()

    tk.Label(window, text="Character Set:").pack()
    tk.OptionMenu(window, char_set_var, *CHAR_SETS.keys()).pack()


def create_listbox_and_scrollbar():
    global selected_files_listbox, scrollbar

    tk.Label(window, text="Selected File(s)").pack()
    list_frame = tk.Frame(window)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=8)

    selected_files_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=1)
    selected_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
    selected_files_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=selected_files_listbox.yview)
    selected_files_listbox.bind(
        '<MouseWheel>',
        lambda e: selected_files_listbox.yview_scroll(int(-1 * (e.delta / 120)), "units")
    )


def create_buttons():
    tk.Button(window, text="Select File(s)",    command=callback).pack(pady=(8, 2))
    tk.Button(window, text="Generate ASCII Art", command=generate_ascii).pack(pady=2)
    tk.Button(window, text="Close Window",       command=close_window).pack(pady=(2, 8))


def create_status_bar():
    global status_label
    status_label = tk.Label(window, text="Ready.", anchor="w", relief=tk.SUNKEN, bd=1)
    status_label.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

# ── Callbacks ─────────────────────────────────────────────────────────────────

def callback():
    files = filedialog.askopenfilenames(
        filetypes=(("Image Files", (".png", ".jpg", ".tif", ".tiff", ".jpeg", ".bmp", ".gif")),)
    )
    if files:
        selected_files.clear()
        selected_files.extend(files)
        update_selected_files_listbox()
        set_status(f"{len(selected_files)} file(s) selected.")


def close_window():
    window.destroy()


def generate_ascii():
    if not selected_files:
        set_status("Please select at least one file before generating.")
        return

    selected_chars = CHAR_SETS[char_set_var.get()]
    total          = len(selected_files)
    is_mono        = (monochrome.get() == "Yes")
    is_full_colour = (colour_depth.get() == "16-bit")

    try:
        if selected_chars is not None:
            ascii_magic._ascii_magic.CHARS_BY_DENSITY = selected_chars

        for i, file_path in enumerate(selected_files, 1):
            set_status(f"Processing {i}/{total}: {os.path.basename(file_path)}…")
            window.update_idletasks()  # Keep UI responsive during batch processing

            try:
                my_art       = AsciiArt.from_image(file_path)
                my_art.image = IEBright(my_art.image).enhance(brightness.get())
                my_art.image = IESat(my_art.image).enhance(saturation.get())

                output_path = os.path.splitext(file_path)[0] + ".html"
                my_art.to_html_file(
                    output_path,
                    columns    = columns.get() or DEFAULT_COLUMNS,
                    monochrome = is_mono,
                    full_color = is_full_colour,
                )

                if char_set_var.get() == "Japanese Kana":
                    inject_cjk_font(output_path)

            except Exception as e:
                set_status(f"Error on {os.path.basename(file_path)}: {e}")
                continue  # Skip the failed file and carry on with the rest

    finally:
        ascii_magic._ascii_magic.CHARS_BY_DENSITY = DEFAULT_CHARS  # Always restore, even on crash

    set_status(f"Done — {total} file(s) converted.")

# ── Validators ────────────────────────────────────────────────────────────────

def validate_column_input(new_value):
    if new_value == "":
        return True
    if new_value.isdigit():
        return 50 <= int(new_value) <= MAX_COLUMNS
    return False


def validate_float_input(new_value):
    if new_value == "":
        return True
    try:
        return 0.0 <= float(new_value) <= 5.0
    except ValueError:
        return False

# ── Helpers ───────────────────────────────────────────────────────────────────

def set_status(message):
    """Update the status bar and mirror to console."""
    if status_label:
        status_label.config(text=message)
    print(message)


def inject_cjk_font(output_path):
    """Inject a Google Fonts CJK monospace stylesheet into the generated HTML."""
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            html = f.read()
        style = (
            '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Mono'
            ':wght@400&display=swap" rel="stylesheet">'
            '<style>body, pre, span { font-family: "Noto Sans Mono", monospace; }</style>'
        )
        html = html.replace("</head>", style + "</head>")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        set_status(f"Warning: could not inject CJK font — {e}")


def update_selected_files_listbox():
    selected_files_listbox.delete(0, tk.END)
    num_files    = len(selected_files)
    display_rows = min(num_files, MAX_HEIGHT)
    selected_files_listbox.config(height=max(1, display_rows))
    for i in range(display_rows):
        selected_files_listbox.insert(tk.END, selected_files[i])
    if num_files > MAX_HEIGHT:
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    else:
        scrollbar.pack_forget()

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    create_widgets()
    window.mainloop()
