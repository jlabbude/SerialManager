import csv
import os
import re
import shutil
import tkinter as tk
import requests

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
    csv_file = os.path.join(os.path.dirname(__file__), "utils", "output.csv")

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

    @staticmethod
    def write_to_csv(data: list[str]) -> None:
        deveui = (data[0][1]).lower()
        csv_file = CSVFile.csv_file

        try:
            with open(csv_file, mode='r+', newline='') as file:
                file_content = file.read()
                if deveui not in file_content:
                    writer = csv.writer(file)
                    writer.writerows(data)
        except FileNotFoundError:
            with open(csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)

    @staticmethod
    def retrieve_app_id(console_output: Text):
        # todo choose app id for csv_templater
        response = requests.post(url='https://community.thingpark.io/thingpark/wireless/'
                                     'rest/subscriptions/mine/appServers',
                                 headers={
                                     'Authorization': f'Bearer {CSVFile.retrieve_token()}',
                                     'accept': 'application/json',
                                 })

        matches = re.findall("\"ID:\" \"(.*)\"", response.text)

        with open(os.path.join(os.path.dirname(__file__), "utils", "appids.txt"), 'a') as output:
            for match in matches:
                output.write(match)

    # Name might be a little misleading since it doesn't grab the app_id,
    # but it's the only field where it has to be retrieved from the already set up network server
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
    def export_devices_from_csv(console_output: Text):
        with open(CSVFile.csv_file, 'rb') as csvfile:
            response = requests.post(url='https://community.thingpark.io/thingpark/wireless/rest/subscriptions/mine'
                                         '/devices/import?async=true&forceDevAddrs=false'
                                         '&networkSubscriptionsHandlingMode'
                                         '=ADVANCED',
                                     headers={
                                         'Authorization': f'Bearer {CSVFile.retrieve_token()}',
                                         'accept': 'application/json',
                                     },
                                     files={'csv': ('output.csv', csvfile, 'text/csv')}
                                     )
        match response.status_code:
            case 200:
                console_output.insert(tk.END, f"Success.\n")
            case 403:
                console_output.insert(tk.END, f"Token error.\n")

        console_output.insert(tk.END, f"{response.text}")

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

    @staticmethod
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

    @staticmethod
    def retrieve_token() -> str:
        response = requests.post(url='https://community.thingpark.io/users-auth/protocol/openid-connect/token',
                                 data={
                                     'client_id': f'{open(os.path.join(os.path.dirname(__file__),
                                                                       "utils", "client.txt"), "r").read()}',
                                     'client_secret': f'{open(os.path.join(os.path.dirname(__file__),
                                                                           "utils", "secret.txt"), "r").read()}',
                                     'grant_type': 'client_credentials'
                                 },
                                 headers={"content-type": "application/x-www-form-urlencoded"}
                                 ).json()
        return response['access_token']
