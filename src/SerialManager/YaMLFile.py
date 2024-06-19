import os
import shutil
from tkinter import filedialog

import tkinter as tk
from typing import Any

import yaml

from .GUI_setup import console, root
from .YaMLConfigDataClasses import AbeewaySmartBadgeConfig
from .CustomGUI import TesteConfig


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
    def read_config_template():
        current_config = AbeewaySmartBadgeConfig()
        with open('/home/lucas/SerialManager/src/config/abeeway-config-template.yaml', 'r') as yamlfile:
            config_data: dict[dict] = yaml.safe_load(yamlfile).get('config', [{}])
        param_names = [value for value in config_data]
        values: list[int] = []
        description: list[str] = []
        description_long: list[str] = []
        units: list[str] = []
        for name in param_names:
            values.append(config_data.get(name).get('value'))
            description.append(config_data.get(name).get('description'))
            description_long.append(config_data.get(name).get('description-long'))
            units.append(config_data.get(name).get('unit'))
        root.withdraw()
        root2 = tk.Tk()
        TesteConfig(root2, items=param_names, values=values, description=description, units=units, description_long=description_long)
