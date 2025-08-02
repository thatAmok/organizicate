import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for embedding
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging
# --- Disabled categories persistence ---
LOG_FILE = "organizicate.log"
import os
import shutil
import json 
import threading
import queue
from tkinter import ttk
import tkinter as tk
from tkinterdnd2 import TkinterDnD
import ttkbootstrap as ttkb
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import tkinterdnd2 as tkdnd
from collections import defaultdict
import copy
from typing import Dict, List
# Add fors tray and tooltips
import sys
try:
    import pystray
    from PIL import Image
except ImportError:
    pystray = None
    Image = None


# --- Disabled categories persistence ---
DISABLED_CATEGORIES_FILE = "disabled_categories.json"
def load_disabled_categories():
    try:
        if os.path.isfile(DISABLED_CATEGORIES_FILE):
            with open(DISABLED_CATEGORIES_FILE, 'r') as f:
                data = json.load(f)
            if isinstance(data, list):
                return set(data)
    except Exception as e:
        print(f"Failed to load disabled categories: {e}")
    return set()
def save_disabled_categories(disabled_set):
    try:
        with open(DISABLED_CATEGORIES_FILE, 'w') as f:
            json.dump(list(disabled_set), f, indent=2)
    except Exception as e:
        print(f"Failed to save disabled categories: {e}")

RECENT_ACTIONS_LIMIT = 20
logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

CONFIG_FILE = "config.json"

default_file_categories = {
    "Documents": [
        # Text & Markdown
        '.doc', '.docx', '.odt', '.txt', '.rtf', '.pages', '.tex', '.wpd', '.wps', '.md', '.markdown', '.rst',
        # Spreadsheets
        '.xls', '.xlsx', '.csv', '.ods', '.numbers', '.tsv', '.dif', '.dbf',
        # Presentations
        '.ppt', '.pptx', '.odp', '.key', '.pps', '.sldx',
        # PDFs and Digital Forms
        '.pdf', '.xps', '.fdf',
        # eBooks
        '.epub', '.mobi', '.azw3', '.fb2', '.ibooks',
        # Markup, Calendar, ContactCards, Learning/Education
        '.djvu', '.ical', '.ics', '.vcard', '.vcf', '.mbox', '.eml', '.msg', '.pst', '.ost',
    ],
    "Pictures": [
        # Raster Images
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.ico',
        # RAW Camera Images
        '.raw', '.cr2', '.nef', '.orf', '.sr2', '.arw', '.dng', '.pef', '.raf', '.rw2',
        # Vector Graphics
        '.svg', '.ai', '.eps', '.cdr', '.wmf', '.emf', '.fh', '.sketch',
        # Design
        '.psd', '.xcf', '.indd', '.kra', '.afdesign', '.xd', '.fig',
    ],    "Audio": [
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff', '.alac', '.mid', '.midi', '.ape', '.opus', '.amr', '.dsd',
        '.als', '.flp', '.logicx', '.ptx', '.aup', '.band',
    ],
    "Videos": [
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.3gp', '.vob', '.mts', '.m2ts', '.ts', '.rm', '.rmvb', '.divx', '.xvid', '.f4v',
        '.prproj', '.veg', '.aep', '.pproj', '.fcpx', '.mlt', '.drp',
    ],
    "Archives": [
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg', '.cab', '.arj', '.lz', '.lzma', '.apk', '.rpm', '.deb', '.jar', '.vhd', '.vdi',
        '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2', '.txz',
        '.bak', '.tmp', '.old', '.backup', '.swp', '.swo', '.sav', '.bkp',
    ],
    # 'Code' category moved to subcategory under 'Others'
    "System & Apps": [
        '.plist', '.command', '.app', '.kext', '.dylib', '.pkg', '.dmg',
        '.run', '.service', '.so', '.desktop', '.deb', '.rpm', '.conf', '.unit', '.appimage', '.snap', '.flatpak', '.journal',
        '.exe', '.msi', '.bat', '.dll', '.sys', '.reg', '.com', '.scr', '.drv', '.efi', '.lnk', '.pif', '.scf', '.library-ms', '.folder', '.desklink',
        '.conf', '.ini', '.yaml', '.yml', '.json', '.toml', '.rc', '.cfg', '.plist',
        '.sh', '.bash', '.ps1', '.zsh', '.bashrc', '.zshrc', '.profile', '.bash_profile', '.xinitrc', '.xsession', '.inputrc', '.gtkrc-2.0',
        '.jar', '.apk', '.bin', '.gadget', '.mod', '.pak', '.sav', '.save', '.gam', '.dat', '.nes', '.snes', '.gba', '.gb', '.iso', '.xex', '.x86', '.x64',
        '.mcworld', '.mcpack', '.mcaddon', '.mcmeta', '.mctemplate', '.nbt', '.litemod', '.mcfunction',
        '.vmdk', '.vdi', '.vhd', '.vhdx', '.qcow2', '.ova', '.ovf',
        '.log', '.db', '.sql', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.ldf', '.ndf',
        '.ttf', '.otf', '.woff', '.woff2', '.eot', '.fon', '.fnt', '.pfb', '.pfm', '.afm',
        '.pem', '.crt', '.cer', '.der', '.pfx', '.p12', '.key',
        '.trace', '.err', '.out', '.cache', '.gpg', '.pgp', '.aes', '.enc', '.crypt', '.lock',
        '.srt', '.sub', '.idx', '.ssa', '.ass',
        '.url', '.webloc', '.alias',
        '.shp', '.shx', '.kml', '.kmz', '.gpx',
        '.crash',
    ],
    "Others": [
        '.iso', '.img', '.dmg', '.bak', '.tar', '.gz', '.xz', '.sparsebundle', '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2', '.txz', '.old', '.backup', '.tmp', '.swp', '.swo', '.sav', '.bkp',
        '.vst', '.vst3', '.plugin', '.xpi', '.crx', '.safariextz', '.litemod', '.mcaddon', '.mcpack', '.mcmeta', '.nbt',
        '.vmdk', '.vbox', '.qcow2', '.ova', '.ovf', 'Dockerfile', '.dockerignore', '.compose',
        '.torrent', '.unknown', '.misc', '.zzz', '.foo', '.bar', '.random', '.undefined', '.none', '.file', '.stuff', '.miscfile', '.extra', '.spare', '.spurious', '.junk', '.useless', '.zzz2', '.zzz3', '.zzz4', '.zzz5', '.zzz6', '.zzz7', '.zzz8', '.zzz9', '.zzz10',
        '.dmp', '.dump', '.temp',
        # Code extensions are now handled as a subcategory in subcategory_map["Others"]
    ],
    # 3D & CAD, Design, and Code are now subcategories under Others (see subcategory_map)
}

# --- Subcategory mappings for subfolder support ---
subcategory_map = {
    "Documents": {
        "Text & Markdown": ['.doc', '.docx', '.odt', '.txt', '.rtf', '.pages', '.tex', '.wpd', '.wps', '.md', '.markdown', '.rst'],
        "Spreadsheets": ['.xls', '.xlsx', '.csv', '.ods', '.numbers', '.tsv', '.dif', '.dbf'],
        "Presentations": ['.ppt', '.pptx', '.odp', '.key', '.pps', '.sldx'],
        "PDFs and Digital Forms": ['.pdf', '.xps', '.fdf'],
        "eBooks": ['.epub', '.mobi', '.azw3', '.fb2', '.ibooks'],
        "Other": ['.djvu', '.ical', '.ics', '.vcard', '.vcf', '.mbox', '.eml', '.msg', '.pst', '.ost'],
    },
    "Pictures": {
        "Raster Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.ico'],
        "RAW Camera Images": ['.raw', '.cr2', '.nef', '.orf', '.sr2', '.arw', '.dng', '.pef', '.raf', '.rw2'],
        "Vector Graphics": ['.svg', '.ai', '.eps', '.cdr', '.wmf', '.emf', '.fh', '.sketch'],
        "Designs": ['.psd', '.xcf', '.indd', '.kra', '.afdesign', '.xd', '.fig'],
    },
    "System & Apps": {
        "macOS": ['.plist', '.command', '.app', '.kext', '.dylib', '.pkg', '.dmg'],
        "Linux": ['.run', '.service', '.so', '.desktop', '.deb', '.rpm', '.conf', '.unit', '.appimage', '.snap', '.flatpak', '.journal'],
        "Windows": ['.exe', '.msi', '.bat', '.dll', '.sys', '.reg', '.com', '.scr', '.drv', '.efi', '.lnk', '.pif', '.scf', '.library-ms', '.folder', '.desklink'],
        "Configuration": ['.ini', '.yaml', '.yml', '.json', '.toml', '.rc', '.cfg'],
        "Scripting": ['.sh', '.bash', '.ps1', '.zsh', '.bashrc', '.zshrc', '.profile', '.bash_profile', '.xinitrc', '.xsession', '.inputrc', '.gtkrc-2.0'],
        "Other": ['.jar', '.apk', '.bin', '.gadget', '.mod', '.pak', '.sav', '.save', '.gam', '.dat', '.nes', '.snes', '.gba', '.gb', '.iso', '.xex', '.x86', '.x64',
            '.mcworld', '.mcpack', '.mcaddon', '.mcmeta', '.mctemplate', '.nbt', '.litemod', '.mcfunction',
            '.vmdk', '.vdi', '.vhd', '.vhdx', '.qcow2', '.ova', '.ovf',
            '.log', '.db', '.sql', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.ldf', '.ndf',
            '.ttf', '.otf', '.woff', '.woff2', '.eot', '.fon', '.fnt', '.pfb', '.pfm', '.afm',
            '.pem', '.crt', '.cer', '.der', '.pfx', '.p12', '.key',
            '.trace', '.err', '.out', '.cache', '.gpg', '.pgp', '.aes', '.enc', '.crypt', '.lock',
            '.srt', '.sub', '.idx', '.ssa', '.ass',
            '.url', '.webloc', '.alias',
            '.shp', '.shx', '.kml', '.kmz', '.gpx',
            '.crash',
        ],
    },
    "Others": {
        "Backups & Disk Images": ['.iso', '.img', '.dmg', '.bak', '.tar', '.gz', '.xz', '.sparsebundle', '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2', '.txz', '.old', '.backup', '.tmp', '.swp', '.swo', '.sav', '.bkp'],
        "Plugins & Extensions": ['.vst', '.vst3', '.plugin', '.xpi', '.crx', '.safariextz', '.litemod', '.mcaddon', '.mcpack', '.mcmeta', '.nbt'],
        "Virtual Machines & Containers": ['.vmdk', '.vbox', '.qcow2', '.ova', '.ovf', 'Dockerfile', '.dockerignore', '.compose'],
        "Miscellaneous": ['.torrent', '.unknown', '.misc', '.zzz', '.foo', '.bar', '.random', '.undefined', '.none', '.file', '.stuff', '.miscfile', '.extra', '.spare', '.spurious', '.junk', '.useless', '.zzz2', '.zzz3', '.zzz4', '.zzz5', '.zzz6', '.zzz7', '.zzz8', '.zzz9', '.zzz10', '.dmp', '.dump', '.temp'],
        "Code": [
            '.py', '.js', '.java', '.c', '.cpp', '.cs', '.rb', '.php', '.html', '.css', '.go', '.rs', '.swift', '.kt', '.m', '.pl', '.bat', '.cmd', '.ts', '.tsx', '.jsx', '.lua', '.groovy', '.vbs', '.r', '.h', '.hpp', '.asm', '.s', '.d', '.erl',
            '.ps1', '.tcl', '.zsh', '.fish', '.jsp', '.asp', '.aspx', '.cgi', '.vue', '.json', '.xml', '.yaml', '.yml',
            'Dockerfile', '.dockerignore', '.compose', 'Makefile', 'CMakeLists.txt', '.sln', '.vcxproj', '.xcodeproj', '.gradle', '.idea', '.iml', '.project', '.classpath', '.command',
            '.bashrc', '.zshrc', '.profile', '.bash_profile', '.xinitrc', '.xsession', '.inputrc', '.gtkrc-2.0',
            '.xcworkspace', '.xcodeproj', '.nib', '.xib', '.dylib', '.ko',
        ],
    },
}

