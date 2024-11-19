
#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import threading
import json
import logging
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('converter.log'),
        logging.StreamHandler()
    ]
)

class BuildConfig:
    """Build configuration settings."""
    DEFAULT_REQUIREMENTS = [
        'python3',
        'kivy',
        'requests',
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'pillow',
        'pyjnius',
        'android'
    ]
    
    ANDROID_PERMISSIONS = [
        'INTERNET',
        'READ_EXTERNAL_STORAGE',
        'WRITE_EXTERNAL_STORAGE',
        'ACCESS_NETWORK_STATE'
    ]
    
    BUILD_SETTINGS = {
        'api': 29,
        'minapi': 21,
        'sdk': 24,
        'ndk': '19b',
        'arch': 'armeabi-v7a'
    }

class PyToApkConverter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config_file = Path.home() / '.pyapkconverter' / 'config.json'
        self.python_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.init_config()
        self.setup_gui()
        self.load_saved_config()
        self.recent_projects = []

    def init_config(self):
        """Initialize configuration directory and file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            default_config = {
                'last_python_dir': str(Path.home()),
                'last_output_dir': str(Path.home() / 'APK_Output'),
                'recent_projects': []
            }
            self.save_config(default_config)

    def load_saved_config(self):
        """Load saved configuration."""
        try:
            with open(self.config_file) as f:
                config = json.load(f)
                self.output_dir.set(config.get('last_output_dir', ''))
                self.recent_projects = config.get('recent_projects', [])
                self.update_recent_projects_menu()
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")

    def save_config(self, config):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def setup_gui(self):
        """Setup the main GUI components."""
        self.title("Python to APK Converter")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create menu
        self.create_menu()

        # Create main content
        self.create_main_content()

        # Create status bar
        self.create_status_bar()

    def create_menu(self):
        """Create application menu."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)

        # Recent projects submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Projects", menu=self.recent_menu)

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clean Build", command=self.clean_build)
        tools_menu.add_command(label="Check Requirements", command=self.check_requirements)
        tools_menu.add_command(label="Build APK", command=self.start_build_apk)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_content(self):
        """Create the main content area."""
        settings_frame = ttk.LabelFrame(self.main_container, text="Project Settings")
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # File selectors
        self.create_file_selectors(settings_frame)

        # Build options frame
        build_frame = ttk.LabelFrame(self.main_container, text="Build Options")
        build_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Create build options
        self.create_build_options(build_frame)

        # Progress and log frame
        progress_frame = ttk.LabelFrame(self.main_container, text="Build Progress")
        progress_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # Create progress indicators
        self.create_progress_indicators(progress_frame)

    def create_file_selectors(self, parent):
        """Create file selection widgets."""
        ttk.Label(parent, text="Python File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.python_entry = ttk.Entry(parent, textvariable=self.python_file, width=50)
        self.python_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(parent, text="Browse", command=self.browse_python_file).grid(row=0, column=2, padx=5)

        ttk.Label(parent, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.output_entry = ttk.Entry(parent, textvariable=self.output_dir, width=50)
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(parent, text="Browse", command=self.browse_output_dir).grid(row=1, column=2, padx=5)

    def create_build_options(self, parent):
        """Create build configuration options."""
        ttk.Label(parent, text="Target SDK:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        sdk_versions = ['29', '28', '27', '26']
        self.sdk_var = tk.StringVar(value='29')
        sdk_combo = ttk.Combobox(parent, textvariable=self.sdk_var, values=sdk_versions, state='readonly')
        sdk_combo.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(parent, text="Build Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.build_type = tk.StringVar(value='debug')
        ttk.Radiobutton(parent, text="Debug", variable=self.build_type, value='debug').grid(row=1, column=1, sticky="w", padx=5)
        ttk.Radiobutton(parent, text="Release", variable=self.build_type, value='release').grid(row=1, column=2, sticky="w", padx=5)

    def create_progress_indicators(self, parent):
        """Create progress bar and log area."""
        self.progress = ttk.Progressbar(parent, length=400, mode='determinate')
        self.progress.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.log_text = tk.Text(parent, height=10, width=60)
        self.log_text.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=1, column=3, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def create_status_bar(self):
        """Create status bar."""
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky="ew")
        self.status_var.set("Ready")

    def update_recent_projects_menu(self):
        """Update the recent projects menu."""
        self.recent_menu.delete(0, tk.END)
        for project in self.recent_projects[-5:]:  # Keep only last 5 projects
            self.recent_menu.add_command(
                label=project['name'],
                command=lambda p=project: self.load_project
