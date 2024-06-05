import os
import shutil
from tkinter import filedialog

import tkinter as tk
import yaml

from SerialManager.GUI_setup import console, root


class YaMLFile:

    @staticmethod
    def import_config() -> None:
        from .serialmgr import define_os_specific_startingdir
        filename = filedialog.askopenfilename(initialdir=define_os_specific_startingdir(),
                                              filetypes=[("Text files", "*.txt"),
                                                         ("Config files", "*.cfg"),
                                                         ("YaML files", "*.yaml")])
        if filename:
            destination_dir = os.path.join(os.path.dirname(__file__), "utils")
            os.makedirs(destination_dir, exist_ok=True)
            destination_file = os.path.join(destination_dir, "config.yaml")
            try:
                shutil.copy(filename, destination_file)
                console.insert(tk.END, "Config file imported successfully.\n")
            except Exception as e:
                console.insert(tk.END, "Error:" + str(e) + "\n")
        else:
            console.insert(tk.END, "No file selected.\n")

    @staticmethod
    def create_config() -> None:
        with open(os.path.join(os.path.dirname(__file__), "utils", "config.yaml"), "w") as file:
            pass