RECENT_ACTIONS_LIMIT = 20

def load_categories() -> Dict[str, List[str]]:
    """Load categories from config or default if no config found."""
    user_categories = {}
    
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            # Validate loaded data (dict[str, list[str]])
            if isinstance(data, dict):
                for k, v in data.items():
                    if not isinstance(k, str) or not isinstance(v, list):
                        raise ValueError("Invalid config format")
                user_categories = data
        except Exception as e:
            print(f"Failed to load config: {e}")
            user_categories = {}
    
    # Merge default categories with user categories
    # Default categories take precedence in case of conflicts
    all_categories = copy.deepcopy(default_file_categories)
    
    # Add user categories that don't conflict with default ones
    for cat_name, extensions in user_categories.items():
        if cat_name not in default_file_categories:
            all_categories[cat_name] = extensions
    
    return all_categories

def save_categories(categories):
    """Save only user-added categories to config file."""
    try:
        # Only save categories that are not in the default set
        user_categories = {
            cat: exts for cat, exts in categories.items() 
            if cat not in default_file_categories
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(user_categories, f, indent=2)
    except Exception as e:
        print(f"Failed to save config: {e}")

def build_extension_map(categories):
    """Build reverse map from extension to category."""
    ext_map = {}
    for cat, exts in categories.items():
        for ext in exts:
            ext_map[ext.lower()] = cat
    return ext_map

class ToolTip:
    """Simple tooltip for tkinter widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
        self.exclusions = set()
        self.exclude_window = None
        self.excluded_paths = []

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        # Fix: Use a safe bbox index for widgets that don't support "insert"
        try:
            if self.widget.winfo_ismapped():
                # Use "insert" for Entry/Text, "active" for Listbox, fallback to (0,0,0,0)
                if isinstance(self.widget, tk.Listbox):
                    x, y, width, height = self.widget.bbox("active") or (0, 0, 0, 0)
                else:
                    x, y, width, height = self.widget.bbox("insert") or (0, 0, 0, 0)
            else:
                x, y, width, height = (0, 0, 0, 0)
        except Exception:
            x, y, width, height = (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("SF Pro Display", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class OrganizicateBeta(TkinterDnD.Tk):
    def _on_close(self):
        if self.settings.get("minimize_to_tray_on_close", False):
            self.minimize_to_tray()
        elif self.settings.get("confirm_quit", True):
            self.confirm_quit_dialog()
        else:
            self.destroy()
    SETTINGS_FILE = os.path.expanduser("~/.organizicate_settings.json")

    def load_settings(self):
        defaults = {
            "default_operation": list(self.operations.keys())[0] if hasattr(self, 'operations') else "Organize all files in a folder",
            "show_pie_chart": True,
            "minimize_to_tray_on_close": False,
            "confirm_delete": True,
            "confirm_quit": True,
            "output_log_font": "Fira Code",
            "output_log_font_size": 10,
            "output_log_max_lines": 500,
        }
        try:
            if os.path.isfile(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
        return defaults

    def save_settings(self):
        try:
            with open(self.SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass
    SETTINGS_FILE = os.path.expanduser("~/.organizicate_settings.json")

    def load_settings(self):
        defaults = {
            "default_operation": list(self.operations.keys())[0] if hasattr(self, 'operations') else "Organize all files in a folder",
            "show_pie_chart": True,
            "minimize_to_tray_on_close": False,
            "confirm_delete": True,
            "confirm_quit": True,
            "output_log_font": "Fira Code",
            "output_log_font_size": 10,
            "output_log_max_lines": 500,
        }
        try:
            if os.path.isfile(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
        return defaults

    def save_settings(self):
        try:
            with open(self.SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass
    def _init_pie_chart(self, parent):
        """Initialize the pie chart widget and data."""
        self.pie_chart_frame = ttk.Frame(parent)
        self.pie_chart_frame.pack(side='right', fill='y', padx=(0, 30))
        self.figure = Figure(figsize=(2.8, 2.8), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Organized Files by Category", fontsize=10)
        self.pie_canvas = FigureCanvasTkAgg(self.figure, master=self.pie_chart_frame)
        self.pie_canvas.get_tk_widget().pack(fill='both', expand=False)
        self.category_counts = {}  # {category: count}
        self._draw_pie_chart()

    def _draw_pie_chart(self):
        self.ax.clear()
        if self.category_counts:
            labels = [f"{cat} ({count})" for cat, count in self.category_counts.items()]
            sizes = list(self.category_counts.values())
            # Use a lighter color palette
            import matplotlib.colors as mcolors
            pastel_colors = list(mcolors.TABLEAU_COLORS.values()) + list(mcolors.CSS4_COLORS.values())
            pastel_colors = [c for c in pastel_colors if not c.lower().startswith('dark') and not c.lower().startswith('black') and not c.lower().startswith('navy')]
            # Cycle colors if not enough
            colors = pastel_colors[:len(labels)] if len(pastel_colors) >= len(labels) else (pastel_colors * ((len(labels) // len(pastel_colors)) + 1))[:len(labels)]
            self.ax.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=140, textprops={'fontsize': 8}, colors=colors)
        else:
            self.ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12)
        self.ax.set_title("Organized Files by Category", fontsize=10)
        self.pie_canvas.draw()

    def _update_pie_chart(self, count_moved):
        """Update the pie chart with new counts."""
        if not hasattr(self, 'category_counts'):
            self.category_counts = {}
        for cat, count in count_moved.items():
            self.category_counts[cat] = self.category_counts.get(cat, 0) + count
        self._draw_pie_chart()
    WELCOME_SHOWN_FILE = os.path.expanduser("~/.organizicate_welcome_shown")

    def show_welcome_dialog(self):
        """Show a modern welcome dialog with usage instructions and method explanations."""
        dialog = tk.Toplevel(self)
        dialog.title("Welcome to Organizicate!")
        dialog.iconify = lambda: None  # Prevent accidental minimize
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        # Set icon
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_ico = os.path.join(base_dir, "appico.ico")
            dialog.wm_iconbitmap(icon_ico)
        except Exception:
            pass
        self._center_window(dialog, 735, 484)
        # Main frame
        frame = ttk.Frame(dialog, padding=(24, 18, 24, 18))
        frame.pack(fill='both', expand=True)
        # Title
        title = ttk.Label(frame, text="Welcome to Organizicate!", font=("SF Pro Display", 18, "bold"))
        title.pack(pady=(0, 8))
        # Subtitle
        subtitle = ttk.Label(frame, text="Your smart file and folder organizer.", font=("SF Pro Display", 12, "italic"), foreground="#4a90e2")
        subtitle.pack(pady=(0, 16))
        # How to use
        howto = (
            "1. Select an organization method from the dropdown at the top.\n"
            "2. Enter or browse for a folder or file path.\n"
            "3. Click 'Organize' to start!\n"
            "4. Manage categories on the right to customize file types.\n"
            "5. Use the Undo button to revert the last move."
        )
        howto_label = ttk.Label(frame, text=howto, font=("SF Pro Display", 11), justify="left")
        howto_label.pack(anchor="w", pady=(0, 16))
        # Method explanations
        methods_title = ttk.Label(frame, text="Organization Methods:", font=("SF Pro Display", 12, "bold"))
        methods_title.pack(anchor="w", pady=(0, 4))
        methods = [
            ("Organize all files in a folder", "Sorts all files into folders by category (e.g., Documents, Pictures, etc.)."),
            ("Organize a single file", "Moves one file to its category folder."),
            ("Organize all folders in a folder", "Moves all folders into a 'Folders' folder."),
            ("Organize all folders in a folder (A-Z)", "Sorts all folders into subfolders by their first letter (A-Z, # for others)."),
            ("Organize everything in a folder", "Organizes both files and folders in one go."),
            ("Organize a single folder", "Moves one folder into a 'Folders' folder."),
            ("Organize a single folder (A-Z)", "Moves one folder into a subfolder by its first letter.")
        ]
        for name, desc in methods:
            row = ttk.Frame(frame)
            row.pack(anchor="w", fill="x", pady=1)
            ttk.Label(row, text="• ", font=("SF Pro Display", 11, "bold"), foreground="#0077ff").pack(side="left")
            ttk.Label(row, text=name+": ", font=("SF Pro Display", 11), foreground="#222").pack(side="left")
            ttk.Label(row, text=desc, font=("SF Pro Display", 11), foreground="#444").pack(side="left")
        # Close button
        close_btn = ttk.Button(frame, text="Get Started", command=dialog.destroy, style=self.button_style)
        close_btn.pack(pady=(18, 0))
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        # Mark welcome as shown if not already
        try:
            with open(self.WELCOME_SHOWN_FILE, "w") as f:
                f.write("shown")
        except Exception:
            pass
    def minimize_to_tray(self):
        """Minimize the app to the system tray using pystray."""
        if not pystray or not Image:
            messagebox.showerror("Tray Not Supported", "pystray or PIL is not installed. Minimize to tray is unavailable.")
            self.destroy()
            return
        if self.tray_icon:
            return  # Already minimized
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.withdraw()
        # Try to load icon
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._add_settings_menu()
        icon_path = os.path.join(base_dir, "appico.ico")
        if not os.path.exists(icon_path):
            icon_path = None
        image = None
        if icon_path:
            try:
                image = Image.open(icon_path)
            except Exception:
                image = None
        if not image:
            # Fallback: blank icon
            image = Image.new("RGB", (64, 64), color=(200, 200, 200))
        def on_restore(icon, item=None):
            self.after(0, self.restore_from_tray)
        def on_quit(icon, item=None):
            icon.stop()
            self.after(0, self.destroy)
        menu = pystray.Menu(
            pystray.MenuItem("Restore Organizicate", on_restore),
            pystray.MenuItem("Quit", on_quit)
        )
        self.tray_icon = pystray.Icon("organizicate", image, "Organizicate", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
    def _add_settings_menu(self):
        if hasattr(self, 'settings_menu_bar'):
            return
        if not hasattr(self, 'menu_bar'):
            self.menu_bar = tk.Menu(self)
        settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        # Default operation
        def_op_var = tk.StringVar(value=self.settings.get("default_operation", list(self.operations.keys())[0]))
        def set_default_op():
            self.settings["default_operation"] = def_op_var.get()
            self.save_settings()
            if messagebox.askyesno("Restart Required", "Changing the default operation requires a restart. Restart now?"):
                self._restart_app()
        settings_menu.add_command(label="Set Default Operation...", command=lambda: self._show_default_op_dialog(def_op_var, set_default_op))
        # Pie chart toggle
        pie_var = tk.BooleanVar(value=self.settings.get("show_pie_chart", True))
        def toggle_pie():
            self.settings["show_pie_chart"] = pie_var.get()
            self.save_settings()
            if messagebox.askyesno("Restart Required", "Changing the pie chart setting requires a restart. Restart now?"):
                self._restart_app()
        settings_menu.add_checkbutton(label="Show Pie Chart (Restart app)", variable=pie_var, command=toggle_pie)
        # Minimize to tray on close
        tray_var = tk.BooleanVar(value=self.settings.get("minimize_to_tray_on_close", False))
        def toggle_tray():
            self.settings["minimize_to_tray_on_close"] = tray_var.get()
            self.save_settings()
        settings_menu.add_checkbutton(label="Minimize to Tray on Close", variable=tray_var, command=toggle_tray)
        # Confirm dialogs
        confirm_delete_var = tk.BooleanVar(value=self.settings.get("confirm_delete", True))
        def toggle_confirm_delete():
            self.settings["confirm_delete"] = confirm_delete_var.get()
            self.save_settings()
        settings_menu.add_checkbutton(label="Confirm on Delete", variable=confirm_delete_var, command=toggle_confirm_delete)
        confirm_quit_var = tk.BooleanVar(value=self.settings.get("confirm_quit", True))
        def toggle_confirm_quit():
            self.settings["confirm_quit"] = confirm_quit_var.get()
            self.save_settings()
        settings_menu.add_checkbutton(label="Confirm on Quit", variable=confirm_quit_var, command=toggle_confirm_quit)
        # Output log font
        settings_menu.add_command(label="Output Log Font...", command=self._show_output_log_font_dialog)
        # Output log max lines
        settings_menu.add_command(label="Output Log Max Lines...", command=self._show_output_log_max_lines_dialog)
        self.menu_bar.insert_cascade(0, label="Settings", menu=settings_menu)
        self.settings_menu_bar = settings_menu
        self.config(menu=self.menu_bar)

    def _restart_app(self):
        import sys
        import subprocess
        python = sys.executable
        script = sys.argv[0]
        args = sys.argv[1:]
        try:
            subprocess.Popen([python, script] + args)
        except Exception as e:
            messagebox.showerror("Restart Failed", f"Could not restart app: {e}")
        self.destroy()

    def _show_default_op_dialog(self, var, on_save):
        dialog = tk.Toplevel(self)
        dialog.title("Set Default Operation")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        self._center_window(dialog, 340, 120)
        ttk.Label(dialog, text="Choose default operation:").pack(pady=(18, 8))
        combo = ttk.Combobox(dialog, values=list(self.operations.keys()), textvariable=var, state="readonly", width=32)
        combo.pack(pady=(0, 12))
        ttk.Button(dialog, text="Save", command=lambda: (on_save(), dialog.destroy()), style=self.button_style).pack()
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def _toggle_pie_chart(self, show):
        # Hide or show pie chart, and resize output log accordingly
        if hasattr(self, 'pie_chart_frame'):
            if show:
                self.pie_chart_frame.pack(side='right', fill='y', padx=(0, 30))
                self.output_text.pack_configure(side='left', fill='both', expand=False)
            else:
                self.pie_chart_frame.pack_forget()
                self.output_text.pack_configure(side='left', fill='both', expand=True)

    def _show_output_log_font_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Output Log Font")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        self._center_window(dialog, 340, 160)
        ttk.Label(dialog, text="Font Family:").pack(pady=(12, 2))
        font_var = tk.StringVar(value=self.settings.get("output_log_font", "Fira Code"))
        font_entry = ttk.Entry(dialog, textvariable=font_var)
        font_entry.pack(pady=(0, 8))
        ttk.Label(dialog, text="Font Size:").pack(pady=(2, 2))
        size_var = tk.IntVar(value=self.settings.get("output_log_font_size", 10))
        size_entry = ttk.Entry(dialog, textvariable=size_var)
        size_entry.pack(pady=(0, 8))
        def save_font():
            self.settings["output_log_font"] = font_var.get()
            self.settings["output_log_font_size"] = size_var.get()
            self.save_settings()
            self.output_text.config(font=(font_var.get(), size_var.get()))
            dialog.destroy()
        ttk.Button(dialog, text="Save", command=save_font, style=self.button_style).pack(pady=(6, 8))
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def _show_output_log_max_lines_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Output Log Max Lines")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        self._center_window(dialog, 340, 120)
        ttk.Label(dialog, text="Set max lines for output log:").pack(pady=(18, 8))
        max_var = tk.IntVar(value=self.settings.get("output_log_max_lines", 500))
        entry = ttk.Entry(dialog, textvariable=max_var)
        entry.pack(pady=(0, 12))
        def save_max():
            self.settings["output_log_max_lines"] = max_var.get()
            self.save_settings()
            dialog.destroy()
        ttk.Button(dialog, text="Save", command=save_max, style=self.button_style).pack()
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def _on_close(self):
        if self.settings.get("minimize_to_tray_on_close", False):
            self.minimize_to_tray()
        elif self.settings.get("confirm_quit", True):
            self.confirm_quit_dialog()
        else:
            self.destroy()
        # (Removed stray icon_path/image code that was duplicated and out of place)

    def restore_from_tray(self):
        """Restore the app from the system tray."""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.deiconify()
        self.withdrawn_for_tray = False
        self.lift()
        self.focus_force()
    def _center_window(self, win, width, height):
        """Center a Toplevel window on the screen."""
        win.update_idletasks()
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")
    def apply_custom_label_styles(self):
        """Apply custom label fonts for Output Log and Manage Categories label frames."""
        style = ttk.Style()
        style.configure("OutputLog.TLabelframe.Label", font=("SF Pro Display", 12, "normal"))
        style.configure("ManageCategories.TLabelframe.Label", font=("SF Pro Display", 12, "normal"))
    def _find_extension_conflicts(self, ext_list, ignore_category=None):
        """Return a dict of {ext: category} for extensions already assigned to other categories."""
        conflicts = {}
        for cat, exts in self.file_categories.items():
            if ignore_category and cat == ignore_category:
                continue
            for ext in ext_list:
                if ext in exts:
                    conflicts[ext] = cat
        return conflicts
    def add_category(self):
        """Add a new user category."""
        new_name = self.cat_name_var.get().strip()
        exts = self.cat_ext_var.get().strip()
        desc = self.cat_desc_var.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Category name cannot be empty.")
            return
        if new_name in self.file_categories:
            messagebox.showerror("Error", f"Category '{new_name}' already exists.")
            return
        ext_list = self.parse_extensions(exts)
        if not ext_list:
            messagebox.showerror("Error", "Please enter at least one valid extension (e.g. .txt).")
            return
        # Check for extension conflicts
        conflicts = self._find_extension_conflicts(ext_list)
        if conflicts:
            msg = "Warning: The following extensions are already assigned to other categories:\n"
            msg += "\n".join([f"{ext}: {cat}" for ext, cat in conflicts.items()])
            msg += "\n\nDo you want to continue?"
            if not messagebox.askyesno("Extension Conflict", msg):
                return
        self.file_categories[new_name] = ext_list
        # Save description for user categories
        if not hasattr(self, "user_category_desc"):
            self.user_category_desc = {}
        if desc:
            self.user_category_desc[new_name] = desc
        elif new_name in self.user_category_desc:
            del self.user_category_desc[new_name]
        save_categories(self.file_categories)
        self.extension_to_category = build_extension_map(self.file_categories)
        self.refresh_category_listbox()
        self.clear_category_entries()  # Clear after successful add
        self.log(f"Added new category '{new_name}' with extensions: {', '.join(ext_list)}")
        self.status_var.set(f"Added category '{new_name}'")
        if new_name not in self.category_counts:
            self.category_counts[new_name] = 0
        self._draw_pie_chart()
    def _should_show_welcome(self):
        # Returns True if welcome dialog should be shown (first launch)
        try:
            return not os.path.isfile(self.WELCOME_SHOWN_FILE)
        except Exception:
            return True

    def _add_help_menu(self):
        # Add a Help menu to the app window to open the welcome dialog
        if hasattr(self, 'menu_bar'):
            return  # Already added
        self.menu_bar = tk.Menu(self)
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Welcome / How to Use", command=self.show_welcome_dialog)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=self.menu_bar)

    def __init__(self):
        TkinterDnD.Tk.__init__(self)
        # Always use SF Pro Display for all ttk widgets, regardless of theme
        self.style = ttkb.Style("cosmo")
        self._set_global_fonts()
        # --- Set appico.ico as window and taskbar icon ---
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_ico = os.path.join(base_dir, "appico.ico")
            if os.path.exists(icon_ico):
                self.wm_iconbitmap(icon_ico)
                # Only set iconphoto if the file is a supported format for PhotoImage (not .ico)
                # If you have a .png version of the icon, use it here:
        except Exception as e:
            print(f"Warning: Could not set iconphoto: {e}")
    def __init__(self):
        TkinterDnD.Tk.__init__(self)
        # --- SETTINGS ---
        self.operations = {
            "Organize all files in a folder": 1,
            "Organize a single file": 2,
            "Organize all folders in a folder": 3,
            "Organize all folders in a folder (A-Z)": 4,
            "Organize everything in a folder": 5,
            "Organize a single folder": 6,
            "Organize a single folder (A-Z)": 7
        }
        self.settings = self.load_settings()
        # Always use SF Pro Display for all ttk widgets, regardless of theme
        self.style = ttkb.Style("cosmo")
        self._set_global_fonts()
        # --- Set appico.ico as window and taskbar icon ---
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_ico = os.path.join(base_dir, "appico.ico")
            if os.path.exists(icon_ico):
                self.wm_iconbitmap(icon_ico)
                # Only set iconphoto if the file is a supported format for PhotoImage (not .ico)
                # If you have a .png version of the icon, use it here:
        except Exception as e:
            print(f"Warning: Could not set iconphoto: {e}")
            print("Warning: appico.ico not found in script directory.")
            print(f"Warning: Could not set window icon: {e}")
        self.title("Organizicate (v0.9.9.1)")
        self.geometry("1128x895") 
        self.resizable(False, False)  # Make window resizable and maximizable

        # Set ttk.Button font to SF Pro Display for all themes
        self.button_style = "primary.TButton"  # or another available style, e.g., "success.TButton"
        self.style.configure(self.button_style, font=("SF Pro Display", 11))

        self.action_queue = queue.Queue()
        self.operation_thread = None
        self.after(200, self.process_action_queue)

        # Load categories (default + user added)
        self.file_categories = load_categories()
        self.extension_to_category = build_extension_map(self.file_categories)

        # Track which categories are default (cannot edit/delete)
        self.default_categories = set(default_file_categories.keys())

        # Load disabled categories
        self.disabled_categories = load_disabled_categories()

        # Debug info
        print(f"Loaded {len(self.file_categories)} categories")
        print(f"Default categories: {len(self.default_categories)}")
        print(f"First few categories: {list(self.file_categories.keys())[:5]}")

        self.undo_stack = []  # For undo last action
        self.tray_icon = None
        self.withdrawn_for_tray = False

        self.recent_folders = []
        # Exclusions: store as set for fast lookup
        self.excluded_paths = set()
        # New theme support
        self.available_themes = list(ttkb.Style().theme_names())
        self.current_theme = tk.StringVar(value="cosmo")
        self.create_widgets()
        self.refresh_category_listbox()
        # DND support
        self._setup_dnd()  # <-- DnD setup
        # Add DnD tooltip to main window
        # For tray support

        # Custom quit dialog and menu bar
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._add_help_menu()
        self._add_settings_menu()

        # Show welcome dialog only on first launch
        if self._should_show_welcome():
            self.after(400, self.show_welcome_dialog)
    def confirm_quit_dialog(self):
        """Show a dialog with 'Minimize to tray' and 'Quit' options."""
        dialog = tk.Toplevel(self)
        dialog.title("Confirm Quit")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        # Set icon
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_ico = os.path.join(base_dir, "appico.ico")
            if os.path.exists(icon_ico):
                dialog.wm_iconbitmap(icon_ico)
        except Exception:
            pass
        self._center_window(dialog, 320, 120)
        label = ttk.Label(dialog, text="Are you sure you want to quit?", font=("SF Pro Display", 12))
        label.pack(pady=(18, 12), padx=18)
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=(0, 12))
        def do_minimize():
            dialog.destroy()
            self.minimize_to_tray()
        def do_quit():
            dialog.destroy()
            self.destroy()
        min_btn = ttk.Button(btn_frame, text="Minimize to tray", command=do_minimize, style=self.button_style)
        min_btn.pack(side="left", padx=(0, 12))
        quit_btn = ttk.Button(btn_frame, text="Quit", command=do_quit, style=self.button_style)
        quit_btn.pack(side="left")
        dialog.bind("<Escape>", lambda e: dialog.destroy())
    def show_exclusions_window(self):
        """Show the exclusions window, centered and with app icon."""
        dialog = tk.Toplevel(self)
        dialog.title("Exclusions")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        # Set icon
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_ico = os.path.join(base_dir, "appico.ico")
            if os.path.exists(icon_ico):
                dialog.wm_iconbitmap(icon_ico)
        except Exception:
            pass
        self._center_window(dialog, 420, 320)
        # ...existing code for exclusions window content...
        # You should move your exclusions window content here.

    def toggle_exclusion_window(self):
        """Open the exclusions window (centered and with icon)."""
        self.show_exclusions_window()
        # Keyboard shortcuts
        self.bind_all("<Control-n>", lambda e: self.add_cat_btn.invoke())
        self.bind_all("<Control-s>", lambda e: self.update_cat_btn.invoke())
        self.bind_all("<Delete>", lambda e: self.delete_cat_btn.invoke())
        self.bind_all("<Escape>", lambda e: self.clear_category_entries())
        # Double-click on listbox
        self.category_listbox.bind("<Double-Button-1>", self.on_category_double_click)

        self.log_to_file("Organizicate started.")

    def _set_global_fonts(self):
        """Force SF Pro Display as the font for all ttk and Tkinter widgets, for all themes and all button variants."""
        import tkinter.font as tkfont
        # Set default font for all Tk widgets
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.config(family="SF Pro Display", size=11)
        self.option_add("*Font", ("SF Pro Display", 11))
        # Set ttk styles for all major widget types and all button variants
        style_names = [
            "TButton", "primary.TButton", "secondary.TButton", "success.TButton", "info.TButton", "warning.TButton", "danger.TButton", "outline.TButton",
            "TLabel", "TEntry", "TCombobox", "TCheckbutton", "TRadiobutton", "TMenubutton", "TNotebook.Tab"
        ]
        for style_name in style_names:
            self.style.configure(style_name, font=("SF Pro Display", 11))
        # Force label frame fonts to 12pt for all themes
        self.style.configure("TLabelframe", font=("SF Pro Display", 11))
        self.style.configure("TLabelframe.Label", font=("SF Pro Display", 11))
        self.style.configure("OutputLog.TLabelframe.Label", font=("SF Pro Display", 11, "normal"))
        self.style.configure("ManageCategories.TLabelframe.Label", font=("SF Pro Display", 11, "normal"))

    def on_theme_change(self, event=None):
        """Handle theme change and re-apply SF Pro Display font for all widgets."""
        selected_theme = self.current_theme.get()
        self.style.theme_use(selected_theme)
        self._set_global_fonts()

    def is_category_disabled(self, cat_name):
        return cat_name in self.disabled_categories

    def set_category_disabled(self, cat_name, disabled=True):
        if disabled:
            self.disabled_categories.add(cat_name)
        else:
            self.disabled_categories.discard(cat_name)
        save_disabled_categories(self.disabled_categories)
        self.refresh_category_listbox()

    def toggle_disable_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        cat_name_with_suffix = self.category_listbox.get(idx)
        cat_name = cat_name_with_suffix.replace(" (default)", "").replace("   [ X ]  ", "")
        if self.is_category_disabled(cat_name):
            self.set_category_disabled(cat_name, False)
            self.status_var.set(f"Enabled category '{cat_name}'")
            self.log(f"Enabled category '{cat_name}'")
        else:
            self.set_category_disabled(cat_name, True)
            self.status_var.set(f"Disabled category '{cat_name}'")
            self.log(f"Disabled category '{cat_name}'")

    def _setup_dnd(self):
        """Enable drag-and-drop for the path entry and window."""
        try:
            import tkinterdnd2 as tkdnd  # type: ignore
            self.tk.call('package', 'require', 'tkdnd')
            self.dnd_enabled = True
        except Exception:
            self.dnd_enabled = False
            return
        # Register DND for path_entry
        try:
            self.path_entry.drop_target_register(tkdnd.DND_FILES)
            self.path_entry.dnd_bind('<<Drop>>', self._on_dnd_path)
            # Visual feedback for drag enter/leave
            self.path_entry.dnd_bind('<<DragEnter>>', lambda e: self.path_entry.config(background="#e0ffe0"))
            self.path_entry.dnd_bind('<<DragLeave>>', lambda e: self.path_entry.config(background="white"))
            self.path_entry.dnd_bind('<<Drop>>', lambda e: self.path_entry.config(background="white"))
        except Exception:
            pass
        # Register DND for main window (optional)
        try:
            self.drop_target_register(tkdnd.DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_dnd_path)
        except Exception:
            pass

    def _on_dnd_path(self, event):
        """Handle file/folder drop on path entry or window."""
        try:
            dropped = event.data
            # Remove curly braces if present (Windows)
            if dropped.startswith('{') and dropped.endswith('}'):
                dropped = dropped[1:-1]
            # Support multiple files/folders
            paths = self.tk.splitlist(dropped)
            if paths:
                path = paths[0]
                self.path_entry.delete(0, 'end')
                self.path_entry.insert(0, path)
                if os.path.isdir(path):
                    self.add_recent_folder(path)
                elif os.path.isfile(path):
                    self.add_recent_folder(os.path.dirname(path))
        except Exception as e:
            messagebox.showerror("DND Error", f"Failed to process dropped item: {e}")

    def on_recent_folder_selected(self, event):
        """Set the path entry to the selected recent folder."""
        selected = self.recent_folders_var.get()
        if selected:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, selected)

    def reload_categories(self):
        self.file_categories = load_categories()
        self.extension_to_category = build_extension_map(self.file_categories)
        self.refresh_category_listbox()
        self.status_var.set("Categories reloaded.")
        self.log("Categories reloaded from disk.")

        # Force refresh the category listbox after UI is created
        self.after(100, self.refresh_category_listbox)

    def create_widgets(self):
        # Main frame with more padding
        main_frame = ttk.Frame(self, padding=(16, 16, 16, 8))
        main_frame.pack(fill='both', expand=True)

        # --- Top Controls: Operation and Theme ---
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(top_frame, text="Organize:", font=("SF Pro Display", 12, "normal")).pack(side='left', padx=(0, 8))
        self.operations = {
            "Organize all files in a folder": 1,
            "Organize a single file": 2,
            "Organize all folders in a folder": 3,
            "Organize all folders in a folder (A-Z)": 4,
            "Organize everything in a folder": 5,
            "Organize a single folder": 6,
            "Organize a single folder (A-Z)": 7
        }
        self.operation_var = tk.StringVar()
        self.operation_dropdown = ttk.Combobox(top_frame, values=list(self.operations.keys()), state="readonly", width=32, textvariable=self.operation_var)
        self.operation_dropdown.pack(side='left', padx=(0, 16))
        # Set default operation from settings
        default_op = self.settings.get("default_operation", list(self.operations.keys())[0])
        if default_op in self.operations:
            self.operation_dropdown.set(default_op)
        else:
            self.operation_dropdown.current(0)
        ttk.Label(top_frame, text="Theme:").pack(side='left', padx=(0, 6))
        self.theme_combo = ttk.Combobox(top_frame, values=self.available_themes, state="readonly", width=14, textvariable=self.current_theme)
        self.theme_combo.pack(side='left')
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
        ToolTip(self.theme_combo, "Change the application theme")

        # --- Path Input Section ---
        path_frame = ttk.LabelFrame(main_frame, text="", padding=(12, 8))
        path_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(path_frame, text="Path:").grid(row=0, column=0, sticky='w', padx=(0, 6))
        self.path_entry = ttk.Entry(path_frame, width=48)
        self.path_entry.grid(row=0, column=1, sticky='ew', padx=(0, 6))
        ToolTip(self.path_entry, "Enter the full path to a file or folder\n(You can drag and drop the wanted file or folder here)")
        path_frame.columnconfigure(1, weight=1)
        self.recent_folders_var = tk.StringVar(value="")
        self.recent_folders_combo = ttk.Combobox(path_frame, textvariable=self.recent_folders_var, width=28, state="readonly", values=[])
        self.recent_folders_combo.grid(row=0, column=2, padx=(0, 6))
        self.recent_folders_combo.bind("<<ComboboxSelected>>", self.on_recent_folder_selected)
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_path, style=self.button_style)
        browse_btn.grid(row=0, column=3, padx=(0, 6))
        ToolTip(browse_btn, "Browse for a file or folder")
        about_btn = ttk.Button(path_frame, text="About", command=self.show_about, style=self.button_style)
        about_btn.grid(row=0, column=4, padx=(0, 6))
        ToolTip(about_btn, "About Organizicate")
        btn_exclude = ttk.Button(path_frame, text="Exclusions", command=self.toggle_exclusion_window, style=self.button_style)
        btn_exclude.grid(row=0, column=5)

        # --- Main Action Buttons ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(0, 10))
        run_btn = ttk.Button(btn_frame, text="Organize", command=self.run_operation, style=self.button_style)
        run_btn.pack(side='left', padx=(0, 8))
        ToolTip(run_btn, "Run the selected organization operation")
        clear_btn = ttk.Button(btn_frame, text="Clear Log", command=self.clear_output, style=self.button_style)
        clear_btn.pack(side='left', padx=(0, 8))
        ToolTip(clear_btn, "Clear the output log")
        self.undo_btn = ttk.Button(btn_frame, text="Undo", command=self.undo_last_action, style=self.button_style)
        self.undo_btn.pack(side='left', padx=(0, 8))
        ToolTip(self.undo_btn, "Undo the last file/folder move operation (multiple undos supported, EXPIREMENTAL with folders.)")
        self.undo_btn.config(state='disabled')
        export_btn = ttk.Button(btn_frame, text="Export Categories", command=self.export_categories, style=self.button_style)
        export_btn.pack(side='left', padx=(0, 8))
        ToolTip(export_btn, "Export user categories to a file")
        import_btn = ttk.Button(btn_frame, text="Import Categories", command=self.import_categories, style=self.button_style)
        import_btn.pack(side='left', padx=(0, 8))
        ToolTip(import_btn, "Import user categories from a file")
        # Show Changes button
        self.show_changes_btn = ttk.Button(btn_frame, text="Show Changes", command=self.show_changes, style=self.button_style)
        self.show_changes_btn.pack(side='left', padx=(0, 8))
        ToolTip(self.show_changes_btn, "Open the last organized folder or file in Explorer")
        self.show_changes_btn.config(state='disabled')

        # --- Output Log Section + Pie Chart ---
        self.apply_custom_label_styles()
        output_frame = ttk.LabelFrame(main_frame, text="Output Log", padding=(11, 8))
        output_frame.configure(style="OutputLog.TLabelframe")
        output_frame.pack(fill='both', expand=False, pady=(0, 10))
        # Output log on the left, pie chart on the right
        log_chart_frame = ttk.Frame(output_frame)
        log_chart_frame.pack(fill='both', expand=True)
        self.output_text = scrolledtext.ScrolledText(
            log_chart_frame,
            width=87,
            height=12,
            font=(self.settings.get("output_log_font", "Fira Code"), self.settings.get("output_log_font_size", 10)),
            state='disabled')
        # Pie chart toggle
        if self.settings.get("show_pie_chart", True):
            self.output_text.pack(side='left', fill='both', expand=False)
            self._init_pie_chart(log_chart_frame)
        else:
            self.output_text.pack(side='left', fill='both', expand=True)

        # --- Category Manager Section ---
        cat_frame = ttk.LabelFrame(main_frame, text="Manage Categories", padding=(11, 8))
        cat_frame.configure(style="ManageCategories.TLabelframe")
        cat_frame.pack(fill='both', expand=True)
        cat_frame.columnconfigure(0, weight=1)
        cat_frame.columnconfigure(1, weight=2)
        cat_frame.rowconfigure(0, weight=1)

        # --- Left: Category Listbox ---
        listbox_frame = ttk.Frame(cat_frame)
        listbox_frame.grid(row=0, column=0, sticky='n', padx=(0, 12), pady=(0, 4))
        # Do not set rowconfigure weight for fixed height
        listbox_frame.columnconfigure(0, weight=1)
        # Set fixed number of rows (e.g., 12)
        self.category_listbox = tk.Listbox(listbox_frame, width=28, height=15)
        self.category_listbox.grid(row=0, column=0, sticky='n')
        self.category_listbox.bind("<<ListboxSelect>>", self.on_category_select)
        ToolTip(self.category_listbox, "List of categories (double-click to edit)")
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.category_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.category_listbox.config(yscrollcommand=scrollbar.set)

        # --- Right: Category Controls ---
        controls_frame = ttk.Frame(cat_frame)
        controls_frame.grid(row=0, column=1, sticky='nsew')
        controls_frame.columnconfigure(0, weight=1)

        # Search/Filter
        search_frame = ttk.Frame(controls_frame)
        search_frame.grid(row=0, column=0, sticky='ew', pady=(0, 6))
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=(0, 4))
        self.cat_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.cat_search_var, width=20)
        search_entry.pack(side='left', padx=(0, 4))
        ToolTip(search_entry, "Type to filter categories")
        self.cat_search_var.trace_add("write", lambda *a: self.refresh_category_listbox())
        clear_btn = ttk.Button(search_frame, text="X", width=2, command=lambda: self.cat_search_var.set(""), style=self.button_style)
        clear_btn.pack(side='left')
        ToolTip(clear_btn, "Clear search")

        # Category Name
        ttk.Label(controls_frame, text="Category Name:").grid(row=1, column=0, sticky='w', pady=(0, 2))
        self.cat_name_var = tk.StringVar()
        self.cat_name_entry = ttk.Entry(controls_frame, textvariable=self.cat_name_var, width=40)
        self.cat_name_entry.grid(row=2, column=0, sticky='ew', pady=(0, 6))
        ToolTip(self.cat_name_entry, "Enter or edit the category name")

        # Extensions
        ttk.Label(controls_frame, text="Extensions (comma separated, with dot):").grid(row=3, column=0, sticky='w', pady=(0, 2))
        self.cat_ext_var = tk.StringVar()
        self.cat_ext_entry = ttk.Entry(controls_frame, textvariable=self.cat_ext_var, width=40)
        self.cat_ext_entry.grid(row=4, column=0, sticky='ew', pady=(0, 6))
        ToolTip(self.cat_ext_entry, "Enter extensions, e.g. .txt, .pdf")

        # Description
        ttk.Label(controls_frame, text="Description (optional):").grid(row=5, column=0, sticky='w', pady=(0, 2))
        self.cat_desc_var = tk.StringVar()
        self.cat_desc_entry = ttk.Entry(controls_frame, textvariable=self.cat_desc_var, width=40)
        self.cat_desc_entry.grid(row=6, column=0, sticky='ew', pady=(0, 6))
        ToolTip(self.cat_desc_entry, "Optional description for user categories")

        # Extension count
        self.ext_count_var = tk.StringVar(value="")
        self.ext_count_label = ttk.Label(controls_frame, textvariable=self.ext_count_var, foreground="gray")
        self.ext_count_label.grid(row=7, column=0, sticky='w', pady=(0, 6))

        # Category Control Buttons
        btn_cat_frame = ttk.Frame(controls_frame)
        btn_cat_frame.grid(row=8, column=0, sticky='ew', pady=(0, 2))
        self.add_cat_btn = ttk.Button(btn_cat_frame, text="Add New Category", command=self.add_category, style=self.button_style)
        self.add_cat_btn.pack(side='left', padx=(0, 6))
        ToolTip(self.add_cat_btn, "Add a new user category (Ctrl+N)")
        self.update_cat_btn = ttk.Button(btn_cat_frame, text="Update Category", command=self.update_category, state='disabled', style=self.button_style)
        self.update_cat_btn.pack(side='left', padx=(0, 6))
        ToolTip(self.update_cat_btn, "Update the selected category (Ctrl+S)")
        self.delete_cat_btn = ttk.Button(btn_cat_frame, text="Delete Category", command=self.delete_category, state='disabled', style=self.button_style)
        self.delete_cat_btn.pack(side='left', padx=(0, 6))
        ToolTip(self.delete_cat_btn, "Delete the selected user category (Del)")
        self.copy_ext_btn = ttk.Button(btn_cat_frame, text="Copy Ext", command=self.copy_extensions, state='disabled', style=self.button_style)
        self.copy_ext_btn.pack(side='left', padx=(0, 6))
        ToolTip(self.copy_ext_btn, "Copy extensions to clipboard")
        self.reset_cat_btn = ttk.Button(btn_cat_frame, text="Reset Categories", command=self.reset_categories, style=self.button_style)
        self.reset_cat_btn.pack(side='left', padx=(0, 6))
        ToolTip(self.reset_cat_btn, "Remove all user-made categories and restore defaults")
        self.disable_cat_btn = ttk.Button(btn_cat_frame, text="Disable Category", command=self.toggle_disable_category, style=self.button_style, state='disabled')
        self.disable_cat_btn.pack(side='left')
        ToolTip(self.disable_cat_btn, "Disable or enable the selected category")

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor='w')
        status_bar.pack(side='bottom', fill='x')

    def refresh_category_listbox(self):
        """Refresh the category listbox with all categories, filtered by search, and add a fake entry at the bottom."""
        self.category_listbox.delete(0, 'end')
        if not self.file_categories:
            print("Warning: No categories found!")
            # Still add the fake entry even if no categories
            self.category_listbox.insert('end', "Select category then double-click name.")
            return
        filter_text = self.cat_search_var.get().strip().lower() if hasattr(self, 'cat_search_var') else ""
        cats_sorted = sorted(self.file_categories.keys())
        count_inserted = 0
        for cat in cats_sorted:
            if filter_text and filter_text not in cat.lower():
                continue
            suffix = " (default)" if cat in self.default_categories else ""
            if self.is_category_disabled(cat):
                suffix += "   [ X ]  "
            self.category_listbox.insert('end', cat + suffix)
            count_inserted += 1
        # Always add the fake entry at the bottom
        self.category_listbox.insert('end', "Select category then double-click name.")
        print(f"Refreshed listbox with {count_inserted} categories (filtered: {filter_text}), plus fake entry at bottom.")

    def parse_extensions(self, ext_string):
        # Split by comma and clean
        exts = [e.strip().lower() if e.strip().startswith('.') else '.' + e.strip().lower() for e in ext_string.split(',') if e.strip()]
        # Allow extensions with multiple dots (e.g., .tar.gz)
        valid_exts = []
        for e in exts:
            if len(e) >= 2 and e[0] == '.' and all(c.isalnum() or c == '.' for c in e[1:]):
                valid_exts.append(e)
        return valid_exts

    def on_category_select(self, event):
        sel = self.category_listbox.curselection()
        if not sel:
            self.cat_name_var.set("")
            self.cat_ext_var.set("")
            self.cat_desc_var.set("")
            self.ext_count_var.set("")
            self.update_cat_btn.config(state='disabled')
            self.delete_cat_btn.config(state='disabled')
            self.add_cat_btn.config(state='normal')
            self.copy_ext_btn.config(state='disabled')
            self.cat_ext_entry.config(state='normal')
            return

        idx = sel[0]
        entry_text = self.category_listbox.get(idx)
        fake_entry = "Select category then double-click name."
        cat_name = entry_text.replace(" (default)", "").replace("   [ X ]  ", "")
        self.cat_name_var.set(cat_name)
        exts = self.file_categories.get(cat_name, [])
        self.cat_ext_var.set(", ".join(exts))
        self.ext_count_var.set(f"Extension count: {len(exts)}")
        self.copy_ext_btn.config(state='normal')
        # Disable delete button for default categories and fake entry
        if cat_name in self.default_categories or entry_text.strip() == fake_entry:
            self.cat_desc_var.set("")
            self.cat_desc_entry.config(state='disabled')
            self.update_cat_btn.config(state='normal')
            self.delete_cat_btn.config(state='disabled')
            self.add_cat_btn.config(state='normal')
            self.cat_ext_entry.config(state='disabled')
            ToolTip(self.update_cat_btn, "Rename default categories (extensions not editable)")
        else:
            self.cat_desc_entry.config(state='normal')
            self.cat_desc_var.set(getattr(self, "user_category_desc", {}).get(cat_name, ""))
            self.update_cat_btn.config(state='normal')
            self.delete_cat_btn.config(state='normal')
            self.add_cat_btn.config(state='disabled')
            self.cat_ext_entry.config(state='normal')
        # Enable/disable the disable/enable button
        if hasattr(self, 'disable_cat_btn'):
            if self.is_category_disabled(cat_name):
                self.disable_cat_btn.config(text="Enable Category", state='normal')
            else:
                self.disable_cat_btn.config(text="Disable Category", state='normal')

    def on_category_double_click(self, event):
        sel = self.category_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        entry_text = self.category_listbox.get(idx)
        # If fake entry is double-clicked, clear fields and focus name entry
        if entry_text.strip() == "Select category then double-click name.":
            self.clear_category_entries()
            self.cat_name_entry.focus_set()
            return
        # Otherwise, focus and select the name entry for editing
        self.cat_name_entry.focus_set()
        self.cat_name_entry.selection_range(0, tk.END)

    def update_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "No category selected to update.")
            return
        idx = sel[0]
        old_name_with_suffix = self.category_listbox.get(idx)
        old_name = old_name_with_suffix.replace(" (default)", "")
        new_name = self.cat_name_var.get().strip()
        exts = self.cat_ext_var.get().strip()
        desc = self.cat_desc_var.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Category name cannot be empty.")
            return
        if new_name != old_name and new_name in self.file_categories:
            messagebox.showerror("Error", f"Category '{new_name}' already exists.")
            return
        if old_name in self.default_categories:
            if new_name == old_name:
                messagebox.showinfo("Info", "No changes to update.")
                return
            self.file_categories[new_name] = self.file_categories.pop(old_name)
            self.default_categories.remove(old_name)
            self.default_categories.add(new_name)
            self.log(f"Renamed default category '{old_name}' to '{new_name}'")
            self.status_var.set(f"Renamed default category '{new_name}'")
        else:
            ext_list = self.parse_extensions(exts)
            if not ext_list:
                messagebox.showerror("Error", "Please enter at least one valid extension (e.g. .txt).")
                return
            # Category conflict warning (ignore current category)
            conflicts = self._find_extension_conflicts(ext_list, ignore_category=old_name)
            if conflicts:
                msg = "Warning: The following extensions are already assigned to other categories:\n"
                msg += "\n".join([f"{ext}: {cat}" for ext, cat in conflicts.items()])
                msg += "\n\nDo you want to continue?"
                if not messagebox.askyesno("Extension Conflict", msg):
                    return
            if new_name != old_name:
                self.file_categories.pop(old_name)
                # Move description if exists
                if hasattr(self, "user_category_desc") and old_name in self.user_category_desc:
                    self.user_category_desc[new_name] = self.user_category_desc.pop(old_name)
            self.file_categories[new_name] = ext_list
            # Save description for user categories
            if not hasattr(self, "user_category_desc"):
                self.user_category_desc = {}
            if desc:
                self.user_category_desc[new_name] = desc
            elif new_name in self.user_category_desc:
                del self.user_category_desc[new_name]
            self.log(f"Updated category '{old_name}' to '{new_name}' with extensions: {', '.join(ext_list)}")
            self.status_var.set(f"Updated category '{new_name}'")
        save_categories(self.file_categories)
        self.extension_to_category = build_extension_map(self.file_categories)
        self.refresh_category_listbox()
        self.clear_category_entries()
        if old_name != new_name:
            if old_name in self.category_counts:
                self.category_counts[new_name] = self.category_counts.pop(old_name)
            else:
                self.category_counts[new_name] = 0
        self._draw_pie_chart()

    def delete_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "No category selected to delete.")
            return
        
        idx = sel[0]
        name_with_suffix = self.category_listbox.get(idx)
        name = name_with_suffix.replace(" (default)", "")
        
        if name in self.default_categories:
            messagebox.showerror("Error", "Cannot delete default categories.")
            return
        
        if not self.settings.get("confirm_delete", True) or messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete category '{name}'?"):
            self.file_categories.pop(name, None)
            # Remove description if present
            if hasattr(self, "user_category_desc") and name in self.user_category_desc:
                del self.user_category_desc[name]
            save_categories(self.file_categories)
            self.extension_to_category = build_extension_map(self.file_categories)
            self.refresh_category_listbox()
            self.clear_category_entries()
            self.log(f"Deleted category '{name}'")
            self.status_var.set(f"Deleted category '{name}'")
            if name in self.category_counts:
                del self.category_counts[name]
            self._draw_pie_chart()

    def clear_category_entries(self):
        self.cat_name_var.set("")
        self.cat_ext_var.set("")
        self.cat_desc_var.set("")
        self.ext_count_var.set("")
        self.add_cat_btn.config(state='normal')
        self.update_cat_btn.config(state='disabled')
        self.delete_cat_btn.config(state='disabled')
        self.copy_ext_btn.config(state='disabled')
        self.cat_ext_entry.config(state='normal')
        self.cat_desc_entry.config(state='normal')
        self.category_listbox.selection_clear(0, 'end')

    def browse_path(self):
        op = self.operations[self.operation_var.get()]
        # Operations that require a folder path:
        folder_ops = (1, 3, 4, 5, 6, 7)
        if op in folder_ops:
            folder = filedialog.askdirectory()
            if folder:
                self.path_entry.delete(0, 'end')
                self.path_entry.insert(0, folder)
                self.add_recent_folder(folder)
        elif op == 2:  # Single file
            file = filedialog.askopenfilename()
            if file:
                self.path_entry.delete(0, 'end')
                self.path_entry.insert(0, file)
                folder = os.path.dirname(file)
                self.add_recent_folder(folder)

    def add_recent_folder(self, folder):
        if not hasattr(self, "recent_folders"):
            self.recent_folders = []
        if folder and folder not in self.recent_folders:
            self.recent_folders.insert(0, folder)  # Add to the beginning of the list
            if len(self.recent_folders) > RECENT_ACTIONS_LIMIT:
                self.recent_folders.pop()  # Remove the oldest entry if limit exceeded
            # Update the combobox values
            self.recent_folders_combo['values'] = self.recent_folders

    def clear_output(self):
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.config(state='disabled')
        self.status_var.set("Output cleared.")
        # Enforce output log font
        self.output_text.config(font=(self.settings.get("output_log_font", "Fira Code"), self.settings.get("output_log_font_size", 10)))

    def log_to_file(self, message, level="info"):
        if level == "error":
            logging.error(message)
        elif level == "warning":
            logging.warning(message)
        else:
            logging.info(message)

    def log(self, message):
        self.output_text.config(state='normal')
        self.output_text.insert('end', message + "\n")
        # Enforce max lines
        max_lines = self.settings.get("output_log_max_lines", 500)
        lines = self.output_text.get('1.0', 'end-1c').splitlines()
        if len(lines) > max_lines:
            self.output_text.delete('1.0', f'{len(lines)-max_lines+1}.0')
        self.output_text.see('end')
        self.output_text.config(state='disabled')
        self.log_to_file(message)

    def log_summary(self, count_moved):
        """Log a summary of moved files/folders by category and update pie chart."""
        if not count_moved:
            self.log("No files or folders were moved.")
            return
        summary = "Summary of moved items:\n"
        for cat, count in sorted(count_moved.items()):
            summary += f"  {cat}: {count}\n"
        summary = summary.rstrip("\n")
        self.log(summary)
        # Update pie chart
        self._update_pie_chart(count_moved)
        return summary

    def run_operation(self):
        path = self.path_entry.get().strip()
        if not path:
            messagebox.showerror("Error", "Please enter a valid path.")
            return
        op = self.operations[self.operation_var.get()]
        self.status_var.set("Running operation...")
        self.log(f"Operation: {self.operation_var.get()}")
        self.log(f"Target Path: {path}")

        # Run in background thread to avoid freezing UI
        if self.operation_thread and self.operation_thread.is_alive():
            messagebox.showwarning("Warning", "An operation is already running.")
            return
        def safe_run():
            try:
                if op == 4:
                    self.organize_folders_az(path)
                elif op == 5:
                    self.organize_everything_in_folder(path)
                elif op == 6:
                    self.organize_single_folder_move(path)
                elif op == 7:
                    self.organize_single_folder_az(path)
                else:
                    self._run_operation_thread(op, path)
            except Exception as e:
                self.action_queue.put(("status", "Error occurred."))
                self.action_queue.put(("log", f"Error: {e}"))
                messagebox.showerror("Operation Error", f"An error occurred:\n{e}")
        import threading
        self.operation_thread = threading.Thread(target=safe_run, daemon=True)
        self.operation_thread.start()
    def organize_single_folder_move(self, folder_path):
        """Move a single folder to the 'Folders' folder in its parent directory."""
        if not os.path.isdir(folder_path):
            self.action_queue.put(("log", f"'{folder_path}' is not a valid folder path."))
            self.action_queue.put(("status", "Error occurred."))
            return
        parent = os.path.dirname(folder_path)
        folders_folder = os.path.join(parent, "Folders")
        if not os.path.exists(folders_folder):
            os.makedirs(folders_folder)
        dst = os.path.join(folders_folder, os.path.basename(folder_path))
        if os.path.abspath(folder_path) == os.path.abspath(dst):
            self.action_queue.put(("log", f"'{folder_path}' is already in 'Folders'."))
            self.action_queue.put(("status", "Operation completed."))
            return
        try:
            shutil.move(folder_path, dst)
            # Add to undo stack
            if hasattr(self, 'undo_stack'):
                self.undo_stack.append([(dst, folder_path)])
                if hasattr(self, 'undo_btn'):
                    self.undo_btn.config(state='normal')
            self.action_queue.put(("log", f"Moved folder '{os.path.basename(folder_path)}' to 'Folders'."))
            self.action_queue.put(("status", "Operation completed."))
            self.last_organized_path = dst
            if hasattr(self, 'show_changes_btn'):
                self.show_changes_btn.config(state='normal')
        except Exception as e:
            self.action_queue.put(("log", f"Failed to move folder: {e}"))
            self.action_queue.put(("status", "Error occurred."))

    def organize_single_folder_az(self, folder_path):
        """Move a single folder to a folder named by its first letter in its parent directory."""
        if not os.path.isdir(folder_path):
            self.action_queue.put(("log", f"'{folder_path}' is not a valid folder path."))
            self.action_queue.put(("status", "Error occurred."))
            return
        import string
        parent = os.path.dirname(folder_path)
        folder_name = os.path.basename(folder_path)
        first_char = folder_name[0].upper() if folder_name else '#'
        if first_char not in string.ascii_uppercase:
            first_char = '#'
        letter_folder = os.path.join(parent, first_char)
        if not os.path.exists(letter_folder):
            os.makedirs(letter_folder)
        dst = os.path.join(letter_folder, folder_name)
        if os.path.abspath(folder_path) == os.path.abspath(dst):
            self.action_queue.put(("log", f"'{folder_path}' is already in '{first_char}/'."))
            self.action_queue.put(("status", "Operation completed."))
            return
        try:
            shutil.move(folder_path, dst)
            # Add to undo stack
            if hasattr(self, 'undo_stack'):
                self.undo_stack.append([(dst, folder_path)])
                if hasattr(self, 'undo_btn'):
                    self.undo_btn.config(state='normal')
            self.action_queue.put(("log", f"Moved folder '{folder_name}' to '{first_char}/'."))
            self.action_queue.put(("status", "Operation completed."))
            self.last_organized_path = dst
            if hasattr(self, 'show_changes_btn'):
                self.show_changes_btn.config(state='normal')
        except Exception as e:
            self.action_queue.put(("log", f"Failed to move folder: {e}"))
            self.action_queue.put(("status", "Error occurred."))
    def organize_everything_in_folder(self, folder_path):
        """Organize all folders and all files inside a folder."""
        if not os.path.isdir(folder_path):
            self.action_queue.put(("log", f"'{folder_path}' is not a valid folder path."))
            self.action_queue.put(("status", "Error occurred."))
            return
        # Organize all folders in the folder
        # Capture undo stack size before
        undo_len_before = len(self.undo_stack) if hasattr(self, 'undo_stack') else 0
        self.organize_all_folders_in_folder(folder_path)
        self.organize_single_folder(folder_path)
        # Combine undo ops from both actions if any
        if hasattr(self, 'undo_stack'):
            undo_len_after = len(self.undo_stack)
            if undo_len_after > undo_len_before:
                # Combine all new undo ops into one
                new_ops = []
                for _ in range(undo_len_after - undo_len_before):
                    new_ops = self.undo_stack.pop() + new_ops
                self.undo_stack.append(new_ops)
                if hasattr(self, 'undo_btn'):
                    self.undo_btn.config(state='normal')
        self.action_queue.put(("log", "Organized everything in the folder."))
        self.action_queue.put(("status", "Operation completed."))
        self.last_organized_path = folder_path
        if hasattr(self, 'show_changes_btn'):
            self.show_changes_btn.config(state='normal')

    def organize_folders_az(self, folder_path):
        """Organize all folders in a folder (A-Z), skipping folders named after any category.
        Each folder is moved into a subfolder named by its first letter (A-Z, or # for non-alpha)."""
        import string
        if not os.path.isdir(folder_path):
            self.action_queue.put(("log", f"'{folder_path}' is not a valid folder path."))
            self.action_queue.put(("status", "Error occurred."))
            return
        # Get all category names (user + default)
        category_names = set(self.file_categories.keys())
        for cat, subcats in subcategory_map.items():
            if isinstance(subcats, dict):
                category_names.update(subcats.keys())
        # List all folders in the directory
        all_folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
        # Filter out folders named after any category (case-insensitive)
        filtered_folders = [f for f in all_folders if f.lower() not in {c.lower() for c in category_names}]
        if not filtered_folders:
            self.action_queue.put(("log", "No folders to organize (all are category folders)."))
            self.action_queue.put(("status", "Operation completed."))
            return
        # Sort alphabetically
        filtered_folders.sort(key=lambda x: x.lower())
        count_moved = 0
        undo_ops = []
        for folder in filtered_folders:
            src = os.path.join(folder_path, folder)
            # Determine the first character (A-Z or #)
            first_char = folder[0].upper() if folder else '#'
            if first_char not in string.ascii_uppercase:
                first_char = '#'
            letter_folder = os.path.join(folder_path, first_char)
            if not os.path.exists(letter_folder):
                os.makedirs(letter_folder)
            dst = os.path.join(letter_folder, folder)
            if os.path.abspath(src) == os.path.abspath(dst):
                continue
            try:
                shutil.move(src, dst)
                count_moved += 1
                undo_ops.append((src, dst))
                self.action_queue.put(("log", f"Moved folder '{folder}' to '{first_char}/'."))
            except Exception as e:
                self.action_queue.put(("log", f"Failed to move '{folder}': {e}"))
        if undo_ops:
            self.undo_stack.append(undo_ops)
            # Always enable the Undo button if there are undoable operations
            if hasattr(self, 'undo_btn'):
                self.undo_btn.config(state='normal')
        self.action_queue.put(("log", f"Moved {count_moved} folders to A-Z folders."))
        self.action_queue.put(("status", "Operation completed."))
        self.last_organized_path = folder_path
        if hasattr(self, 'show_changes_btn'):
            self.show_changes_btn.config(state='normal')

    def _run_operation_thread(self, op, path):
        try:
            if op == 1:
                self.organize_single_folder(path)
            elif op == 2:
                self.organize_single_file(path)
            elif op == 3:
                self.organize_all_folders_in_folder(path)
            else:
                self.action_queue.put(("status", "Unknown operation selected."))
                self.action_queue.put(("log", "Unknown operation selected."))
                return
            self.action_queue.put(("status", "Operation completed."))
        except Exception as e:
            self.action_queue.put(("status", "Error occurred."))
            self.action_queue.put(("log", f"Error: {e}"))

    def process_action_queue(self):
        try:
            while True:
                action, msg = self.action_queue.get_nowait()
                if action == "log":
                    self.log(msg)
                elif action == "status":
                    self.status_var.set(msg)
        except queue.Empty:
            pass
        self.after(100, self.process_action_queue)

    # === Organization methods ===

    def get_category_for_file(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        # Find main category
        main_cat = self.extension_to_category.get(ext, "Other")
        # If the category is disabled, treat as "Other"
        if self.is_category_disabled(main_cat):
            main_cat = "Other"
        # Try to find subcategory
        subcat = None
        if main_cat in subcategory_map:
            for sub, ext_list in subcategory_map[main_cat].items():
                if ext in ext_list:
                    subcat = sub
                    break
        return (main_cat, subcat)

    def ensure_folder(self, base_path, folder_name, subcategory=None):
        # If category is Code, 3D & CAD, or Design, nest inside Others
        if folder_name in ("Code", "3D & CAD", "Design"):
            folder_path = os.path.join(base_path, "Others", folder_name)
        else:
            folder_path = os.path.join(base_path, folder_name)
        # Add subcategory as subfolder if present
        if subcategory:
            folder_path = os.path.join(folder_path, subcategory)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def organize_single_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError(f"\n'{folder_path}' is not a valid folder path.")
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            self.log("\nNo files found in the folder.")
            return
        count_moved = defaultdict(int)
        undo_ops = []
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            if self._is_excluded(file_path):
                self.log(f"\nExcluded file '{file_name}'. Skipped.")
                continue
            main_cat, subcat = self.get_category_for_file(file_name)
            # If the file's category is disabled, get_category_for_file returns 'Other'.
            # If the file's true category is disabled, skip it (do not move to 'Other').
            true_cat = self.extension_to_category.get(os.path.splitext(file_name)[1].lower(), "Other")
            if self.is_category_disabled(true_cat):
                self.log(f"\nCategory '{true_cat}' is disabled. '{file_name}' skipped.")
                continue
            if main_cat == "Other" and self.is_category_disabled(main_cat):
                self.log(f"\nCategory 'Other' is disabled. '{file_name}' skipped.")
                continue
            dest_folder = self.ensure_folder(folder_path, main_cat, subcat)
            dst = os.path.join(dest_folder, file_name)
            try:
                shutil.move(file_path, dst)
                self.log(f"\nMoved file '{file_name}' to folder '{main_cat}'{f'/{subcat}' if subcat else ''}.")
                count_moved[f"{main_cat}{f'/{subcat}' if subcat else ''}"] += 1
                undo_ops.append((file_path, dst))
            except PermissionError as e:
                self.log(f"\nPermission denied: '{file_name}'. Skipped. ({e})")
            except Exception as e:
                self.log(f"\nFailed to move '{file_name}': {e}")
        if undo_ops:
            self.undo_stack.append(undo_ops)
            self.undo_btn.config(state='normal')
        self.log_summary(count_moved)
        self.last_organized_path = folder_path
        if hasattr(self, 'show_changes_btn'):
            self.show_changes_btn.config(state='normal')

    def organize_single_file(self, file_path):
        """Organize a single file by moving it into its category folder."""
        folder_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        main_cat, subcat = self.get_category_for_file(file_name)
        true_cat = self.extension_to_category.get(os.path.splitext(file_name)[1].lower(), "Other")
        dest_folder = self.ensure_folder(folder_path, main_cat, subcat)
        dst = os.path.join(dest_folder, file_name)
        if os.path.abspath(file_path) == os.path.abspath(dst):
            self.log(f"\nFile '{file_name}' is already in the correct folder.")
            # Still add the parent folder to recent folders for consistency
            self.add_recent_folder(folder_path)
            self.last_organized_path = dst
            if hasattr(self, 'show_changes_btn'):
                self.show_changes_btn.config(state='normal')
            return
        if self.is_category_disabled(true_cat):
            self.log(f"\nCategory '{true_cat}' is disabled. '{file_name}' skipped.")
            return
        if main_cat == "Other" and self.is_category_disabled(main_cat):
            self.log(f"\nCategory 'Other' is disabled. '{file_name}' skipped.")
            return
        try:
            shutil.move(file_path, dst)
            self.log(f"\nMoved file '{file_name}' to folder '{main_cat}'{f'/{subcat}' if subcat else ''}.")
            self.undo_stack.append([(file_path, dst)])
            self.undo_btn.config(state='normal')
            # Add the parent folder to recent folders
            self.add_recent_folder(folder_path)
            self.last_organized_path = dst
            if hasattr(self, 'show_changes_btn'):
                self.show_changes_btn.config(state='normal')
        except PermissionError as e:
            self.log(f"\nPermission denied: '{file_name}'. Skipped. ({e})")
        except Exception as e:
            self.log(f"\nFailed to move '{file_name}': {e}")
            self.last_organized_path = dst
            if hasattr(self, 'show_changes_btn'):
                self.show_changes_btn.config(state='normal')


    def organize_all_folders_in_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError(f"'{folder_path}' is not a valid folder path.")
        count_moved = 0
        undo_ops = []
        # Get all category names (including subcategories)
        category_names = set(self.file_categories.keys())
        # Add subcategory names
        for cat, subcats in subcategory_map.items():
            if isinstance(subcats, dict):
                category_names.update(subcats.keys())
        folders_folder = os.path.join(folder_path, "Folders")
        if not os.path.exists(folders_folder):
            os.makedirs(folders_folder)
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if self._is_excluded(item_path):
                self.action_queue.put(("log", f"Excluded folder '{item}'. Skipped."))
                continue
            if os.path.isdir(item_path):
                # Don't move the Folders folder itself or any folder named after a category
                if item == "Folders" or item in category_names:
                    continue
                try:
                    os.listdir(item_path)
                except PermissionError as e:
                    self.action_queue.put(("log", f"Permission denied: '{item}'. Skipped. ({e})"))
                    continue
                except Exception as e:
                    self.action_queue.put(("log", f"Failed to access folder '{item}': {e}"))
                    continue
                dst = os.path.join(folders_folder, item)
                if os.path.abspath(item_path) == os.path.abspath(dst):
                    continue
                try:
                    common = os.path.commonpath([os.path.abspath(item_path), os.path.abspath(dst)])
                    if common == os.path.abspath(item_path):
                        continue
                except ValueError:
                    pass
                try:
                    shutil.move(item_path, dst)
                    self.action_queue.put(("log", f"Moved folder '{item}' to 'Folders'."))
                    count_moved += 1
                    undo_ops.append((item_path, dst))
                except PermissionError as e:
                    self.action_queue.put(("log", f"Permission denied: '{item}'. Skipped. ({e})"))
                except Exception as e:
                    self.action_queue.put(("log", f"Failed to move folder '{item}': {e}"))
        if undo_ops:
            self.undo_stack.append(undo_ops)
            self.undo_btn.config(state='normal')
        self.action_queue.put(("log", f"Moved {count_moved} folders to 'Folders'."))
        self.last_organized_path = folder_path
        if hasattr(self, 'show_changes_btn'):
            self.show_changes_btn.config(state='normal')
    def _is_excluded(self, path):
        # Exclude if the absolute path or its normalized version is in the set
        abspath = os.path.abspath(path)
        return abspath in self.excluded_paths or abspath.rstrip(os.sep) in self.excluded_paths

    def get_category_for_folder(self, folder_path):
        """Categorize a folder based on its contents."""
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            return "Empty"
        cat_count = defaultdict(int)
        for file in files:
            cat = self.get_category_for_file(file)
            cat_count[cat] += 1
        if not cat_count:
            return "Other"
        if len(cat_count) == 1:
            return next(iter(cat_count))
        most_common = max(cat_count.items(), key=lambda x: x[1])
        if most_common[1] > len(files) // 2:
            return most_common[0]
        return "Mixed"

    # --- Export/Import Categories ---
    def export_categories(self):
        user_categories = {cat: exts for cat, exts in self.file_categories.items() if cat not in default_file_categories}
        if not user_categories:
            messagebox.showinfo("Export Categories", "No user categories to export.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Export Categories")
        if file:
            try:
                with open(file, "w") as f:
                    json.dump(user_categories, f, indent=2)
                self.status_var.set("Categories exported.")
                self.log(f"Exported user categories to {file}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")

    def import_categories(self):
        file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Import Categories")
        if file:
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Invalid format")
                # Merge, skip conflicts
                added = 0
                for cat, exts in data.items():
                    if cat not in self.file_categories:
                        self.file_categories[cat] = exts
                        added += 1
                save_categories(self.file_categories)
                self.extension_to_category = build_extension_map(self.file_categories)
                self.refresh_category_listbox()
                self.status_var.set(f"Imported {added} categories.")
                self.log(f"Imported {added} categories from {file}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import: {e}")

    # --- Undo Last Action ---
    def undo_last_action(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "No actions to undo.")
            self.undo_btn.config(state='disabled')
            return
        undo_ops = self.undo_stack.pop()
        errors = []
        for src, dst in reversed(undo_ops):
            try:
                # Move back from dst to src
                if os.path.exists(dst):
                    shutil.move(dst, src)
                    self.log(f"Undo: moved '{os.path.basename(dst)}' back to '{os.path.dirname(src)}'")
                else:
                    errors.append(f"File not found: {dst}")
            except Exception as e:
                errors.append(f"Failed to undo move for '{dst}': {e}")
        if errors:
            self.log("\n".join(errors))
        if not self.undo_stack:
            self.undo_btn.config(state='disabled')
        else:
            self.undo_btn.config(state='normal')
        self.status_var.set("Undo completed.")

    # --- System Tray Minimization ---
    def minimize_to_tray(self):
        if not (pystray and Image):
            self.destroy()
            return
        self.withdrawn_for_tray = True
        self.withdraw()
        # Use get_resource_path to find appico.png
        # Helper to get resource path for tray icon (works for PyInstaller and normal run)
        def get_resource_path(filename):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, filename)
            return os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)
        icon_png = get_resource_path("appico.png")
        if not os.path.exists(icon_png):
            print("Warning: appico.png not found for tray icon.")
            self.destroy()
            return
        image = Image.open(icon_png)
        menu = pystray.Menu(
            pystray.MenuItem('Restore', self.restore_from_tray),
            pystray.MenuItem('Exit', self.exit_from_tray)
        )
        self.tray_icon = pystray.Icon("Organizicate", image, "Organizicate", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self._restore_window()

    def _restore_window(self):
        self.deiconify()
        self.withdrawn_for_tray = False
        self.lift()
        self.focus_force()

    def exit_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.destroy()

    def destroy(self):
        super().destroy()

    def copy_extensions(self):
        """Copy the extensions of the selected category to the clipboard."""
        sel = self.category_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        cat_name_with_suffix = self.category_listbox.get(idx)
        cat_name = cat_name_with_suffix.replace(" (default)", "")
        exts = self.file_categories.get(cat_name, [])
        ext_str = ", ".join(exts)
        self.clipboard_clear()
        self.clipboard_append(ext_str)
        self.status_var.set(f"Copied extensions for '{cat_name}' to clipboard.")

    def show_about(self):
        import sys, platform, os
        # Prevent multiple About windows
        if hasattr(self, '_about_win') and self._about_win.winfo_exists():
            self._about_win.lift()
            return
        width, height = 600, 520
        about_win = tk.Toplevel(self)
        # Set appico.ico as icon for About window only
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_ico = os.path.join(base_dir, "appico.ico")
            if os.path.exists(icon_ico):
                about_win.iconbitmap(icon_ico)
        except Exception as e:
            print(f"Warning: Could not set About window icon: {e}")
        self._about_win = about_win
        about_win.resizable(False, False)
        about_win.grab_set()
        about_win.title("About Organizicate")
        frame = ttk.Frame(about_win, padding=(40, 32, 40, 32))
        frame.pack(fill='both', expand=True)

        # App name and logo
        app_name = ttk.Label(frame, text="Organizicate", font=("SF Pro Display", 32, "bold"))
        app_name.pack(pady=(0, 6))
        version = ttk.Label(frame, text="Beta v0.9.9.1", font=("SF Pro Display", 14, "bold"), foreground="#2563eb")
        version.pack(pady=(0, 18))

        # Divider
        divider1 = ttk.Separator(frame, orient='horizontal')
        divider1.pack(fill='x', pady=(0, 18))

        # Description
        desc = ttk.Label(
            frame,
            text="A modern, customizable file/folder organizer for Windows.\n\nOrganizicate helps you quickly sort, categorize, and manage your files and folders with ease.",
            font=("SF Pro Display", 13),
            justify="center",
            wraplength=480
        )
        desc.pack(pady=(0, 18))

        # Author
        author = ttk.Label(frame, text="Developed by @thatAmok", font=("SF Pro Display", 11, "normal"), foreground="#888")
        author.pack(pady=(0, 18))

        # Divider
        divider2 = ttk.Separator(frame, orient='horizontal')
        divider2.pack(fill='x', pady=(0, 18))

        # Technical info (2 columns)
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill='x', pady=(0, 10))
        left_info = [
            f"Python: {platform.python_version()}",
            f"Platform: {platform.system()} {platform.release()}",
            f"Theme: {self.current_theme.get() if hasattr(self, 'current_theme') else 'N/A'}",
            f"Drag-and-drop: {'Enabled' if getattr(self, 'dnd_enabled', False) else 'Disabled'}",
            f"Threading: {'Enabled' if hasattr(self, 'operation_thread') else 'Disabled'}",
        ]
        right_info = [
            f"App: {os.path.abspath(sys.argv[0])}",
            f"Config: {os.path.abspath(CONFIG_FILE)}",
            f"Log: {os.path.abspath(LOG_FILE)}",
            f"Default cats: {len(self.default_categories)}",
            f"User cats: {len([c for c in self.file_categories if c not in self.default_categories])}",
        ]
        left_col = ttk.Frame(info_frame)
        left_col.pack(side='left', anchor='n', expand=True, fill='x', padx=(0, 16))
        right_col = ttk.Frame(info_frame)
        right_col.pack(side='left', anchor='n', expand=True, fill='x')
        for line in left_info:
            ttk.Label(left_col, text=line, font=("SF Pro Display", 10), foreground="#444").pack(anchor='w', pady=1)
        for line in right_info:
            ttk.Label(right_col, text=line, font=("SF Pro Display", 10), foreground="#444").pack(anchor='w', pady=1)

        # Divider
        divider3 = ttk.Separator(frame, orient='horizontal')
        divider3.pack(fill='x', pady=(10, 18))

        # GitHub link
        def open_github(event=None):
            import webbrowser
            webbrowser.open_new("https://github.com/thatAmok/organizicate")
        link = tk.Label(frame, text="GitHub: github.com/thatAmok/organizicate", fg="#2563eb", cursor="hand2", font=("SF Pro Display", 11, "underline"))
        link.pack(pady=(0, 0))
        link.bind("<Button-1>", open_github)

        # Close button
        close_btn = ttk.Button(frame, text="Close", command=about_win.destroy, style=self.button_style)
        close_btn.pack(pady=(28, 0))

        # Center and set size
        self._center_window(about_win, width, height)

    def show_changes(self):
        """Open the last organized folder or file in Explorer."""
        if hasattr(self, 'last_organized_path') and self.last_organized_path:
            import subprocess, os
            path = self.last_organized_path
            if os.path.exists(path):
                if os.path.isdir(path):
                    subprocess.Popen(f'explorer \"{os.path.abspath(path)}\"')
                else:
                    subprocess.Popen(f'explorer /select,\"{os.path.abspath(path)}\"')
            else:
                messagebox.showinfo("Show Changes", "The last organized path no longer exists.")
        else:
            messagebox.showinfo("Show Changes", "No recent organization path to show.")

    def on_theme_change(self, event=None):
        """Handle theme change from the dropdown."""
        selected_theme = self.current_theme.get()
        try:
            ttkb.Style().theme_use(selected_theme)
            self.status_var.set(f"Theme changed to '{selected_theme}'.")
        except Exception as e:
            self.status_var.set(f"Failed to change theme: {e}")

    def reset_categories(self):
        """Remove all user-made categories and restore defaults."""
        if not messagebox.askyesno("Reset Categories", "Are you sure you want to remove all user-made categories? This cannot be undone."):
            return
        # Remove user categories
        self.file_categories = copy.deepcopy(default_file_categories)
        save_categories(self.file_categories)
        self.extension_to_category = build_extension_map(self.file_categories)
        self.refresh_category_listbox()
        self.clear_category_entries()
        self.status_var.set("User categories removed. Defaults restored.")
        self.log("All user-made categories have been removed. Only default categories remain.")
        
    def toggle_exclusion_window(self):
        if hasattr(self, 'exclude_window') and self.exclude_window.winfo_exists():
            self.exclude_window.destroy()
            return

        self.exclude_window = tk.Toplevel(self)
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_ico = os.path.join(base_dir, "appico.ico")
            if os.path.exists(icon_ico):
                self.exclude_window.iconbitmap(icon_ico)
        except Exception as e:
            print(f"Warning: Could not set window icon: {e}")
        self.exclude_window.title("Exclusions")
        self.exclude_window.geometry("715x426")
        self.exclude_window.resizable(False, False)
        self.exclude_window.grab_set()

        frame = ttk.Frame(self.exclude_window, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Exclude Files/Folders from Organizing:", font=("SF Pro Display", 12)).pack(anchor="w")


        # Path entry and browse/add/remove buttons
        path_frame = ttk.Frame(frame)
        path_frame.pack(fill="x", pady=(5, 10))
        self.excl_path_var = tk.StringVar()
        excl_path_entry = ttk.Entry(path_frame, textvariable=self.excl_path_var, width=45)
        excl_path_entry.pack(side="left", fill="x", expand=True)

        # Custom browse: allow multi-file selection and drag-and-drop for folders/files
        def browse_excl():
            # Try to select
            files = filedialog.askopenfilenames(title="Select files or folders to exclude")
            # If user selects files, add them
            if files:
                for path in files:
                    abspath = os.path.abspath(path)
                    current = [self.exclude_listbox.get(i) for i in range(self.exclude_listbox.size())]
                    if abspath not in [os.path.abspath(line.strip()) for line in current if line.strip()]:
                        self.exclude_listbox.insert("end", abspath)
                self.excl_path_var.set("")
        browse_btn = ttk.Button(path_frame, text="Browse & Add", command=browse_excl, style=self.button_style)
        browse_btn.pack(side="left", padx=(5,0))
        ToolTip(browse_btn, "Browse for multiple files (folders: use drag-and-drop)")

        # Enable drag-and-drop for the entry and listbox for both files and folders
        try:
            excl_path_entry.drop_target_register(tkdnd.DND_FILES)
            def on_excl_dnd(event):
                dropped = event.data
                if dropped.startswith('{') and dropped.endswith('}'):
                    dropped = dropped[1:-1]
                paths = self.tk.splitlist(dropped)
                for path in paths:
                    abspath = os.path.abspath(path)
                    current = [self.exclude_listbox.get(i) for i in range(self.exclude_listbox.size())]
                    if abspath not in [os.path.abspath(line.strip()) for line in current if line.strip()]:
                        self.exclude_listbox.insert("end", abspath)
                self.excl_path_var.set("")
            excl_path_entry.dnd_bind('<<Drop>>', on_excl_dnd)
            self.exclude_listbox.drop_target_register(tkdnd.DND_FILES)
            self.exclude_listbox.dnd_bind('<<Drop>>', on_excl_dnd)
        except Exception:
            pass

        def remove_selected_excl():
            # Remove selected items from the Listbox
            selected = list(self.exclude_listbox.curselection())
            for idx in reversed(selected):
                self.exclude_listbox.delete(idx)
        remove_btn = ttk.Button(path_frame, text="Remove", command=remove_selected_excl, style=self.button_style)
        remove_btn.pack(side="left", padx=(5,0))

        self.exclude_listbox = tk.Listbox(frame, height=12, font=("SF Pro Display", 10), selectmode="extended")
        self.exclude_listbox.pack(fill="both", expand=True, pady=10)
        self.exclude_listbox.delete(0, "end")
        if self.excluded_paths:
            for path in sorted(self.excluded_paths):
                self.exclude_listbox.insert("end", path)

        def save_exclusions():
            items = [self.exclude_listbox.get(i) for i in range(self.exclude_listbox.size())]
            self.excluded_paths = set(os.path.abspath(line.strip()) for line in items if line.strip())
            self.exclude_window.destroy()
            self.status_var.set("Exclusions updated.")
            self.log("Excluded paths updated.")

        ttk.Button(frame, text="Save", command=save_exclusions, style=self.button_style).pack(anchor="e", pady=(10, 0))



# NOTE FOR DEVELOPERS:
# If you change or replace the icon file (appico.ico
# and the .spec file before running PyInstaller again. Otherwise, PyInstaller may use a cached/old icon.
# Example:), you MUST delete the 'build' and 'dist' folders,
#   rmdir /s /q build
#   rmdir /s /q dist
#   del organizicate.spec
#   pyinstaller --onefile --windowed --icon=appico.ico organizicate.py

# --- Advanced run block ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Organizicate - Smart file/folder organizer")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--config", type=str, default=CONFIG_FILE, help="Path to config file (default: config.json)")
    args = parser.parse_args()

    if args.config != CONFIG_FILE:
        CONFIG_FILE = args.config

    if args.debug:
        print("Debug mode enabled")
        print(f"Using config file: {CONFIG_FILE}")

    app = OrganizicateBeta()
    if args.debug:
        app.log("Debug mode is ON")
    app.mainloop()
