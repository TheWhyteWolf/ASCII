import tkinter as tk
from tkinter import filedialog
import os
import json
import re
import webbrowser
from pathlib import Path
from ascii_magic import AsciiArt
from PIL import Image, ImageEnhance, ImageTk
import ascii_magic
from ascii_magic.constants import CHARS_BY_DENSITY as DEFAULT_CHARS

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

# ── Constants ─────────────────────────────────────────────────────────────────

DEFAULT_COLUMNS     = 80
MAX_COLUMNS         = 800
MAX_HEIGHT          = 8
DEFAULT_WIDTH_RATIO = 2.2
DEFAULT_FONT_SIZE   = 8
SETTINGS_PATH       = Path.home() / ".ascii_magic_settings.json"
PREVIEW_SIZE        = (160, 160)

SUPPORTED_EXT = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.gif'}

DARK  = {"bg": "#1e1e1e", "fg": "#d4d4d4", "entry": "#2d2d2d",
         "btn": "#3c3c3c", "select": "#264f78", "trough": "#3c3c3c"}
LIGHT = {"bg": "#f0f0f0", "fg": "#1e1e1e", "entry": "#ffffff",
         "btn": "#e0e0e0", "select": "#cce8ff", "trough": "#c0c0c0"}

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

DEFAULT_SETTINGS = {
    "columns":       "",
    "brightness":    1.4,
    "saturation":    1.0,
    "contrast":      1.0,
    "sharpness":     1.0,
    "width_ratio":   str(DEFAULT_WIDTH_RATIO),
    "font_size":     DEFAULT_FONT_SIZE,
    "monochrome":    "No",
    "colour_depth":  "8-bit",
    "char_set":      "Standard",
    "auto_preview":  "No",
    "dark_mode":     "No",
    "output_folder": "",
}

# ── Settings persistence ───────────────────────────────────────────────────────

