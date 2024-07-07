import os
import shutil
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import filedialog

import yaml

from SerialManager.CustomGUI import ConfigGUI
from SerialManager.GUI_setup import console, root
from SerialManager.ConfigGen import ConfigGen


@dataclass
class ConfigStruct:
    values: list[int] = field(default_factory=list)
    parameter: list[int] = field(default_factory=list)
    description: list[str] = field(default_factory=list)
    description_long: list[str] = field(default_factory=list)
    units: list[str] = field(default_factory=list)
    select_list: list[str | dict[str: list[str]]] = field(default_factory=list)
    list_flags: list[bool | None] = field(default_factory=list)
    range: list[(int, int), None] = field(default_factory=list)
    disabled: list[int, str, None] = field(default_factory=list)


class YaMLFile:

    @staticmethod
    def import_config() -> None:
        from SerialManager.serialmgr import define_os_specific_startingdir
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
    def read_and_set_config() -> list[(int, int)]:
        gui_display_config = ConfigStruct()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'abeeway-config-template.yaml'), 'r') as yamlfile:
            config_data: dict[dict] = yaml.safe_load(yamlfile).get('config', [{}])
        param_names = [value for value in config_data]
        for name in param_names:
            gui_display_config.values.append(config_data.get(name).get('value'))
            gui_display_config.description.append(config_data.get(name).get('description'))
            gui_display_config.description_long.append(config_data.get(name).get('description-long'))
            gui_display_config.units.append(config_data.get(name).get('unit'))
            gui_display_config.select_list.append(config_data.get(name).get('list'))
            gui_display_config.list_flags.append(config_data.get(name).get('list-type'))
            gui_display_config.parameter.append(config_data.get(name).get('parameter'))
            if config_data.get(name).get('disabled') is not None:
                gui_display_config.disabled.append(int(config_data.get(name).get('disabled')))

            else:
                gui_display_config.disabled.append(None)
            if config_data.get(name).get('range-high') is not None or config_data.get(name).get('range-low') is not None:
                if config_data.get(name).get('range-high') is str or config_data.get(name).get('range-low') is str:
                    gui_display_config.range.append(((int(config_data.get(name).get('range-low')), 16),
                                                     (int(config_data.get(name).get('range-high')), 16)))
                else:
                    gui_display_config.range.append((config_data.get(name).get('range-low'),
                                                    (config_data.get(name).get('range-high'))))
            else:
                gui_display_config.range.append(None)

        root.withdraw()
        root2 = tk.Tk()
        result = ConfigGUI(root=root2,
                           items=param_names,
                           values=gui_display_config.values,
                           description=gui_display_config.description,
                           description_long=gui_display_config.description_long,
                           units=gui_display_config.units,
                           select_list=gui_display_config.select_list,
                           list_flag=gui_display_config.list_flags,
                           parameters=gui_display_config.parameter,
                           rangehl=gui_display_config.range,
                           disabled=gui_display_config.disabled)
        root2.wait_window()
        return result.cfg

    def create_cfg(self) -> None:
        values = self.read_and_set_config()
        gen = ConfigGen(cfg=values)
        gen.create_cfg_file()
