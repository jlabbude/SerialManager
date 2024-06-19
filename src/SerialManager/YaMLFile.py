import os
import shutil
import tkinter as tk
from tkinter import filedialog

import yaml

from .CustomGUI import TesteConfig
from .GUI_setup import console, root
from .YaMLConfigDataClasses import AbeewaySmartBadgeConfig


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
        # TODO refactor this mess
        param_names = [value for value in config_data]
        values: list[int] = []
        description: list[str] = []
        description_long: list[str] = []
        units: list[str] = []
        select_list: list[str] = []
        list_flags: list[bool | None] = []
        for name in param_names:
            values.append(config_data.get(name).get('value'))
            description.append(config_data.get(name).get('description'))
            description_long.append(config_data.get(name).get('description-long'))
            units.append(config_data.get(name).get('unit'))
            select_list.append(config_data.get(name).get('list'))
            list_flags.append(config_data.get(name).get('list-type'))
        root.withdraw()
        root2 = tk.Tk()
        TesteConfig(root=root2,
                    items=param_names,
                    values=values,
                    description=description,
                    description_long=description_long,
                    units=units,
                    select_list=select_list,
                    list_flag=list_flags)
