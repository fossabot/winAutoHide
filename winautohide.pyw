#!/usr/bin/env python3
"""Automatically hide files in user specified folders that match a regular expression."""
import ctypes
import os
import pickle
import re
import sys
import time
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
from configparser import ConfigParser

DATABASE_FILE_PATH = "./database"
CONFIG_FILE_PATH = "./config.ini"
DEFAULT_FREQUENCY = -1
DEFAULT_PATTERN = r"^\."
EXECUTABLE_NAME = "./winAutoHide.exe"
STARTUP_FOLDER = "\\".join((os.environ["APPDATA"],
                            r"Microsoft\Windows\Start Menu\Programs\Startup"))


class GUI:
    """The GUI class for interacting with tkinter."""

    def __init__(self, master):
        """Create tkinter widgets and display them."""
        # setup window
        self.master = master
        self.master.title("winAutoHide")
        self.master.geometry()
        self.master.resizable(width=False, height=False)

        # load watchlist from database
        self.watchlist = load_watchlist()

        # load settings from config file
        if not os.path.exists(CONFIG_FILE_PATH):
            create_config_file()
        config = ConfigParser()
        with open(CONFIG_FILE_PATH, "r") as file:
            config.read_file(file)
        pattern = config.get("settings", "pattern")
        frequency = config.getint("settings", "frequency")

        # create widgets
        self.options_frame = ttk.Frame(self.master)
        self.directory_buttons = ttk.Frame(self.master)
        self.treeview_frame = ttk.Frame(self.master)
        self.bottom_buttons = ttk.Frame(self.master)

        self.pattern_label = ttk.Label(self.options_frame,
                                       text="Pattern: ")
        self.frequency_label = ttk.Label(self.options_frame,
                                         text="Frequency: ")
        self.pattern_entry = ttk.Entry(self.options_frame)
        self.frequency_entry = ttk.Entry(self.options_frame)
        self.directories_treeview = ttk.Treeview(self.treeview_frame,
                                                 columns=("path",),
                                                 selectmode="browse",
                                                 show="tree")
        self.directories_treeview.column("#0", minwidth=0, width=0)
        self.directories_treeview.column("path", width=400)
        self.directories_treeview_scrollbar_y = ttk.Scrollbar(self.treeview_frame,
                                                              orient=tk.VERTICAL,
                                                              command=self.directories_treeview.yview)
        self.directories_treeview_scrollbar_x = ttk.Scrollbar(self.treeview_frame,
                                                              orient=tk.HORIZONTAL,
                                                              command=self.directories_treeview.xview)
        self.directories_treeview.config(yscrollcommand=self.directories_treeview_scrollbar_y.set)
        self.directories_treeview.config(xscrollcommand=self.directories_treeview_scrollbar_x.set)
        self.add_directory_button = ttk.Button(self.directory_buttons,
                                               text="Add new directory",
                                               command=self.add_directory)
        self.remove_directory_button = ttk.Button(self.directory_buttons,
                                                  text="Remove directory",
                                                  command=self.remove_directory)
        self.toggle_directories_button = ttk.Button(self.directory_buttons,
                                                    text="Hide directories",
                                                    command=self.toggle_directories)
        self.start_button = ttk.Button(self.bottom_buttons,
                                       text="Start",
                                       command=self.start)
        self.run_on_startup_button = ttk.Button(self.bottom_buttons,
                                                text="Run on system startup",
                                                command=run_on_system_startup)
        self.remove_from_startup_button = ttk.Button(self.bottom_buttons,
                                                     text="Remove from system startup",
                                                     command=remove_from_system_startup)

        # display widgets
        self.options_frame.grid(row=0, column=0, pady=10, padx=20)
        self.directory_buttons.grid(row=1, column=0, pady=10, padx=20)
        self.treeview_frame.grid(row=2, column=0, pady=10, padx=20)
        self.bottom_buttons.grid(row=3, column=0, pady=10, padx=20)

        self.pattern_label.grid(row=0, column=0, sticky=tk.W)
        self.frequency_label.grid(row=1, column=0, sticky=tk.W)
        self.pattern_entry.grid(row=0, column=1, pady=2.5)
        self.frequency_entry.grid(row=1, column=1, pady=2.5)
        self.directories_treeview.grid(row=0, column=0)
        self.directories_treeview_scrollbar_y.grid(row=0, column=1, sticky=tk.NS)
        self.directories_treeview_scrollbar_x.grid(row=1, column=0, sticky=tk.EW)
        self.add_directory_button.grid(row=0, column=0, padx=5)
        self.remove_directory_button.grid(row=0, column=1, padx=5)
        self.toggle_directories_button.grid(row=0, column=2, padx=5)
        self.start_button.grid(row=0, column=0, padx=5)
        self.run_on_startup_button.grid(row=0, column=1, padx=5)
        self.remove_from_startup_button.grid(row=0, column=2, padx=5)

        # apply default selections
        self.frequency_entry.insert(0, frequency)
        self.pattern_entry.insert(0, pattern)

        self.refresh_directories_treeview()

    def add_directory(self):
        """Add a new directory to the watchlist."""
        directory_path = tkinter.filedialog.askdirectory()
        if directory_path:
            self.watchlist.add(directory_path)
            self.refresh_directories_treeview()

    def remove_directory(self):
        selected_column = self.directories_treeview.selection()
        selected_column_path = self.directories_treeview.item(selected_column, "values")[0]

        self.watchlist.remove(selected_column_path)
        self.directories_treeview.delete(selected_column)
        self.refresh_directories_treeview()

    def toggle_directories(self):
        """Toggle between showing and hiding the directories list."""
        if self.treeview_frame.grid_info() == {}:
            self.refresh_directories_treeview()
            self.treeview_frame.grid()
            self.toggle_directories_button.config(text="Hide directories")
            pass
        else:
            self.treeview_frame.grid_remove()
            self.toggle_directories_button.config(text="Show directories")

    def refresh_directories_treeview(self):
        """Refresh the directories treeview widget."""
        old_columns = self.directories_treeview.get_children()

        for path in self.watchlist:
            self.directories_treeview.insert("", 0, values=(path,))

        if old_columns:
            self.directories_treeview.delete(*old_columns)

        if self.watchlist:
            self.directories_treeview.selection_set(self.directories_treeview.get_children()[-1])

    def start(self):
        """Destroy current window and start the mainloop of the background process."""
        save_watchlist(self.watchlist)

        pattern = self.pattern_entry.get()
        try:
            frequency = int(self.frequency_entry.get())
        except ValueError as error:
            print(error)
            return None
        save_config(pattern, frequency)

        if not self.watchlist:
            print("Watchlist is empty!")
        else:
            self.master.withdraw()
            main_loop(self.watchlist, pattern, frequency)
        exit(0)


