import re
import os
from tkinter import Text
import tkinter as tk
from .Device import Device
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

    def check_config_discrepancy(serial_port: str, br: int, console_output: Text) -> bool:
        device_config = Device.config_show_at_device(serial_port=serial_port, br=br)
        deveui = str(Device.get_deveui(serial_port=serial_port, br=br))
        config_file = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config"), "config.cfg")
        with open(config_file, 'r') as config:
            for line in config:
                config_parameter_cfg = Config.get_config_parameter_from_cfg(line)
                config_value_cfg = Config.get_config_value_from_cfg(config_parameter_cfg, line)
                config_name = config_dict.get(config_parameter_cfg)
                if config_parameter_cfg is not None or config_value_cfg is not None:
                    config_value_dev = Device.get_config_value_from_dev(device_config, config_name)
                    if config_value_cfg != config_value_dev:
                        console_output.insert(tk.END, f"Config error: {deveui} \n")
                        console_output.insert(tk.END, f"[{config_name} : {config_value_cfg}] -> [{config_value_dev}] \n")
                        return False

        console_output.insert(tk.END, f"Done: {deveui} \n")
        return True