def load_settings():
    try:
        with open(SETTINGS_PATH) as f:
            return {**DEFAULT_SETTINGS, **json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()


def save_settings():
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump({
                "columns":       columns_var.get(),
                "brightness":    brightness.get(),
                "saturation":    saturation.get(),
                "contrast":      contrast.get(),
                "sharpness":     sharpness.get(),
                "width_ratio":   width_ratio_var.get(),
                "font_size":     font_size.get(),
                "monochrome":    monochrome.get(),
                "colour_depth":  colour_depth.get(),
                "char_set":      char_set_var.get(),
                "auto_preview":  auto_preview.get(),
                "dark_mode":     dark_mode.get(),
                "output_folder": output_folder.get(),
            }, f, indent=2)
    except Exception as e:
        print(f"Could not save settings: {e}")

# ── Window ────────────────────────────────────────────────────────────────────

settings = load_settings()

window = TkinterDnD.Tk() if DND_AVAILABLE else tk.Tk()
window.title("IMS + ASCII MAGIC Converter")
window.minsize(500, 680)

# ── Variables ─────────────────────────────────────────────────────────────────

selected_files = []
output_folder  = tk.StringVar(value=settings["output_folder"])

# StringVar for text entries (handles empty string cleanly)
columns_var     = tk.StringVar(value=settings["columns"])
width_ratio_var = tk.StringVar(value=settings["width_ratio"])

# DoubleVar/IntVar for sliders
brightness   = tk.DoubleVar(value=settings["brightness"])
saturation   = tk.DoubleVar(value=settings["saturation"])
contrast     = tk.DoubleVar(value=settings["contrast"])
sharpness    = tk.DoubleVar(value=settings["sharpness"])
font_size    = tk.IntVar(value=settings["font_size"])

# Option menus
monochrome   = tk.StringVar(value=settings["monochrome"])
colour_depth = tk.StringVar(value=settings["colour_depth"])
char_set_var = tk.StringVar(value=settings["char_set"])
auto_preview = tk.StringVar(value=settings["auto_preview"])
dark_mode    = tk.StringVar(value=settings["dark_mode"])

IEBright   = ImageEnhance.Brightness
IESat      = ImageEnhance.Color
IEContrast = ImageEnhance.Contrast
IESharp    = ImageEnhance.Sharpness

# Widget references
selected_files_listbox = None
scrollbar              = None
status_label           = None
output_folder_label    = None
preview_label          = None
preview_image_ref      = None   # Held to prevent GC
tab_buttons            = {}
tab_frames             = {}
active_tab             = tk.StringVar(value="Image")

# ── Theme ─────────────────────────────────────────────────────────────────────

def theme():
    return DARK if dark_mode.get() == "Yes" else LIGHT


def apply_theme(widget=None):
    _restyle(widget or window, theme())


def _restyle(w, t):
    cls = type(w).__name__
    try:
        if cls in ("Tk", "Frame"):
            w.config(bg=t["bg"])
        elif cls == "Label":
            w.config(bg=t["bg"], fg=t["fg"])
        elif cls == "Button":
            w.config(bg=t["btn"], fg=t["fg"],
                     activebackground=t["bg"], activeforeground=t["fg"])
        elif cls == "Entry":
            w.config(bg=t["entry"], fg=t["fg"], insertbackground=t["fg"])
        elif cls == "Listbox":
            w.config(bg=t["entry"], fg=t["fg"],
                     selectbackground=t["select"], selectforeground=t["fg"])
        elif cls == "OptionMenu":
            w.config(bg=t["btn"], fg=t["fg"],
                     activebackground=t["bg"], activeforeground=t["fg"])
            try:
                w["menu"].config(bg=t["btn"], fg=t["fg"])
            except tk.TclError:
                pass
        elif cls == "Scale":
            w.config(bg=t["bg"], fg=t["fg"],
                     troughcolor=t["trough"], activebackground=t["btn"])
        elif cls == "Scrollbar":
            w.config(bg=t["btn"], troughcolor=t["trough"])
    except tk.TclError:
        pass

    for child in w.winfo_children():
        _restyle(child, t)

    _restyle_tabs(t)


def _restyle_tabs(t):
    for name, btn in tab_buttons.items():
        try:
            if name == active_tab.get():
                btn.config(bg=t["entry"], fg=t["fg"], relief=tk.SUNKEN)
            else:
                btn.config(bg=t["btn"], fg=t["fg"], relief=tk.RAISED)
        except tk.TclError:
            pass

# ── Tab system ────────────────────────────────────────────────────────────────

def switch_tab(name):
    active_tab.set(name)
    for n, frame in tab_frames.items():
        if n == name:
            frame.pack(fill=tk.X, padx=8, pady=(0, 4))
        else:
            frame.pack_forget()
    _restyle_tabs(theme())

# ── UI helpers ────────────────────────────────────────────────────────────────

def _labeled_entry(parent, text, var, validator):
    tk.Label(parent, text=text).pack(anchor="w", padx=8)
    tk.Entry(parent, textvariable=var, validate="key",
             validatecommand=(window.register(validator), '%P')
             ).pack(fill=tk.X, padx=8, pady=(0, 6))


def _labeled_scale(parent, text, var, from_, to, resolution=0.1):
    tk.Label(parent, text=text).pack(anchor="w", padx=8)
    tk.Scale(parent, variable=var, from_=from_, to=to,
             resolution=resolution, orient=tk.HORIZONTAL
             ).pack(fill=tk.X, padx=8, pady=(0, 6))


def _labeled_menu(parent, text, var, options, cmd=None):
    tk.Label(parent, text=text).pack(anchor="w", padx=8)
    kwargs = {"command": cmd} if cmd else {}
    tk.OptionMenu(parent, var, *options, **kwargs).pack(anchor="w", padx=8, pady=(0, 6))

# ── UI builders ───────────────────────────────────────────────────────────────

def create_widgets():
    tk.Label(window, text="IMS + ASCII MAGIC Converter",
             font=("", 12, "bold")).pack(pady=(10, 4))
    _create_tab_bar()
    _create_file_area()
    _create_action_buttons()
    _create_status_bar()
    apply_theme()


def _create_tab_bar():
    bar = tk.Frame(window)
    bar.pack(fill=tk.X, padx=8, pady=(4, 0))

    for name in ("Image", "Style", "Output"):
        frame = tk.Frame(window, bd=1, relief=tk.GROOVE)
        tab_frames[name] = frame
        btn = tk.Button(bar, text=name, width=10,
                        command=lambda n=name: switch_tab(n))
        btn.pack(side=tk.LEFT, padx=1)
        tab_buttons[name] = btn

    _build_image_tab(tab_frames["Image"])
    _build_style_tab(tab_frames["Style"])
    _build_output_tab(tab_frames["Output"])
    switch_tab("Image")


def _build_image_tab(p):
    tk.Label(p, text="").pack(pady=1)
    _labeled_entry(p, f"Columns (50–{MAX_COLUMNS}),  default = {DEFAULT_COLUMNS}:",
                   columns_var, _validate_columns)
    _labeled_entry(p, f"Width Ratio (0.5–4.0),  default = {DEFAULT_WIDTH_RATIO}:",
                   width_ratio_var, _validate_float)
    _labeled_scale(p, "Brightness (0.0–5.0):", brightness, 0.0, 5.0)
    _labeled_scale(p, "Saturation (0.0–5.0):", saturation, 0.0, 5.0)
    _labeled_scale(p, "Contrast (0.0–5.0):",   contrast,   0.0, 5.0)
    _labeled_scale(p, "Sharpness (0.0–5.0):",  sharpness,  0.0, 5.0)
    _labeled_scale(p, f"Font Size (4–32 px),  default = {DEFAULT_FONT_SIZE}:",
                   font_size, 4, 32, resolution=1)
    tk.Label(p, text="").pack(pady=1)


def _build_style_tab(p):
    tk.Label(p, text="").pack(pady=1)
    _labeled_menu(p, "Monochrome:",    monochrome,   YesNo)
    _labeled_menu(p, "Colour Depth:",  colour_depth, BitDepth)
    _labeled_menu(p, "Character Set:", char_set_var, list(CHAR_SETS.keys()))
    tk.Label(p, text="").pack(pady=1)


def _build_output_tab(p):
    global output_folder_label
    tk.Label(p, text="").pack(pady=1)
    _labeled_menu(p, "Auto-preview in browser:", auto_preview, YesNo)
    _labeled_menu(p, "Dark Mode:", dark_mode, YesNo,
                  cmd=lambda _: apply_theme())

    tk.Label(p, text="Output Folder:").pack(anchor="w", padx=8)
    row = tk.Frame(p)
    row.pack(fill=tk.X, padx=8, pady=(0, 6))

    saved = output_folder.get()
    output_folder_label = tk.Label(
        row, text=_truncate(saved) if saved else "Same as source image",
        anchor="w", relief=tk.SUNKEN, bd=1, width=28)
    output_folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(row, text="Browse…", command=_choose_folder).pack(side=tk.LEFT, padx=(4, 0))
    tk.Button(row, text="Clear",   command=_clear_folder).pack(side=tk.LEFT, padx=(2, 0))
    tk.Label(p, text="").pack(pady=1)


def _create_file_area():
    global selected_files_listbox, scrollbar, preview_label

    outer = tk.Frame(window)
    outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 0))

    # ── Left: listbox ──────────────────────────────────────────────────
    left = tk.Frame(outer)
    left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(left, text="Selected File(s)").pack(anchor="w")

    list_row = tk.Frame(left)
    list_row.pack(fill=tk.BOTH, expand=True)

    selected_files_listbox = tk.Listbox(list_row, selectmode=tk.MULTIPLE, height=6)
    selected_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    selected_files_listbox.bind("<<ListboxSelect>>", _on_listbox_select)
    selected_files_listbox.bind(
        "<MouseWheel>",
        lambda e: selected_files_listbox.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    scrollbar = tk.Scrollbar(list_row, orient=tk.VERTICAL)
    selected_files_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=selected_files_listbox.yview)

    # File buttons row
    btn_row = tk.Frame(left)
    btn_row.pack(fill=tk.X, pady=(3, 0))
    tk.Button(btn_row, text="Select File(s)",  command=_pick_files).pack(side=tk.LEFT, padx=(0, 2))
    tk.Button(btn_row, text="Remove Selected", command=_remove_selected).pack(side=tk.LEFT, padx=2)
    tk.Button(btn_row, text="Clear All",       command=_clear_all).pack(side=tk.LEFT, padx=2)

    # ── Right: preview ────────────────────────────────────────────────
    right = tk.Frame(outer, width=PREVIEW_SIZE[0] + 10)
    right.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
    right.pack_propagate(False)

    tk.Label(right, text="Preview").pack()
    preview_label = tk.Label(right, text="No\npreview",
                             anchor="center", relief=tk.SUNKEN, bd=1)
    preview_label.pack(fill=tk.BOTH, expand=True)

    # Drag-and-drop binding
    if DND_AVAILABLE:
        selected_files_listbox.drop_target_register(DND_FILES)
        selected_files_listbox.dnd_bind("<<Drop>>", _on_drop)
        tk.Label(window, text="✓ Drag & drop enabled", font=("", 7)).pack()
    else:
        tk.Label(window, text="pip install tkinterdnd2 to enable drag & drop",
                 font=("", 7)).pack()


