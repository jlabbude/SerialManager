import csv
import os
import re
import shutil
import tkinter as tk

from tkinter import Text, filedialog
from dataclasses import dataclass


@dataclass
class DevStruct:
    deveui: str = ""
    join_eui: str = ""
    app_key: str = ""
    name: str = ""
    app_id: str = ""


class NetworkServer:

    # Fields with default value are supposed to be the most common values
    # However I've decided to make them mutable to allow, for example, the deletion of devices,
    # or creation of other devices that aren't the same model of dev_model_id
    @staticmethod
    def csv_templater(console_output: Text,
                      deveui: str,
                      join_eui: str,
                      app_key: str,
                      name: str,
                      app_id: str,
                      directive: str = "CREATE_OTAA",
                      _na: str = "",
                      dev_model_id: str = "ABEE/Badge-1.0.2b-AS",
                      motion_indicator: str = "RANDOM"
                      ) -> None:
        data = [
            [
                directive, deveui, _na, dev_model_id, join_eui, app_key,
                _na, _na, _na, _na,
                name,
                _na, _na, _na, _na, _na,
                motion_indicator,
                _na, _na,
                app_id,
                _na, _na, _na, _na, _na
            ]
        ]

        csv_file = "output.csv"

        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        console_output.insert(tk.END, f"Written to {csv_file}")

    @staticmethod
    def grab_dev_info_struct(deveui: str, console_output: Text) -> DevStruct:
        devstruct = DevStruct()

        with open('values.csv', 'r', newline='') as values:
            csv_reader = csv.reader(values, dialect='excel', delimiter=',')
            for row in csv_reader:
                if row[0].strip().lower() == deveui:
                    devstruct.deveui = deveui
                    devstruct.join_eui = row[1]
                    devstruct.app_key = row[2]
                elif row == csv_reader.line_num - 1:
                    print("DevEUI not on list")
                    return devstruct

        return devstruct

    @staticmethod
    def deveui_array_builder() -> None:
        global deveui_array
        deveui_array = []
        with open('deveui.txt', 'r') as deveui_file:
            for line in deveui_file:
                deveui = re.search('(.*)\n', line).group(1).strip().lower()
                if deveui is not None:
                    deveui_array.append(deveui)

    @staticmethod
    def csv_builder(console_output: Text) -> None:
        for deveui in deveui_array:
            dev_struct = NetworkServer.grab_dev_info_struct(deveui=deveui,
                                                            console_output=console_output)
            NetworkServer.csv_templater(console_output=console_output,
                                        deveui=dev_struct.deveui,
                                        join_eui=dev_struct.join_eui,
                                        app_key=dev_struct.app_key,
                                        name=dev_struct.name,
                                        app_id=dev_struct.app_id, )
            console_output.insert(tk.END, f".csv file created.\n"
                                          f"There are {len(deveui_array) - 1}, is this correct?")
            # todo popup here

    def import_values(console_output: Text) -> None:
        from .abeewayconfig import define_os_specific_startingdir
        filename = filedialog.askopenfilename(initialdir=define_os_specific_startingdir(),
                                              filetypes=[("CSV", "*.csv")])
        if filename:
            destination_dir = os.path.join(os.path.dirname(__file__), "utils")
            os.makedirs(destination_dir, exist_ok=True)
            destination_file = os.path.join(destination_dir, "values.cfg")
            try:
                shutil.copy(filename, destination_file)
                console_output.insert(tk.END, "CSV file imported successfully.\n")
            except Exception as e:
                console_output.insert(tk.END, "Error:" + str(e) + "\n")
        else:
            console_output.insert(tk.END, "No file selected.\n")
