import csv
import os
import re
import shutil
import tkinter as tk
from dataclasses import dataclass
from io import BytesIO
from tkinter import filedialog, messagebox
from typing import Any

import kapak.error
import requests
from kapak.aes import decrypt

from SerialManager.CustomGUI import HidePassword, CustomDialog
from SerialManager.ConsoleButtons import ConsoleButtons


@dataclass
class DevStruct:
    deveui: str = ""
    join_eui: str = ""
    app_key: str = ""
    name: str = ""
    app_id: str = ""


class CSVFile:
    csv_file = os.path.join(os.path.dirname(__file__), "utils", "output.csv")

    def __init__(self,
                 root: tk.Tk,
                 gui_instance: ConsoleButtons):
        self.root = root
        self.gui = gui_instance

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
        """
        Fields with a default value already set are supposed to be the most common choices.
        However, I've decided to make them mutable to allow, for example, the deletion of devices,
        or creation of other devices that aren't the same model of dev_model_id
        :param deveui:
        :param join_eui:
        :param app_key:
        :param name:
        :param app_id:
        :param directive:
        :param _na:
        :param dev_model_id:
        :param motion_indicator:
        :return:
        """
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

    def fetch_and_choose_app_id(self) -> str | None:
        response = requests.get(url='https://community.thingpark.io/thingpark/wireless/'
                                    'rest/subscriptions/mine/appServers',
                                headers={
                                    'Authorization': f'Bearer {self.retrieve_token()}',
                                    'accept': 'application/json',
                                })
        json_appids = response.json()['briefs']  # list of app ids

        popup = tk.Toplevel(self.root)
        popup.title("Select Items")
        popup.geometry("300x300")

        listbox = tk.Listbox(popup, selectmode=tk.MULTIPLE)
        listbox.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        name_id_dict: dict[str, str] = {}

        selected_items = []

        def get_selected_items():
            selected_indices = listbox.curselection()
            # TODO improve this
            nonlocal selected_items
            selected_items = [listbox.get(i) for i in selected_indices]
            popup.destroy()

        for application in json_appids:
            name_id_dict.update({application['name']: application['ID']})
            listbox.insert(tk.END, application['name'])

        btn_select = tk.Button(popup, text="Select", command=get_selected_items)
        btn_select.pack(pady=10)
        btn_select.wait_window()

        if len(selected_items) == 0:
            messagebox.showwarning("No Selection",
                                   "Please select at least 1 application.")
            return
        else:
            final_list = [name_id_dict.get(element) for element in selected_items]
            return ",".join(final_list)

    def grab_dev_info(self, deveui: str) -> DevStruct:
        """
        Name might be a little misleading since it doesn't grab the app_id,
        but it's the only field where it has to be retrieved from the already set up network server
        :param deveui:
        :return:
        """
        devstruct = DevStruct()

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "values.csv"),
                  'r', newline='') as values:
            csv_reader = csv.reader(values, dialect='excel', delimiter=',')
            for row in csv_reader:
                if row[0].strip().lower() == deveui:
                    devstruct.deveui = deveui
                    devstruct.join_eui = row[1]
                    devstruct.app_key = row[2]
                elif row == csv_reader.line_num - 1:
                    self.gui.write_to_console(f"{deveui} not found in values.csv.")
                    return devstruct

        return devstruct

    def build_deveui_array_from_log(self) -> list[str]:
        deveui_array = []
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "utils", "deveui.txt"), 'r') as deveui_file:
                for line in deveui_file:
                    deveui = re.search('(.*)', line).group(1).strip().lower()
                    if deveui is not None:
                        deveui_array.append(deveui)
        except FileNotFoundError:
            self.gui.write_to_console("Please configure a device before trying this.")
        return deveui_array

    def export_devices_from_csv(self) -> None:
        try:
            with open(CSVFile.csv_file, 'rb') as csvfile:
                response = requests.post(url='https://community.thingpark.io/thingpark/wireless/rest/subscriptions/mine'
                                             '/devices/import?async=true&forceDevAddrs=false'
                                             '&networkSubscriptionsHandlingMode'
                                             '=ADVANCED',
                                         headers={
                                             'Authorization': f'Bearer {self.retrieve_token()}',
                                             'accept': 'application/json',
                                         },
                                         files={'csv': ('output.csv', csvfile, 'text/csv')}
                                         )
            match response.status_code:
                case 200:
                    self.gui.write_to_console(f"Success.")
                case 403:
                    self.gui.write_to_console(f"Token error.")

            self.gui.write_to_console(f"{response.text}")
        except FileNotFoundError:
            self.gui.write_to_console(f"No CSV output found.")

    @staticmethod
    def set_name() -> tuple[str, int]:
        popup = tk.Tk()
        popup.withdraw()  # hide the self.root window
        dialog = CustomDialog(popup, title="Enter Details")
        return dialog.name, dialog.starting_num

    def csv_builder_and_writer(self) -> None:
        deveui_array = self.build_deveui_array_from_log()
        csv_file = CSVFile.csv_file
        app_id = self.fetch_and_choose_app_id().strip()

        name, starting_num = CSVFile.set_name()

        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            for name_num, deveui in enumerate(deveui_array, start=starting_num):
                dev_info = self.grab_dev_info(deveui=deveui)
                dev_struct = CSVFile.csv_templater(deveui=dev_info.deveui,
                                                   join_eui=dev_info.join_eui,
                                                   app_key=dev_info.app_key,
                                                   name=f"{name.upper()} {name_num}",
                                                   app_id=app_id)
                writer.writerows(dev_struct)

        self.gui.write_to_console(f"CSV file created.\n"
                                  f"There are {len(deveui_array)} devices.")
        response = messagebox.askyesno("Device amount", f"Are there {len(deveui_array)} devices?")
        match response:
            case False:
                os.remove(csv_file)
                self.gui.write_to_console("CSV file deleted.")

    def importer(self) -> None:
        from SerialManager.main import define_os_specific_startingdir

        def choose_file_type():
            def on_csv():
                file_type.set("csv")
                file_dialog.destroy()

            def on_bin():
                file_type.set("bin")
                file_dialog.destroy()

            file_dialog = tk.Toplevel(self.root)
            file_dialog.title("Select File Type")
            tk.Label(file_dialog, text="Choose what file to import:").pack(pady=10)
            tk.Button(file_dialog, text="Device info (csv)", command=on_csv).pack(side="left", padx=20, pady=20)
            tk.Button(file_dialog, text="API key (bin)", command=on_bin).pack(side="right", padx=20, pady=20)
            file_dialog.transient(self.root)
            file_dialog.grab_set()
            self.root.wait_window(file_dialog)

        file_type = tk.StringVar()
        choose_file_type()

        match file_type.get():
            case "csv":
                filetypes = [("CSV", "*.csv")]
                dest_filename = "values.csv"
            case "bin":
                filetypes = [("BIN", "*.bin")]
                dest_filename = "keys.bin"
            case _:
                self.gui.write_to_console("No file type selected.")
                return

        filename = filedialog.askopenfilename(initialdir=define_os_specific_startingdir(), filetypes=filetypes)

        if filename:
            destination_dir = os.path.join(os.path.dirname(__file__), "utils")
            os.makedirs(destination_dir, exist_ok=True)
            destination_file = os.path.join(destination_dir, dest_filename)
            try:
                shutil.copy(filename, destination_file)
                self.gui.write_to_console(f"{file_type.get().upper()} file imported successfully as {dest_filename}.")
            except Exception as e:
                self.gui.write_to_console("Error:" + str(e))
        else:
            self.gui.write_to_console("No file selected.")

    def retrieve_token(self) -> str | None:
        try:
            api = open(os.path.join(os.path.dirname(__file__), "utils", "keys.bin"), "rb")
            out = BytesIO()
            dialog = HidePassword(self.root, title="Password")
            password = dialog.result
            try:
                for _ in decrypt(src=api, dst=out, password=password):
                    pass
            except kapak.error.KapakError as e:
                self.gui.write_to_console(f"Error: {e}")
                return
            except TypeError:
                self.gui.write_to_console("Empty password.")
                return
            out.seek(0)
            decrypted_content = out.read().decode().splitlines()
            response = requests.post(url='https://community.thingpark.io/users-auth/protocol/openid-connect/token',
                                     data={
                                         'client_id': f'{decrypted_content[0]}',
                                         'client_secret': f'{decrypted_content[1]}',
                                         'grant_type': 'client_credentials'
                                     },
                                     headers={"content-type": "application/x-www-form-urlencoded"}
                                     ).json()
            return response['access_token']
        except FileNotFoundError:
            self.gui.write_to_console("Please import your API Key.")
            return