def _create_action_buttons():
    tk.Button(window, text="Generate ASCII Art", command=generate_ascii,
              font=("", 10, "bold")).pack(pady=(8, 2), ipadx=10, ipady=3)
    tk.Button(window, text="Close", command=_on_close).pack(pady=(0, 8))


def _create_status_bar():
    global status_label
    status_label = tk.Label(window, text="Ready.", anchor="w", relief=tk.SUNKEN, bd=1)
    status_label.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

# ── File management ───────────────────────────────────────────────────────────

def _pick_files():
    files = filedialog.askopenfilenames(
        filetypes=(("Image Files", (".png", ".jpg", ".tif", ".tiff", ".jpeg", ".bmp", ".gif")),))
    if files:
        _add_files(list(files))


def _on_drop(event):
    paths = _parse_drop(event.data)
    if paths:
        _add_files(paths)
    else:
        set_status("Drop contained no supported image files.")


def _parse_drop(data):
    parts = re.findall(r'\{[^}]+\}|\S+', data)
    return [p.strip('{}') for p in parts
            if os.path.isfile(p.strip('{}'))
            and Path(p.strip('{}')).suffix.lower() in SUPPORTED_EXT]


def _add_files(paths):
    added = 0
    for p in paths:
        if p not in selected_files:
            selected_files.append(p)
            added += 1
    _refresh_listbox()
    set_status(f"{added} file(s) added — {len(selected_files)} total.")
    if selected_files:
        _show_preview(selected_files[-1])


