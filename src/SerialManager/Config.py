import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter.simpledialog import askstring

from typing_extensions import Buffer

from SerialManager.GUI_setup import console, root
from SerialManager.smartbadgecfgdict import config_dict


class Config:

    @staticmethod
    def clear_dev_log():
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "deveui.txt"), 'w') as file:
            file.truncate()
            file.close()
        console.insert(tk.END, 'DevEUI log cleared.\n')

    @staticmethod
    def get_new_pass() -> Buffer:
        with open(os.path.join(os.path.join(os.path.dirname(__file__), "utils"), "config.cfg"), 'r') as cfg:
            match = re.search("config set 102 (.*)", cfg.read())
            return (match.group().encode() if match else b'123') + b'\r'

    @staticmethod
    def get_config_value_from_cfg(parameter: int, line: str) -> int:
        if parameter is not None:
            pattern = r"config set %d (.*)" % parameter
            p = re.compile(pattern)
            match = p.search(line)
            if match:
                return int(match.group(1))

    @staticmethod
    def get_config_parameter_from_cfg(line: str) -> int:
        p = re.compile("config set (.*) ")
        match = p.search(line)
        if match:
            return int(match.group(1))

    @staticmethod
    def check_config_discrepancy(serial_port: str, br: int) -> bool:
        from Device import Device
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
    def export_or_import() -> None:
        from SerialManager.serialmgr import define_os_specific_startingdir

        def export_import():
            def on_csv():
                choice.set("export")
                file_dialog.destroy()

            def on_bin():
                choice.set("import")
                file_dialog.destroy()

            file_dialog = tk.Toplevel(root)
            file_dialog.title("Select")
            tk.Label(file_dialog, text="Import or export?").pack(pady=10)
            tk.Button(file_dialog, text="Export current config", command=on_csv).pack(side="left", padx=20, pady=20)
            tk.Button(file_dialog, text="Import external config", command=on_bin).pack(side="right", padx=20, pady=20)
            file_dialog.transient(root)
            file_dialog.grab_set()
            root.wait_window(file_dialog)

        choice = tk.StringVar()
        export_import()

        match choice.get():
            case "import":
                filename = filedialog.askopenfilename(initialdir=define_os_specific_startingdir(),
                                                      filetypes=[("Text files", "*.txt"),
                                                                 ("Config files", "*.cfg"),
                                                                 ("YaML files", "*.yaml")])
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
            case "export":
                folder = filedialog.askdirectory(initialdir=define_os_specific_startingdir())
                config_file = os.path.join(os.path.join(os.path.dirname(__file__), "utils"), "config.cfg")

                if folder and config_file:
                    new_file_name = askstring("Input", "Nome da operação:",
                                              parent=None)
                    if new_file_name:
                        new_file_path = os.path.join(folder, new_file_name)
                        new_file_name.join(".cfg")
                        shutil.copy(config_file, os.path.join(folder, new_file_path + ".cfg"))
                        console.insert(tk.END, "Config file exported successfully as {}.\n".format(new_file_name))
                    else:
                        console.insert(tk.END, "No new file name provided. Operation cancelled.\n")
                else:
                    console.insert(tk.END, "No folder selected.\n")
