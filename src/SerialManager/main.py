import argparse
from glob import glob
from platform import system
from threading import Thread
from time import sleep
from tkinter import Tk

import serial.tools.list_ports

from SerialManager.Config import Config
from SerialManager.Device import Device
from SerialManager.ConsoleButtons import ConsoleButtons
from SerialManager.CSVFile import CSVFile
from SerialManager.YaMLFile import YaMLFile

baud_rate = 9600
operating_system = system()


def define_os_specific_serial_ports() -> list[str]:
    match operating_system:
        case "Linux":
            return glob("/dev/ttyACM*")
        case "Windows":
            return [port.device for port in serial.tools.list_ports.comports()]


def define_os_specific_startingdir() -> str:
    match operating_system:
        case "Linux":
            return "~/Desktop"
        case "Windows":
            return "~\\Desktop"
        case _:
            return "~/Desktop"


def serial_parallel_process(target: object | None) -> None:
    serial_port_array = define_os_specific_serial_ports()
    threads = []
    for serial_port in serial_port_array:
        thread = Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def no_join_parallel_process(target: object | None) -> list[Thread]:
    serial_port_array = define_os_specific_serial_ports()
    threads = []
    for serial_port in serial_port_array:
        thread = Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    return threads


def config_process(config: Config) -> None:
    serial_parallel_process(target=Device.start_dev)
    sleep(5)

    serial_parallel_process(target=Device.set_config_on_device)
    sleep(5)

    no_join_parallel_process(target=config.check_config_discrepancy)
    sleep(5)

    serial_parallel_process(target=Device.reset_dev)


def main() -> None:
    parser = argparse.ArgumentParser(description='Serial Device Configuration/Upload tool')
    subparsers = parser.add_subparsers(dest='arg')
    parser_arg = subparsers.add_parser('abeeway', help='Configure/Upload Abeeway trackers')
    parser_arg.add_argument('abeeway', choices=['config', 'upload', 'create-cfg'])
    args = parser.parse_args()

    if args.arg == 'abeeway':
        match args.abeeway:
            case 'config':
                gui = ConsoleButtons(title="Configure window", root=Tk())
                config = Config(root=gui.root, gui_instance=gui)

                (gui
                 .button1(text="Configure device",
                          bg="lightblue",
                          command=lambda: config_process(config))
                 .button2(text="Import/Export config",
                          bg="lightblue",
                          command=lambda: config.export_or_import())
                 .button3(text="Reset device",
                          bg="lightcoral",
                          command=lambda: serial_parallel_process(target=Device.reset_dev))
                 .button4(text="Start device",
                          bg="lightgreen",
                          command=lambda: serial_parallel_process(target=Device.start_dev))
                 .mainloop())
                exit()

            case 'upload':
                gui = ConsoleButtons(title="Upload window", root=Tk())
                config = Config(root=gui.root, gui_instance=gui)
                csvfile = CSVFile(root=gui.root, gui_instance=gui)

                (gui
                 .button1(text="Make CSV",
                          bg="lightblue",
                          command=lambda: csvfile.csv_builder_and_writer())
                 .button2(text="Import",
                          bg="lightblue",
                          command=lambda: csvfile.importer())
                 .button3(text="Clear device log",
                          bg="lightcoral",
                          command=lambda: config.clear_dev_log())
                 .button4(text="Export devices",
                          bg="lightgreen",
                          command=lambda: csvfile.export_devices_from_csv())
                 .mainloop())
                exit()

            case 'create-cfg':
                YaMLFile(root=Tk())

    else:
        print("Try 'serialmgr abeeway'.")
        exit()
