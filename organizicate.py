import os
import shutil
import json 
import threading
import queue
from tkinter import ttk
import ttkbootstrap as ttkb
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from collections import defaultdict
import copy
from typing import Dict, List
# Add for tray and tooltips
import sys
try:
    import pystray
    from PIL import Image
except ImportError:
    pystray = None
    Image = None

import logging

# Setup logging to file
LOG_FILE = "organizicate.log"
logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

CONFIG_FILE = "config.json"

# Default categories (hardcoded, cannot edit/delete)
default_file_categories = {
    "Documents": [
        # Documents, Spreadsheets, Presentations, eBooks, Markup, Calendar, ContactCards
        '.doc', '.docx', '.pdf', '.txt', '.rtf', '.odt', '.pages', '.tex', '.wpd', '.wps', '.md', '.markdown', '.djvu',
        '.xls', '.xlsx', '.csv', '.ods', '.numbers', '.tsv', '.dif', '.dbf',
        '.ppt', '.pptx', '.odp', '.key', '.pps', '.sldx',
        '.epub', '.mobi', '.azw3', '.fb2', '.ibooks',
        '.rst', '.ical', '.ics', '.vcard', '.vcf', '.mbox', '.eml', '.msg', '.pst', '.ost',
    ],
    "Images": [
        # Images_Raster, Images_Vector, VectorDesign, ImageProjects
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.ico', '.raw', '.cr2', '.nef', '.orf', '.sr2', '.arw', '.dng', '.pef', '.raf',
        '.svg', '.ai', '.eps', '.pdf', '.cdr', '.wmf', '.emf', '.fh', '.sketch',
        '.psd', '.xcf', '.indd', '.kra', '.afdesign', '.psd', '.xcf', '.kra', '.svg', '.ai', '.indd',
    ],
    "Audio": [
        # Audio, AudioProjects
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff', '.alac', '.mid', '.midi', '.ape', '.opus', '.amr', '.dsd',
        '.als', '.flp', '.logicx', '.ptx', '.aup', '.band',
    ],
    "Video": [
        # Video, VideoProjects
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.3gp', '.vob', '.mts', '.m2ts', '.ts', '.rm', '.rmvb', '.divx', '.xvid', '.f4v',
        '.prproj', '.veg', '.aep', '.pproj', '.fcpx', '.mlt', '.drp',
    ],
    "Archives": [
        # Archives, CompressedBackups, Backups
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg', '.cab', '.arj', '.lz', '.lzma', '.apk', '.rpm', '.deb', '.jar', '.vhd', '.vdi',
        '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2', '.txz',
        '.bak', '.tmp', '.old', '.backup', '.swp', '.swo', '.sav', '.bkp',
    ],
    "Code": [
        # Code, Scripts, Web, Docker, Shell, Shaders, ProjectFiles
        '.py', '.js', '.java', '.c', '.cpp', '.cs', '.rb', '.php', '.html', '.css', '.go', '.rs', '.swift', '.kt', '.m', '.pl', '.sh', '.bat', '.cmd', '.ts', '.tsx', '.jsx', '.lua', '.groovy', '.vbs', '.r', '.h', '.hpp', '.asm', '.s', '.d', '.erl',
        '.ps1', '.vbs', '.pl', '.r', '.lua', '.groovy', '.tcl', '.bat', '.cmd', '.sh', '.zsh', '.fish',
        '.css', '.js', '.html', '.php', '.jsp', '.asp', '.aspx', '.cgi', '.pl', '.vue', '.ts', '.tsx', '.jsx', '.json', '.xml', '.yaml', '.yml',
        'Dockerfile', '.dockerignore', '.compose', '.yml', '.yaml',
        '.sh', '.bash', '.zsh', '.csh', '.ksh', '.fish',
        '.glsl', '.hlsl', '.cg', '.fx', '.shader',
        '.sln', '.vcxproj', '.xcodeproj', '.gradle', 'Makefile', 'CMakeLists.txt', '.idea', '.iml', '.project', '.classpath',
    ],
    "System & Apps": [
        # Combined Apps & Games and System
        '.app', '.bat', '.com', '.jar', '.apk', '.bin', '.scr', '.gadget', '.mod', '.pak', '.sav', '.save', '.gam', '.dat', '.nes', '.snes', '.gba', '.gb', '.iso', '.xex', '.x86', '.x64', '.dll',
        '.mcworld', '.mcpack', '.mcaddon', '.mcmeta', '.mctemplate', '.jar', '.dat', '.nbt', '.litemod', '.mod', '.mcfunction',
        '.vmdk', '.vdi', '.vhd', '.vhdx', '.qcow2', '.ova', '.ovf',
        '.ini', '.cfg', '.conf', '.log', '.bat', '.cmd', '.sys', '.dll', '.drv', '.exe', '.msi', '.tmp', '.dat', '.bak', '.drv', '.efi',
        '.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.plist', '.reg', '.desktop',
        '.db', '.sql', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.dbf', '.log', '.ldf', '.ndf', '.bak',
        '.ttf', '.otf', '.woff', '.woff2', '.eot', '.fon', '.fnt', '.pfb', '.pfm', '.afm',
        '.pem', '.crt', '.cer', '.der', '.pfx', '.p12', '.key',
        '.log', '.trace', '.err', '.out',
        '.dat', '.tmp', '.cache', '.bak', '.old', '.save', '.backup', '.ini', '.cfg',
        '.gpg', '.pgp', '.aes', '.enc', '.crypt', '.lock',
        '.srt', '.sub', '.idx', '.ssa', '.ass',
        '.lnk', '.url', '.webloc', '.desktop', '.alias', '.pif', '.scf', '.library-ms', '.folder', '.desklink',
        '.shp', '.shx', '.dbf', '.kml', '.kmz', '.gpx',
    ],
    "Other": [
        # Expanded with more miscellaneous extensions
        '.torrent', '.bak', '.swp', '.swo', '.old', '.backup', '.cache', '.tmp', '.unknown', '.misc', '.zzz', '.foo', '.bar', '.dat', '.bin', '.log', '.err', '.out', '.dmp', '.dump', '.temp', '.random', '.undefined', '.none', '.file', '.stuff', '.miscfile', '.extra', '.spare', '.spurious', '.junk', '.useless', '.zzz', '.zzz2', '.zzz3', '.zzz4', '.zzz5', '.zzz6', '.zzz7', '.zzz8', '.zzz9', '.zzz10',
    ],
    "Design": [
        # New category for design files
        '.psd', '.ai', '.sketch', '.xd', '.fig', '.indd', '.afdesign', '.cdr', '.svg', '.eps', '.pdf', '.xcf', '.kra',
    ],
    "Documents": [
        # New category for learning/education files
        '.epub', '.mobi', '.azw3', '.fb2', '.ibooks', '.pdf', '.djvu', '.md', '.markdown', '.rst', '.txt', '.ppt', '.pptx', '.odp', '.key', '.pps', '.sldx',
    ],
    "3D & CAD": [
        # New category for 3D models and CAD files
        '.obj', '.fbx', '.stl', '.dae', '.3ds', '.blend', '.max', '.skp', '.dwg', '.dxf', '.3mf', '.ply',
    ],
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
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class OrganizicateBeta(ttkb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        # --- Set appicon.ico as window and taskbar icon ---
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_ico = os.path.join(base_dir, "appicon.ico")
            if os.path.exists(icon_ico):
                self.wm_iconbitmap(icon_ico)
                # Only set iconphoto if the file is a supported format for PhotoImage (not .ico)
                # If you have a .png version of the icon, use it here:
                icon_png = os.path.join(base_dir, "appicon.png")
                if os.path.exists(icon_png):
                    try:
                        icon_img = tk.PhotoImage(file=icon_png)
                        self.iconphoto(True, icon_img)
                    except Exception as e:
                        print(f"Warning: Could not set iconphoto: {e}")
            else:
                print("Warning: appicon.ico not found in script directory.")
        except Exception as e:
            print(f"Warning: Could not set window icon: {e}")
        self.title("Organizicate (v0.9.8.1)")
        self.geometry("990x800")  # Set canvas size to 733x785
        self.resizable(False, False)  # Make window resizable and maximizable

        # Set default font for all widgets except the console/output
        default_font = ("SF Pro Display", 12)
        self.option_add("*Font", default_font)
        # Set ttk.Button font to SF Pro Display
        style = ttkb.Style()
        style.configure("TButton", font=("SF Pro Display", 11))
        self.button_style = "TButton"

        self.action_queue = queue.Queue()
        self.operation_thread = None
        self.after(200, self.process_action_queue)

        # Load categories (default + user added)
        self.file_categories = load_categories()
        self.extension_to_category = build_extension_map(self.file_categories)

        # Track which categories are default (cannot edit/delete)
        self.default_categories = set(default_file_categories.keys())

        # Debug info
        print(f"Loaded {len(self.file_categories)} categories")
        print(f"Default categories: {len(self.default_categories)}")
        print(f"First few categories: {list(self.file_categories.keys())[:5]}")

        self.undo_stack = []  # For undo last action
        self.tray_icon = None
        self.withdrawn_for_tray = False

        self.recent_folders = []
        # New theme support
        self.available_themes = list(ttkb.Style().theme_names())
        self.current_theme = tk.StringVar(value="cosmo")
        self.create_widgets()
        self.refresh_category_listbox()
        # DND support
        self._setup_dnd()  # <-- DnD setup
        # Add DnD tooltip to main window
        # For tray support
        if pystray and Image:
            self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        # Keyboard shortcuts
        self.bind_all("<Control-n>", lambda e: self.add_cat_btn.invoke())
        self.bind_all("<Control-s>", lambda e: self.update_cat_btn.invoke())
        self.bind_all("<Delete>", lambda e: self.delete_cat_btn.invoke())
        self.bind_all("<Escape>", lambda e: self.clear_category_entries())
        # Double-click on listbox
        self.category_listbox.bind("<Double-Button-1>", self.on_category_double_click)

        self.log_to_file("Organizicate started.")

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
        selected = self.recent_folders_combo.get()
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
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # --- Operation and Theme Selection (side by side) ---
        op_theme_frame = ttk.Frame(main_frame)
        op_theme_frame.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 5))
        ttk.Label(op_theme_frame, text="Select organization operation:", font=("SF Pro Display", 12, "bold")).pack(side='left')
        self.operations = {
            "Organize a single folder": 1,
            "Organize a single file": 2,
            "Organize all files in a folder": 3,
            "Organize all folders in a folder": 4
        }
        self.operation_var = tk.StringVar()
        self.operation_dropdown = ttk.Combobox(
            op_theme_frame, values=list(self.operations.keys()), state="readonly", width=40,
            textvariable=self.operation_var
        )
        self.operation_dropdown.pack(side='left', padx=(10, 0))
        self.operation_dropdown.current(0)
        # Theme dropdown (now next to operation dropdown)
        ttk.Label(op_theme_frame, text="Theme:").pack(side='left', padx=(15, 0))
        self.theme_combo = ttk.Combobox(
            op_theme_frame,
            values=self.available_themes,
            state="readonly",
            width=12,
            textvariable=self.current_theme
        )
        self.theme_combo.pack(side='left')
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
        ToolTip(self.theme_combo, "Change the application theme")

        # --- Path input with recent folders dropdown ---
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=2, column=0, pady=10, sticky='w')
        ttk.Label(path_frame, text="Enter the full path:").pack(side='left')
        self.path_entry = ttk.Entry(path_frame, width=48)
        self.path_entry.pack(side='left', padx=5)
        # DND hint
        ToolTip(self.path_entry, "Enter the full path to a file or folder\n(You can drag and drop the wanted file or folder here)")
        # Recent folders dropdown
        self.recent_folders_var = tk.StringVar(value=[])
        self.recent_folders_combo = ttk.Combobox(path_frame, textvariable=tk.StringVar(), width=10, state="readonly")
        self.recent_folders_combo.pack(side='left', padx=2)
        self.recent_folders_combo.bind("<<ComboboxSelected>>", self.on_recent_folder_selected)
        # Browse button
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_path)
        browse_btn.pack(side='left')
        ToolTip(browse_btn, "Browse for a file or folder")
        # About button (next to Browse)
        about_btn = ttk.Button(path_frame, text="About", command=self.show_about)
        about_btn.pack(side='left', padx=(5,0))
        ToolTip(about_btn, "About Organizicate")

        # --- Dark Mode Toggle Button ---
        # dark_btn = ttk.Button(path_frame, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        # dark_btn.pack(side='left', padx=(5,0))
        # ToolTip(dark_btn, "Switch between light and dark mode")

        # Run, Clear, Undo, Export, Import buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, pady=10, sticky='w')

        run_btn = ttk.Button(btn_frame, text="Organize", command=self.run_operation)
        run_btn.pack(side='left', padx=5)
        ToolTip(run_btn, "Run the selected organization operation")

        clear_btn = ttk.Button(btn_frame, text="Clear Output", command=self.clear_output)
        clear_btn.pack(side='left', padx=5)
        ToolTip(clear_btn, "Clear the output log")

        undo_btn = ttk.Button(btn_frame, text="Undo Last Action", command=self.undo_last_action)
        undo_btn.pack(side='left', padx=5)
        ToolTip(undo_btn, "Undo the last file/folder move operation")

        export_btn = ttk.Button(btn_frame, text="Export Categories", command=self.export_categories)
        export_btn.pack(side='left', padx=5)
        ToolTip(export_btn, "Export user categories to a file")

        import_btn = ttk.Button(btn_frame, text="Import Categories", command=self.import_categories)
        import_btn.pack(side='left', padx=5)
        ToolTip(import_btn, "Import user categories from a file")

        # --- Output Section ---
        ttk.Label(main_frame, text="Output:", font=("SF Pro Display", 12, "bold")).grid(row=4, column=0, sticky='w')
        self.output_text = scrolledtext.ScrolledText(main_frame, width=95, height=15, font=("0xProto Nerd Font", 10), state='disabled')
        self.output_text.grid(row=5, column=0, sticky='nsew')

        # --- Category Manager Section ---
        cat_frame = ttk.LabelFrame(main_frame, text="Manage Categories (Add/Edit/Delete User Categories)", padding=10)
        cat_frame.grid(row=6, column=0, pady=15, sticky='nsew')
        cat_frame.columnconfigure(0, weight=0)
        cat_frame.columnconfigure(1, weight=0)
        for i in range(6):
            cat_frame.rowconfigure(i, weight=0)
        cat_frame.rowconfigure(2, weight=1)  # Let the listbox row expand

        # --- Search/Filter Entry with clear button ---
        search_frame = ttk.Frame(cat_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0,5))
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.cat_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.cat_search_var, width=20)
        search_entry.pack(side='left', padx=3)
        ToolTip(search_entry, "Type to filter categories")
        self.cat_search_var.trace_add("write", lambda *a: self.refresh_category_listbox())
        # Quick clear button
        clear_btn = ttk.Button(search_frame, text="X", width=2, command=lambda: self.cat_search_var.set(""))
        clear_btn.pack(side='left', padx=2)
        ToolTip(clear_btn, "Clear search")

        # --- Category Control Buttons (move to top right) ---
        btn_cat_frame = ttk.Frame(cat_frame)
        btn_cat_frame.grid(row=1, column=1, sticky='w', pady=(0, 5))
        self.add_cat_btn = ttk.Button(btn_cat_frame, text="Add New Category", command=self.add_category)
        self.add_cat_btn.pack(side='left', padx=5)
        ToolTip(self.add_cat_btn, "Add a new user category (Ctrl+N)")
        self.update_cat_btn = ttk.Button(btn_cat_frame, text="Update Category", command=self.update_category, state='disabled')
        self.update_cat_btn.pack(side='left', padx=5)
        ToolTip(self.update_cat_btn, "Update the selected category (Ctrl+S)")
        self.delete_cat_btn = ttk.Button(btn_cat_frame, text="Delete Category", command=self.delete_category, state='disabled')
        self.delete_cat_btn.pack(side='left', padx=5)
        ToolTip(self.delete_cat_btn, "Delete the selected user category (Del)")
        # Copy extensions button
        self.copy_ext_btn = ttk.Button(btn_cat_frame, text="Copy Ext", command=self.copy_extensions, state='disabled')
        self.copy_ext_btn.pack(side='left', padx=5)
        ToolTip(self.copy_ext_btn, "Copy extensions to clipboard")
        # Reset categories button
        self.reset_cat_btn = ttk.Button(btn_cat_frame, text="Reset Categories", command=self.reset_categories)
        self.reset_cat_btn.pack(side='left', padx=5)
        ToolTip(self.reset_cat_btn, "Remove all user-made categories and restore defaults")
        # --- Category listbox with frame for better layout ---
        listbox_frame = ttk.Frame(cat_frame)
        listbox_frame.grid(row=1, column=0, rowspan=7, sticky='nsew', padx=(0, 10))
        listbox_frame.rowconfigure(0, weight=1)
        listbox_frame.columnconfigure(0, weight=1)
        self.category_listbox = tk.Listbox(listbox_frame, height=8, width=25)
        self.category_listbox.pack(side='left', fill='both', expand=True)
        self.category_listbox.bind("<<ListboxSelect>>", self.on_category_select)
        ToolTip(self.category_listbox, "List of categories (double-click to edit)")
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.category_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.category_listbox.config(yscrollcommand=scrollbar.set)

        # --- Entry for category name ---
        ttk.Label(cat_frame, text="Category Name:").grid(row=2, column=1, sticky='w')
        self.cat_name_var = tk.StringVar()
        self.cat_name_entry = ttk.Entry(cat_frame, textvariable=self.cat_name_var, width=40)
        self.cat_name_entry.grid(row=3, column=1, sticky='ew', pady=3)
        ToolTip(self.cat_name_entry, "Enter or edit the category name")

        # --- Entry for extensions (comma separated) ---
        ttk.Label(cat_frame, text="Extensions (comma separated, with dot):").grid(row=4, column=1, sticky='w')
        self.cat_ext_var = tk.StringVar()
        self.cat_ext_entry = ttk.Entry(cat_frame, textvariable=self.cat_ext_var, width=40)
        self.cat_ext_entry.grid(row=5, column=1, sticky='ew', pady=3)
        ToolTip(self.cat_ext_entry, "Enter extensions, e.g. .txt, .pdf")

        # --- Category description field (user categories only) ---
        ttk.Label(cat_frame, text="Description (optional):").grid(row=6, column=1, sticky='w')
        self.cat_desc_var = tk.StringVar()
        self.cat_desc_entry = ttk.Entry(cat_frame, textvariable=self.cat_desc_var, width=40)
        self.cat_desc_entry.grid(row=7, column=1, sticky='ew', pady=3)
        ToolTip(self.cat_desc_entry, "Optional description for user categories")

        # --- Extension count label ---
        self.ext_count_var = tk.StringVar(value="")
        self.ext_count_label = ttk.Label(cat_frame, textvariable=self.ext_count_var, foreground="gray")
        self.ext_count_label.grid(row=8, column=1, sticky='w', pady=(0, 3))

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor='w')
        status_bar.pack(side='bottom', fill='x')

    def refresh_category_listbox(self):
        """Refresh the category listbox with all categories, filtered by search."""
        self.category_listbox.delete(0, 'end')
        if not self.file_categories:
            print("Warning: No categories found!")
            return
        filter_text = self.cat_search_var.get().strip().lower() if hasattr(self, 'cat_search_var') else ""
        cats_sorted = sorted(self.file_categories.keys())
        for cat in cats_sorted:
            if filter_text and filter_text not in cat.lower():
                continue
            suffix = " (default)" if cat in self.default_categories else ""
            self.category_listbox.insert('end', cat + suffix)
        print(f"Refreshed listbox with {len(cats_sorted)} categories (filtered: {filter_text})")

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
        cat_name_with_suffix = self.category_listbox.get(idx)
        cat_name = cat_name_with_suffix.replace(" (default)", "")
        self.cat_name_var.set(cat_name)
        exts = self.file_categories.get(cat_name, [])
        self.cat_ext_var.set(", ".join(exts))
        self.ext_count_var.set(f"Extension count: {len(exts)}")
        self.copy_ext_btn.config(state='normal')
        # Description: only for user categories
        if cat_name in self.default_categories:
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

    def on_category_double_click(self, event):
        sel = self.category_listbox.curselection()
        if sel:
            self.cat_name_entry.focus_set()
            self.cat_name_entry.selection_range(0, tk.END)

    def _find_extension_conflicts(self, ext_list, ignore_category=None):
        """Return a dict of {ext: category} for extensions already assigned elsewhere."""
        conflicts = {}
        for cat, exts in self.file_categories.items():
            if ignore_category and cat == ignore_category:
                continue
            for ext in exts:
                if ext in ext_list:
                    conflicts[ext] = cat
        return conflicts

    def add_category(self):
        # Always clear selection and fields when adding a new category
        self.category_listbox.selection_clear(0, 'end')
        name = self.cat_name_var.get().strip()
        exts = self.cat_ext_var.get().strip()
        desc = self.cat_desc_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Category name cannot be empty.")
            return
        if name in self.file_categories:
            messagebox.showerror("Error", f"Category '{name}' already exists.")
            return
        ext_list = self.parse_extensions(exts)
        if not ext_list:
            messagebox.showerror("Error", "Please enter at least one valid extension (e.g. .txt).")
            return
        # Category conflict warning
        conflicts = self._find_extension_conflicts(ext_list)
        if conflicts:
            msg = "Warning: The following extensions are already assigned to other categories:\n"
            msg += "\n".join([f"{ext}: {cat}" for ext, cat in conflicts.items()])
            msg += "\n\nDo you want to continue?"
            if not messagebox.askyesno("Extension Conflict", msg):
                return
        self.file_categories[name] = ext_list
        # Save description for user categories
        if not hasattr(self, "user_category_desc"):
            self.user_category_desc = {}
        if desc:
            self.user_category_desc[name] = desc
        save_categories(self.file_categories)
        self.extension_to_category = build_extension_map(self.file_categories)
        self.refresh_category_listbox()
        self.clear_category_entries()
        self.log(f"Added new category '{name}' with extensions: {', '.join(ext_list)}")
        self.status_var.set(f"Added new category '{name}'")

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
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete category '{name}'?"):
            self.file_categories.pop(name, None)
            save_categories(self.file_categories)
            self.extension_to_category = build_extension_map(self.file_categories)
            self.refresh_category_listbox()
            self.clear_category_entries()
            self.log(f"Deleted category '{name}'")
            self.status_var.set(f"Deleted category '{name}'")

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
        if op in (1, 3, 4):  # Folder related operations
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
            self.recent_folders.insert(0, folder)
            if len(self.recent_folders) > 10:
                self.recent_folders = self.recent_folders[:10]
            self.recent_folders_combo["values"] = self.recent_folders

    def clear_output(self):
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.config(state='disabled')
        self.status_var.set("Output cleared.")

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
        self.output_text.see('end')
        self.output_text.config(state='disabled')
        self.log_to_file(message)

    def log_summary(self, count_moved):
        """Log a summary of moved files/folders by category."""
        if not count_moved:
            self.log("No files or folders were moved.")
            return
        summary_lines = ["Summary of moved items:"]
        for cat, count in sorted(count_moved.items()):
            summary_lines.append(f"  {cat}: {count}")
        summary = "\n".join(summary_lines)
        self.log(summary)
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
                self._run_operation_thread(op, path)
            except Exception as e:
                self.action_queue.put(("status", "Error occurred."))
                self.action_queue.put(("log", f"Error: {e}"))
                messagebox.showerror("Operation Error", f"An error occurred:\n{e}")
        self.operation_thread = threading.Thread(
            target=safe_run,
            daemon=True
        )
        self.operation_thread.start()

    def _run_operation_thread(self, op, path):
        try:
            if op == 1:
                self.organize_single_folder(path)
            elif op == 2:
                self.organize_single_file(path)
            elif op == 3:
                self.organize_all_files_in_folder(path)
            elif op == 4:
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
        return self.extension_to_category.get(ext, "Other")

    def ensure_folder(self, base_path, folder_name):
        folder_path = os.path.join(base_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def organize_single_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError(f"\n'{folder_path}' is not a valid folder path.")
        # Only move files in the top-level folder, do not touch subfolders or their contents
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            self.log("\nNo files found in the folder.")
            return
        count_moved = defaultdict(int)
        undo_ops = []
        for file_name in files:
            category = self.get_category_for_file(file_name)
            dest_folder = self.ensure_folder(folder_path, category)
            file_path = os.path.join(folder_path, file_name)
            dst = os.path.join(dest_folder, file_name)
            try:
                shutil.move(file_path, dst)
                self.log(f"\nMoved file '{file_name}' to folder '{category}'.")
                count_moved[category] += 1
                undo_ops.append((file_path, dst))
            except PermissionError as e:
                self.log(f"\nPermission denied: '{file_name}'. Skipped. ({e})")
            except Exception as e:
                self.log(f"\nFailed to move '{file_name}': {e}")
        if undo_ops:
            self.undo_stack.append(undo_ops)
        self.log_summary(count_moved)

    def organize_single_file(self, file_path):
        """Organize a single file by moving it into its category folder."""
        if not os.path.isfile(file_path):
            raise ValueError(f"'{file_path}' is not a valid file path.")
        folder_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        category = self.get_category_for_file(file_name)
        dest_folder = self.ensure_folder(folder_path, category)
        dst = os.path.join(dest_folder, file_name)
        if os.path.abspath(file_path) == os.path.abspath(dst):
            self.log(f"\nFile '{file_name}' is already in the correct folder.")
            return
        try:
            shutil.move(file_path, dst)
            self.log(f"\nMoved file '{file_name}' to folder '{category}'.")
            self.undo_stack.append([(file_path, dst)])
        except PermissionError as e:
            self.log(f"\nPermission denied: '{file_name}'. Skipped. ({e})")
        except Exception as e:
            self.log(f"\nFailed to move '{file_name}': {e}")

    def organize_all_files_in_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError(f"'{folder_path}' is not a valid folder path.")
        count_moved = defaultdict(int)
        undo_ops = []
        # Only process files in the top-level folder, not recursively
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        for file in files:
            src = os.path.join(folder_path, file)
            category = self.get_category_for_file(file)
            dest_folder = self.ensure_folder(folder_path, category)
            dst = os.path.join(dest_folder, file)
            if os.path.abspath(src) == os.path.abspath(dst):
                continue  # skip if same file
            try:
                shutil.move(src, dst)
                self.action_queue.put(("log", f"Moved file '{file}' to folder '{category}'."))
                count_moved[category] += 1
                undo_ops.append((src, dst))
            except PermissionError as e:
                self.action_queue.put(("log", f"Permission denied: '{file}'. Skipped. ({e})"))
            except Exception as e:
                self.action_queue.put(("log", f"Failed to move '{file}': {e}"))
        if undo_ops:
            self.undo_stack.append(undo_ops)
        # Fix: Use log_summary instead of _format_log_summary
        self.action_queue.put(("log", self.log_summary(count_moved)))

    def organize_all_folders_in_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError(f"'{folder_path}' is not a valid folder path.")
        count_moved = 0
        undo_ops = []
        # Only move top-level folders, do not move or touch their contents
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                try:
                    # Try to access the folder to avoid permission errors early
                    os.listdir(item_path)
                except PermissionError as e:
                    self.action_queue.put(("log", f"Permission denied: '{item}'. Skipped. ({e})"))
                    continue
                except Exception as e:
                    self.action_queue.put(("log", f"Failed to access folder '{item}': {e}"))
                    continue
                # Do not move folders that are already in a category folder
                category = self.get_category_for_folder(item_path)
                dest_folder = self.ensure_folder(folder_path, category)
                dst = os.path.join(dest_folder, item)
                if os.path.abspath(item_path) == os.path.abspath(dst):
                    continue
                try:
                    # Prevent moving a folder into itself or its subfolders
                    common = os.path.commonpath([os.path.abspath(item_path), os.path.abspath(dst)])
                    if common == os.path.abspath(item_path):
                        continue
                except ValueError:
                    pass
                try:
                    shutil.move(item_path, dst)
                    self.action_queue.put(("log", f"Moved folder '{item}' to folder '{category}'."))
                    count_moved += 1
                    undo_ops.append((item_path, dst))
                except PermissionError as e:
                    self.action_queue.put(("log", f"Permission denied: '{item}'. Skipped. ({e})"))
                except Exception as e:
                    self.action_queue.put(("log", f"Failed to move folder '{item}': {e}"))
        if undo_ops:
            self.undo_stack.append(undo_ops)
        self.action_queue.put(("log", f"Moved {count_moved} folders."))

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
            messagebox.showinfo("Undo", "No action to undo.")
            return
        last = self.undo_stack.pop()
        try:
            # last: list of (src, dst) tuples (undo: move dst -> src)
            for src, dst in reversed(last):
                if os.path.exists(dst):
                    shutil.move(dst, src)
                    self.log(f"Undo: moved '{os.path.basename(dst)}' back to '{os.path.dirname(src)}'")
            self.status_var.set("Undo completed.")
        except Exception as e:
            self.log(f"Undo failed: {e}")
            self.status_var.set("Undo failed.")

    # --- System Tray Minimization ---
    def minimize_to_tray(self):
        if not (pystray and Image):
            self.destroy()
            return
        self.withdrawn_for_tray = True
        self.withdraw()
        # Use get_resource_path to find appicon.png
        # Helper to get resource path for tray icon (works for PyInstaller and normal run)
        def get_resource_path(filename):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, filename)
            return os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)
        icon_png = get_resource_path("appicon.png")
        if not os.path.exists(icon_png):
            print("Warning: appicon.png not found for tray icon.")
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
        about_win = tk.Toplevel(self)
        # Set desired size here
        width, height = 540, 630
        about_win.resizable(False, False)
        about_win.grab_set()
        frame = ttk.Frame(about_win, padding=30)
        frame.pack(fill='both', expand=True)
        # App name
        app_name = ttk.Label(frame, text="Organizicate", font=("SF Pro Display", 30, "bold"))
        app_name.pack(pady=(0, 18))
        # Version
        version = ttk.Label(frame, text="Beta (v0.9.8.1)", font=("SF Pro Display", 16, "bold"), foreground="#555")
        version.pack(pady=(0, 18))
        # Description
        desc = ttk.Label(
            frame,
            text="A modern, customizable file/folder organizer for Windows.\n\nOrganizicate helps you quickly sort, categorize, and manage your files and folders with ease.\n\nDeveloped by @yourAmok.",
            font=("SF Pro Display", 13),
            justify="center",
            wraplength=470
        )
        desc.pack(pady=(0, 18))
        # Technical info
        info_lines = [
            f"Python version: {platform.python_version()}",
            f"Platform: {platform.system()} {platform.release()} ({platform.version()})",
            f"App location: {os.path.abspath(sys.argv[0])}",
            f"Config file: {os.path.abspath(CONFIG_FILE)}",
            f"Log file: {os.path.abspath(LOG_FILE)}",
            f"Default categories: {len(self.default_categories)}",
            f"User categories: {len([c for c in self.file_categories if c not in self.default_categories])}",
            f"Theme: {self.current_theme.get() if hasattr(self, 'current_theme') else 'N/A'}",
            f"Drag-and-drop: {'Enabled' if getattr(self, 'dnd_enabled', False) else 'Disabled'}",
            f"Threading: {'Enabled' if hasattr(self, 'operation_thread') else 'Disabled'}",
            f"Dependencies: tkinter, ttkbootstrap, PIL, pystray"
        ]
        info = ttk.Label(frame, text="\n".join(info_lines), font=("SF Pro Display", 11), justify="center", foreground="#444", anchor="center")
        info.pack(pady=(0, 10), fill='x', expand=True)
        # GitHub link
        def open_github(event=None):
            import webbrowser
            webbrowser.open_new("https://github.com/yourAmok/organizicate")
        link = tk.Label(frame, text="GitHub: github.com/yourAmok/organizicate", fg="#2563eb", cursor="hand2", font=("SF Pro Display", 10, "underline"))
        link.pack(pady=(10, 0))
        link.bind("<Button-1>", open_github)
        # Close button
        close_btn = ttk.Button(frame, text="Close", command=about_win.destroy)
        close_btn.pack(pady=(18, 0))
        # Center and set size
        self._center_window(about_win, width, height)

    def _center_window(self, win, width, height):
        win.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (width // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def on_theme_change(self, event=None):
        """Handle theme change from the dropdown."""
        selected_theme = self.current_theme.get()
        try:
            ttkb.Style().theme_use(selected_theme)
            # Re-apply button font after theme change
            ttkb.Style().configure("TButton", font=("SF Pro Display", 11))
            self.status_var.set(f"Theme changed to '{selected_theme}'")
        except Exception as e:
            self.status_var.set(f"Failed to change theme: {e}")

    def reset_categories(self):
        """Remove all user-made categories and restore only defaults."""
        user_cats = [cat for cat in self.file_categories if cat not in default_file_categories]
        if not user_cats:
            messagebox.showinfo("Reset Categories", "No user categories to remove.")
            return
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


# NOTE FOR DEVELOPERS:
# If you change or replace the icon file (appicon.ico
# and the .spec file before running PyInstaller again. Otherwise, PyInstaller may use a cached/old icon.
# Example:), you MUST delete the 'build' and 'dist' folders,
#   rmdir /s /q build
#   rmdir /s /q dist
#   del organizicate.spec
#   pyinstaller --onefile --windowed --icon=appicon.ico organizicate.py

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
