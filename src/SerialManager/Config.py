import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter.simpledialog import askstring

from typing_extensions import Buffer

from SerialManager.abeeway_smartbadge_dict import config_dict
from SerialManager.ConsoleButtons import ConsoleButtons


class Config:

    def __init__(self, gui_instance: ConsoleButtons, root: tk.Tk):
        self.gui = gui_instance
        self.root = root

    def clear_dev_log(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "deveui.txt"), 'w') as file:
            file.truncate()
            file.close()
        self.gui.write_to_console('DevEUI log cleared.')

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

    def check_config_discrepancy(self, serial_port: str, br: int) -> bool:
        from SerialManager.Device import Device
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
                            self.gui.write_to_console(f"Config error: {deveui} ")
                            self.gui.write_to_console(f"An error occurred. Please try starting the device, "
                                                   f"then configuring again. ")
                            return False

                        if config_value_cfg != config_value_dev:
                            self.gui.write_to_console(f"Config error: {deveui} ")
                            self.gui.write_to_console(f"[Parameter : {config_name}] - Current: [{config_value_dev}] | "
                                                   f"Correct: [{config_value_cfg}] ")
                            return False
        except FileNotFoundError:
            self.gui.write_to_console(f"Config file not found.")
            return False

        self.gui.write_to_console(f"Done: {deveui} ")
        return True

    def export_or_import(self) -> None:
        from SerialManager.main import define_os_specific_startingdir

        def export_import():
            def on_csv():
                choice.set("export")
                file_dialog.destroy()

            def on_bin():
                choice.set("import")
                file_dialog.destroy()

            file_dialog = tk.Toplevel(self.root)
            file_dialog.title("Select")
            tk.Label(file_dialog, text="Import or export?").pack(pady=10)
            tk.Button(file_dialog, text="Export current config", command=on_csv).pack(side="left", padx=20, pady=20)
            tk.Button(file_dialog, text="Import external config", command=on_bin).pack(side="right", padx=20, pady=20)
            file_dialog.transient(self.root)
            file_dialog.grab_set()
            self.root.wait_window(file_dialog)

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
                        self.gui.write_to_console("Config file imported successfully.")
                    except Exception as e:
                        self.gui.write_to_console("Error:" + str(e) + "")
                else:
                    self.gui.write_to_console("No file selected.")
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
                        self.gui.write_to_console("Config file exported successfully as {}.\n".format(new_file_name))
                    else:
                        self.gui.write_to_console("No new file name provided. Operation cancelled.")
                else:
                    self.gui.write_to_console("No folder selected.")