def hide_files(files: set):
    """Hide all files in files."""
    print(" ".join(("Hiding these files:", *files)))
    for file in files:
        ctypes.windll.kernel32.SetFileAttributesW(file, 2)


def matches_pattern(pattern: str, string: str) -> bool:
    """Check whether string matches pattern."""
    regex = re.compile(pattern)
    search = regex.search(string)
    if search is not None:
        return True
    return False


def get_matching_files(pattern: str, path: str) -> set:
    """Return a list of all files in path that match pattern."""
    print("".join(("Searching in: ", path)))
    matching_files = set()
    try:
        files = os.listdir(path)
    except PermissionError:
        return set()
    for file in files:
        if matches_pattern(pattern, file):
            matching_files.add("".join((path, "\\", file)))
        elif os.path.isdir("".join((path, "\\", file))):
            matching_files = matching_files | get_matching_files(pattern, "".join((path, "\\", file)))
    return matching_files


def main_loop(watch_list: set, pattern: str, timeout: int):
    """Hide files in watch list that match pattern then wait and repeat."""
    while True:
        for directory in watch_list:
            hide_files(get_matching_files(pattern, directory))
        if timeout == -1:
            break
        for _ in range(0, timeout):
            time.sleep(1)


def save_watchlist(watchlist: set):
    """Save watchlist to pickle file."""
    with open(DATABASE_FILE_PATH, "wb") as file:
        pickle.dump(watchlist, file)


def load_watchlist() -> set:
    """Return watchlist from database."""
    if os.path.exists(DATABASE_FILE_PATH):
        with open(DATABASE_FILE_PATH, "rb") as file:
            watchlist = pickle.load(file)
        return watchlist
    else:
        return set()


def create_config_file():
    """Create the config file."""
    config = ConfigParser()
    config["settings"] = {}
    config["settings"]["pattern"] = DEFAULT_PATTERN
    config["settings"]["frequency"] = str(DEFAULT_FREQUENCY)

    with open(CONFIG_FILE_PATH, "w") as file:
        config.write(file)


def save_config(pattern: str, frequency: int):
    """Save the settings to the config file."""
    if not os.path.exists(CONFIG_FILE_PATH):
        create_config_file()

    config = ConfigParser()
    with open(CONFIG_FILE_PATH, "r") as file:
        config.read_file(file)

    config["settings"]["pattern"] = pattern
    config["settings"]["frequency"] = str(frequency)

    with open(CONFIG_FILE_PATH, "w") as file:
        config.write(file)


def run_on_system_startup():
    """Add program to system startup."""
    startup_file = STARTUP_FOLDER + "/winAutoHide.pyw"
    executable_path = os.path.realpath(EXECUTABLE_NAME)

    with open(startup_file, "w") as file:
        file.write(f"from subprocess import call\n"
                   f"call(['{executable_path}', '--no-gui'])")


def remove_from_system_startup():
    """Remove program from system startup."""
    startup_file = STARTUP_FOLDER + "/winAutoHide.pyw"

    if os.path.exists(startup_file):
        os.remove(startup_file)


def start_from_commandline():
    """Start the program silently."""
    data = load_watchlist()
    if data:
        if os.path.exists(CONFIG_FILE_PATH):
            config = ConfigParser()
            with open(CONFIG_FILE_PATH, "r") as file:
                config.read_file(file)

            pattern = config["settings"]["pattern"]
            frequency = int(config["settings"]["frequency"])

            main_loop(data, pattern, frequency)
        else:
            create_config_file()
            main_loop(data, DEFAULT_PATTERN, DEFAULT_FREQUENCY)
    else:
        print("No files in watchlist!")


def start_gui():
    """Start the Graphical User Interface."""
    root = tk.Tk()
    window = GUI(root)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-gui":
            start_from_commandline()
    else:
        start_gui()
