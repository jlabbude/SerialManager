import argparse
from glob import glob
from platform import system
from threading import Thread
from time import sleep
from tkinter import Button

import serial.tools.list_ports

from SerialManager.YaMLFile import YaMLFile
from SerialManager.CSVFile import CSVFile
from SerialManager.Config import Config
from SerialManager.Device import Device
from SerialManager.GUI_setup import root, console

baud_rate = 9600
operating_system = system()


def define_os_specific_serial_ports() -> None:
    global serial_port_array
    match operating_system:
        case "Linux":
            serial_port_array = glob("/dev/ttyACM*")
        case "Windows":
            def get_ports():
                ports = serial.tools.list_ports.comports()
                return [port.device for port in ports]

            serial_port_array = get_ports()


def define_os_specific_startingdir() -> str:
    match operating_system:
        case "Linux":
            return "~/Desktop"
        case "Windows":
            return "~\\Desktop"
        case _:
            return "~/Desktop"


def serial_parallel_process(target: object | None) -> None:
    threads = []
    for serial_port in serial_port_array:
        thread = Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def no_join_parallel_process(target: object | None) -> list[Thread]:
    threads = []
    for serial_port in serial_port_array:
        thread = Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    return threads


def config_process() -> None:
    define_os_specific_serial_ports()

    # TODO: investigate instability here
    serial_parallel_process(target=Device.start_dev)
    sleep(5)

    serial_parallel_process(target=Device.set_config_on_device)
    sleep(5)

    no_join_parallel_process(target=Config.check_config_discrepancy)
    sleep(5)

    serial_parallel_process(target=Device.reset_dev)


def main() -> None:
    parser = argparse.ArgumentParser(description='Serial Device Configuration/Upload tool')
    subparsers = parser.add_subparsers(dest='arg')
    parser_arg = subparsers.add_parser('abeeway', help='Configure/Upload Abeeway trackers')
    parser_arg.add_argument('abeeway', choices=['config', 'upload', 'create-cfg'])
    args = parser.parse_args()

    root.title("Config window")
    root.geometry("800x600")
    root.configure(padx=10, pady=10)

    console.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
    if args.arg == 'abeeway':
        match args.abeeway:
            case 'config':
                button1 = Button(root,
                                 text="Configure device",
                                 bg="lightblue",
                                 fg="black",
                                 width=15,
                                 height=2,
                                 font=("Arial", 12),
                                 command=lambda: config_process())
                button4 = Button(root,
                                 text="Reset device",
                                 bg="lightcoral",
                                 fg="black",
                                 width=15,
                                 height=2,
                                 font=("Arial", 12),
                                 command=lambda: serial_parallel_process(target=Device.reset_dev))
                button3 = Button(root,
                                 text="Start device",
                                 bg="lightgreen",
                                 fg="black",
                                 width=15,
                                 height=2,
                                 font=("Arial", 12),
                                 command=lambda: serial_parallel_process(target=Device.start_dev))
                button2 = Button(root,
                                 text="Export/Import config",
                                 bg="lightblue",
                                 fg="black",
                                 width=15,
                                 height=2,
                                 font=("Arial", 12),
                                 command=lambda: Config.export_or_import())

                root.grid_rowconfigure(0, weight=1)
                root.grid_rowconfigure(1, weight=1)
                root.grid_rowconfigure(2, weight=1)
                root.grid_rowconfigure(3, weight=1)
                root.grid_rowconfigure(4, weight=4)

                root.grid_columnconfigure(0, weight=2)
                root.grid_columnconfigure(1, weight=2)

                button1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                button2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                button3.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
                button4.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

                root.mainloop()

            case 'upload':
                button1 = Button(root,
                                 text="Make CSV",
                                 bg="lightblue",
                                 fg="black",
                                 width=15,
                                 height=2,
                                 font=("Arial", 12),
                                 command=lambda: CSVFile.csv_builder_and_writer())
                button2 = Button(root,
                                 text="Import",
                                 bg="lightblue",
                                 fg="black",
                                 width=15,
                                 height=2,
                                 font=("Arial", 12),
                                 command=lambda: CSVFile.importer())
                button3 = Button(root,
                                 text="Clear device log",
                                 bg="lightcoral",
                                 fg="black",
                                 width=15,
                                 height=2,
                                 font=("Arial", 12),
                                 command=lambda: Config.clear_dev_log())
                button4 = Button(root,
                                 text="Export devices",
                                 bg="lightgreen",
                                 fg="black",
                                 width=15,
                                 height=2,
                                 font=("Arial", 12),
                                 command=lambda: CSVFile.export_devices_from_csv())

                root.grid_rowconfigure(0, weight=1)
                root.grid_rowconfigure(1, weight=1)
                root.grid_rowconfigure(2, weight=1)
                root.grid_rowconfigure(3, weight=1)
                root.grid_rowconfigure(4, weight=4)

                root.grid_columnconfigure(0, weight=2)
                root.grid_columnconfigure(1, weight=2)

                button1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                button2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                button3.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
                button4.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

                root.mainloop()

            case 'create-cfg':
                seta = YaMLFile()
                seta.create_cfg()

                root.destroy()

    else:
        print("Try 'serialmgr abeeway'.")
        exit()
