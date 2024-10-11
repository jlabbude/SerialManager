import argparse
import os
import re
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


def define_os_specific_serial_ports() -> list[str]:
    match system():
        case "Linux":
            return glob("/dev/ttyACM*")
        case "Windows":
            return [port.device for port in serial.tools.list_ports.comports()]


def define_os_specific_startingdir() -> str:
    match system():
        case "Windows":
            return "~\\Desktop"
        case _:
            return "~/Desktop"


def serial_parallel_process(target: object | None, baud_rate: int = 9600) -> None:
    threads: list[Thread] = []
    for serial_port in define_os_specific_serial_ports():
        thread = Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def no_join_parallel_process(target: object | None, baud_rate: int = 9600) -> list[Thread]:
    threads: list[Thread] = []
    for serial_port in define_os_specific_serial_ports():
        thread = Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    return threads


def config_process(config: Config) -> None:
    config.gui.clear_console()

    serial_parallel_process(target=Device.start_dev)
    sleep(5)

    serial_parallel_process(target=Device.set_config_on_device)
    sleep(5)

    no_join_parallel_process(target=config.check_config_discrepancy)
    sleep(5)

    serial_parallel_process(target=Device.reset_dev)
    sleep(5)

    deveui_list = get_deveui_from_done(config.gui.read_console())
    write_deveui_to_log(deveui_list)
    print_lines(len(deveui_list), config)


def get_deveui_from_done(done: str) -> list[str]:
    done_lines = done.splitlines()
    done_list: list[str] = []
    for line in done_lines:
        match = re.match(pattern=r"Done: (.*)", string=line)
        if match:
            done_list.append(match.group(1))
    return done_list


def write_deveui_to_log(deveiu_list: list[str]) -> None:
    deveui_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "deveui.txt")
    if os.path.isfile(deveui_file):
        with open(deveui_file, 'r+') as deveui_log:
            for deveui in deveiu_list:
                deveui_log_content = deveui_log.read().splitlines()
                if deveui not in deveui_log_content:
                    deveui_log.write(deveui + "\n")
    else:
        with open(deveui_file, 'a') as deveui_log:
            for deveui in deveiu_list:
                deveui_log.write(deveui + "\n")


def print_lines(size: int, config: Config) -> None:
    deveui_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "deveui.txt")
    with open(deveui_file, 'rb') as deveui_log:
        deveui_amount: int = sum(1 for _ in deveui_log)
        config.gui.write_to_console(f'{size} devices have been wrote to the log.'
                                    f'\nThere are {deveui_amount} devices.')


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
                device = Device(root=gui.root, gui_instance=gui)

                (gui
                 .button1(text="Configure device",
                          bg="lightblue",
                          command=lambda: config_process(config))
                 .button2(text="Import/Export config",
                          bg="lightblue",
                          command=lambda: config.export_or_import())
                 .button3(text="Check devices",
                          bg="#8cfc88",
                          command=lambda: config.print_number_of_devices())
                 .button4(text="Start/Reset",
                          bg="#fc964c",
                          command=lambda: device.start_or_reset())
                 .mainloop())
                exit()

            case 'upload':
                gui = ConsoleButtons(title="Upload window", root=Tk())
                root = gui.root
                config = Config(root=root, gui_instance=gui)
                csvfile = CSVFile(root=root, gui_instance=gui)

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
