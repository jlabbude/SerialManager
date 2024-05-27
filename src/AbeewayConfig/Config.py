import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog

from .Device import Device
from .GUI_setup import console
from .smartbadgecfgdict import config_dict


class Config:
    def get_config_value_from_cfg(parameter: int, line: str) -> int:
        if parameter is not None:
            pattern = r"config set %d (.*)" % parameter
            p = re.compile(pattern)
            match = p.search(line)
            if match:
                return int(match.group(1))

    def get_config_parameter_from_cfg(line: str) -> int:
        p = re.compile("config set (.*) ")
        match = p.search(line)
        if match:
            return int(match.group(1))

    def check_config_discrepancy(serial_port: str, br: int) -> bool:
        device_config = Device.config_show_at_device(serial_port=serial_port, br=br)
        deveui = str(Device.get_deveui(serial_port=serial_port, br=br))
        config_file = os.path.join(os.path.join(os.path.dirname(__file__), "utils"), "config.cfg")
        try:
            with open(config_file, 'r') as config:
                for line in config:
                    config_parameter_cfg = Config.get_config_parameter_from_cfg(line)
                    config_value_cfg = Config.get_config_value_from_cfg(config_parameter_cfg, line)
                    config_name = config_dict.get(config_parameter_cfg)
                    if config_parameter_cfg is not None or config_value_cfg is not None:
                        config_value_dev = Device.get_config_value_from_dev(device_config, config_name)

                        if config_parameter_cfg == 249 and config_value_dev == 5:
                            console.insert(tk.END, f"Config error: {deveui} \n")
                            console.insert(tk.END, f"An error occurred. Please try starting the device, "
                                                   f"then configuring again. \n")
                            return False

                        if config_value_cfg != config_value_dev:
                            console.insert(tk.END, f"Config error: {deveui} \n")
                            console.insert(tk.END, f"[Parameter : {config_name}] - Current: [{config_value_dev}] | "
                                                   f"Correct: [{config_value_cfg}] \n")
                            return False
        except FileNotFoundError:
            console.insert(tk.END, f"Config file not found.\n")
            return False

        console.insert(tk.END, f"Done: {deveui} \n")
        return True

    @staticmethod
    def import_config() -> None:
        from .abeewayconfig import define_os_specific_startingdir
        filename = filedialog.askopenfilename(initialdir=define_os_specific_startingdir(),
                                              filetypes=[("Text files", "*.txt"),
                                                         ("Config files", "*.cfg")])
        if filename:
            destination_dir = os.path.join(os.path.dirname(__file__), "utils")
            os.makedirs(destination_dir, exist_ok=True)
            destination_file = os.path.join(destination_dir, "config.cfg")
            try:
                shutil.copy(filename, destination_file)
                console.insert(tk.END, "Config file imported successfully.\n")
            except Exception as e:
                console.insert(tk.END, "Error:" + str(e) + "\n")
        else:
            console.insert(tk.END, "No file selected.\n")