def _remove_selected():
    indices = list(selected_files_listbox.curselection())
    if not indices:
        set_status("No files highlighted in the list.")
        return
    for i in reversed(indices):
        del selected_files[i]
    _refresh_listbox()
    set_status(f"Removed {len(indices)} file(s) — {len(selected_files)} remaining.")
    _show_preview(selected_files[0]) if selected_files else _clear_preview()


def _clear_all():
    selected_files.clear()
    _refresh_listbox()
    _clear_preview()
    set_status("File list cleared.")


def _on_listbox_select(event):
    idx = selected_files_listbox.curselection()
    if idx:
        _show_preview(selected_files[idx[0]])


def _refresh_listbox():
    selected_files_listbox.delete(0, tk.END)
    n = len(selected_files)
    selected_files_listbox.config(height=max(1, min(n, MAX_HEIGHT)))
    for p in selected_files:
        selected_files_listbox.insert(tk.END, p)
    if n > MAX_HEIGHT:
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    else:
        scrollbar.pack_forget()

# ── Preview ───────────────────────────────────────────────────────────────────

def _show_preview(path):
    global preview_image_ref
    try:
        img = Image.open(path)
        img.thumbnail(PREVIEW_SIZE, Image.LANCZOS)
        preview_image_ref = ImageTk.PhotoImage(img)
        preview_label.config(image=preview_image_ref, text="")
    except Exception:
        preview_label.config(image="", text="Preview\nunavailable")


