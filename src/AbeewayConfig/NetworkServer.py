import csv


class NetworkServer:

    # Documentation about how to format the CSV file can be found at:
    # todo
    @staticmethod
    def csv_builder(deveui: str,
                    join_eui: str,
                    app_key: str,
                    name: str,
                    app_id: str,
                    _directive: str = "CREATE_OTAA",
                    _na: str = "",
                    _dev_model_id: str = "ABEE/Badge-1.0.2b-AS",
                    _motion_indicator: str = "RANDOM"
                    ) -> None:
        data = [
            [
                _directive, deveui, _na, _dev_model_id, join_eui, app_key,
                _na, _na, _na, _na,
                name,
                _na, _na, _na, _na, _na,
                _motion_indicator,
                _na, _na,
                app_id,
                _na, _na, _na, _na, _na
            ]
        ]

        # Specify the file name
        csv_file = "output.csv"

        # Open the CSV file in write mode
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        print("Data has been written to", csv_file)

    def grab_dev_info_tuple():
        pass


# testing
NetworkServer.csv_builder("1234567890ABCDEF", "1234567890ABCDEF", "1234567890ABCDEF", "Test", "1234567890ABCDEF")
