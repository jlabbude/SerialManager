import csv
import re

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
    def csv_builder(deveui: str,
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

        print("written to", csv_file)

    @staticmethod
    def grab_dev_info_struct() -> DevStruct:
        devstruct = DevStruct()

        with open('deveui.txt', 'r') as deveui_file:
            deveui = re.search('(.*)\n', deveui_file.read()).group(1).strip().lower()
            if deveui is None:
                print("No deveui found")
                return devstruct
            else:
                deveui = deveui
                print(deveui)

        with open('values.csv', 'r', newline='') as values:
            csv_reader = csv.reader(values, dialect='excel', delimiter=',')
            for row in csv_reader:
                if row[0].strip().lower() == deveui:
                    devstruct.deveui = deveui

                    devstruct.join_eui = row[1]
                    print(row[1])
                    devstruct.app_key = row[2]
                    print(row[2])
                elif row == csv_reader.line_num - 1:
                    print("DevEUI not on list")
                    return devstruct

        return devstruct



struct = NetworkServer.grab_dev_info_struct()

NetworkServer.csv_builder(struct.deveui,
                          struct.join_eui,
                          struct.app_key,
                          "Test",
                          "1234567890ABCDEF")