def _clear_preview():
    global preview_image_ref
    preview_image_ref = None
    preview_label.config(image="", text="No\npreview")

# ── Output folder ─────────────────────────────────────────────────────────────

def _choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_folder.set(folder)
        output_folder_label.config(text=_truncate(folder))
        set_status(f"Output folder: {folder}")


def _clear_folder():
    output_folder.set("")
    output_folder_label.config(text="Same as source image")
    set_status("Output folder cleared — saving beside source images.")


def _truncate(path, n=36):
    return path if len(path) <= n else "…" + path[-(n - 1):]


def _resolve_output(source_path):
    base   = os.path.splitext(os.path.basename(source_path))[0] + ".html"
    folder = output_folder.get()
    return os.path.join(folder, base) if folder else os.path.splitext(source_path)[0] + ".html"

# ── Value helpers ─────────────────────────────────────────────────────────────

def _get_columns():
    try:
        v = int(columns_var.get())
        return v if 50 <= v <= MAX_COLUMNS else DEFAULT_COLUMNS
    except (ValueError, TypeError):
        return DEFAULT_COLUMNS


def _get_width_ratio():
    try:
        v = float(width_ratio_var.get())
        return v if 0.5 <= v <= 4.0 else DEFAULT_WIDTH_RATIO
    except (ValueError, TypeError):
        return DEFAULT_WIDTH_RATIO

# ── Generation ────────────────────────────────────────────────────────────────

def generate_ascii():
    if not selected_files:
        set_status("Please select at least one file before generating.")
        return

    selected_chars = CHAR_SETS[char_set_var.get()]
    total          = len(selected_files)
    is_mono        = monochrome.get() == "Yes"
    is_full_colour = colour_depth.get() == "16-bit"
    should_preview = auto_preview.get() == "Yes"
    cols           = _get_columns()
    ratio          = _get_width_ratio()
    fsize          = font_size.get() or DEFAULT_FONT_SIZE

    try:
        if selected_chars is not None:
            ascii_magic._ascii_magic.CHARS_BY_DENSITY = selected_chars

        for i, file_path in enumerate(selected_files, 1):
            set_status(f"Processing {i}/{total}: {os.path.basename(file_path)}…")
            window.update_idletasks()

            try:
                my_art       = AsciiArt.from_image(file_path)
                my_art.image = IEBright(my_art.image).enhance(brightness.get())
                my_art.image = IESat(my_art.image).enhance(saturation.get())
                my_art.image = IEContrast(my_art.image).enhance(contrast.get())
                my_art.image = IESharp(my_art.image).enhance(sharpness.get())

                output_path = _resolve_output(file_path)
                my_art.to_html_file(
                    output_path,
                    columns           = cols,
                    width_ratio       = ratio,
                    monochrome        = is_mono,
                    full_color        = is_full_colour,
                    additional_styles = f"font-size: {fsize}px;",
                )

                if char_set_var.get() == "Japanese Kana":
                    _inject_cjk_font(output_path)

                if should_preview:
                    webbrowser.open(f"file://{os.path.abspath(output_path)}")

            except Exception as e:
                set_status(f"Error on {os.path.basename(file_path)}: {e}")
                continue

    finally:
        ascii_magic._ascii_magic.CHARS_BY_DENSITY = DEFAULT_CHARS  # Always restore

    set_status(f"Done — {total} file(s) converted.")

# ── Validators ────────────────────────────────────────────────────────────────

def _validate_columns(v):
    if v == "": return True
    return v.isdigit()   # Range enforced at generation time


def _validate_float(v):
    if v == "": return True
    try:
        float(v)
        return True
    except ValueError:
        return False

# ── Helpers ───────────────────────────────────────────────────────────────────

def set_status(message):
    if status_label:
        status_label.config(text=message)
    print(message)


def _inject_cjk_font(output_path):
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


def _on_close():
    save_settings()
    window.destroy()

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    create_widgets()
    window.mainloop()
