import csv
import os
import re
import shutil
import tkinter as tk

from dataclasses import dataclass
from tkinter import Text, filedialog
from typing import Any


@dataclass
class DevStruct:
    deveui: str = ""
    join_eui: str = ""
    app_key: str = ""
    name: str = ""
    app_id: str = ""


class CSVFile:

    # Fields with default value are supposed to be the most common values
    # However I've decided to make them mutable to allow, for example, the deletion of devices,
    # or creation of other devices that aren't the same model of dev_model_id
    @staticmethod
    def csv_templater(deveui: str,
                      join_eui: str,
                      app_key: str,
                      name: str,
                      app_id: str,
                      directive: str = "CREATE_OTAA",
                      _na: str = "",
                      dev_model_id: str = "ABEE/Badge-1.0.2b-AS",
                      motion_indicator: str = "RANDOM"
                      ) -> list[str | Any]:
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

        return data

    def write_to_csv(data: list[str]) -> None:
        global csv_file
        csv_file = os.path.join(os.path.dirname(__file__), "utils", "output.csv")

        pattern = re.compile(data[0][1], re.IGNORECASE)

        with open(csv_file, mode='r', newline='') as file:
            lines = file.readlines()
            for line in lines:
                if pattern.search(line.strip()):
                    return
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    @staticmethod
    def grab_dev_info(deveui: str, console_output: Text) -> DevStruct:
        devstruct = DevStruct()

        with open('values.csv', 'r', newline='') as values:
            csv_reader = csv.reader(values, dialect='excel', delimiter=',')
            for row in csv_reader:
                if row[0].strip().lower() == deveui:
                    devstruct.deveui = deveui
                    devstruct.join_eui = row[1]
                    devstruct.app_key = row[2]
                elif row == csv_reader.line_num - 1:
                    console_output.insert(tk.END, f"{deveui} not found in values.csv.\n")
                    return devstruct

        return devstruct

    @staticmethod
    def build_deveui_array_from_log() -> list[str]:
        deveui_array = []
        with open('deveui.txt', 'r') as deveui_file:
            for line in deveui_file:
                deveui = re.search('(.*)\n', line).group(1).strip().lower()
                if deveui is not None:
                    deveui_array.append(deveui)
        return deveui_array

    @staticmethod
    def csv_builder(console_output: Text) -> None:
        deveui_array = CSVFile.build_deveui_array_from_log()
        for deveui in deveui_array:
            dev_info = CSVFile.grab_dev_info(deveui=deveui,
                                             console_output=console_output)
            dev_struct = CSVFile.csv_templater(deveui=dev_info.deveui,
                                               join_eui=dev_info.join_eui,
                                               app_key=dev_info.app_key,
                                               name=dev_info.name,
                                               app_id=dev_info.app_id)
            CSVFile.write_to_csv(data=dev_struct)

            console_output.insert(tk.END, f"CSV file created.\n"
                                          f"There are {len(deveui_array)} devices. \n")
            # todo popup here

    def import_values(console_output: Text) -> None:
        from .abeewayconfig import define_os_specific_startingdir
        filename = filedialog.askopenfilename(initialdir=define_os_specific_startingdir(),
                                              filetypes=[("CSV", "*.csv")])
        if filename:
            destination_dir = os.path.join(os.path.dirname(__file__), "utils")
            os.makedirs(destination_dir, exist_ok=True)
            destination_file = os.path.join(destination_dir, "values.csv")
            try:
                shutil.copy(filename, destination_file)
                console_output.insert(tk.END, "CSV file imported successfully.\n")
            except Exception as e:
                console_output.insert(tk.END, "Error:" + str(e) + "\n")
        else:
            console_output.insert(tk.END, "No file selected.\n")
