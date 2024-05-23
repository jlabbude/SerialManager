import tkinter as tk
from glob import glob
from platform import system
from threading import Thread
from time import sleep
from tkinter import Button, Text

import serial.tools.list_ports

from .Config import Config
from .Device import Device
from .CSVFile import CSVFile

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


def serial_parallel_process(target) -> None:
    threads = []
    for serial_port in serial_port_array:
        thread = Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def with_console_parallel_process(target, console_output):
    threads = []
    for serial_port in serial_port_array:
        thread = Thread(target=target, args=(serial_port, baud_rate, console_output))
        threads.append(thread)
        thread.start()
    return threads


def config_process(console_output) -> None:
    define_os_specific_serial_ports()

    # TODO: investigate instability here
    serial_parallel_process(target=Device.start_dev)
    sleep(5)

    serial_parallel_process(target=Device.set_config_on_device)
    sleep(5)

    with_console_parallel_process(target=Config.check_config_discrepancy, console_output=console_output)
    sleep(5)

    serial_parallel_process(target=Device.reset_dev)


def config_gui_builder() -> None:
    root = tk.Tk()
    root.title("Config window")
    root.geometry("800x600")
    root.configure(padx=10, pady=10)

    console = Text(root, wrap="word")
    console.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
    button1 = Button(root,
                     text="Configure device",
                     bg="lightblue",
                     fg="black",
                     width=15,
                     height=2,
                     font=("Arial", 12),
                     command=lambda: config_process(console_output=console))
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
                     text="Import config",
                     bg="lightblue",
                     fg="black",
                     width=15,
                     height=2,
                     font=("Arial", 12),
                     command=lambda: Config.import_config(console))

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


def nw_sv_gui():
    root = tk.Tk()
    root.title("Upload window")
    root.geometry("800x600")
    root.configure(padx=10, pady=10)

    console = Text(root, wrap="word")
    console.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
    button1 = Button(root,
                     text="Make CSV",
                     bg="lightblue",
                     fg="black",
                     width=15,
                     height=2,
                     font=("Arial", 12),
                     command=lambda: CSVFile.csv_builder(console_output=console))
    button2 = Button(root,
                     text="Import device info",
                     bg="lightblue",
                     fg="black",
                     width=15,
                     height=2,
                     font=("Arial", 12),
                     command=lambda: CSVFile.import_values(console_output=console))
    button3 = Button(root,
                     text="Renew API key",
                     bg="lightcoral",
                     fg="black",
                     width=15,
                     height=2,
                     font=("Arial", 12),
                     command=lambda: print('TODO'))
    button4 = Button(root,
                     text="Export devices",
                     bg="lightgreen",
                     fg="black",
                     width=15,
                     height=2,
                     font=("Arial", 12),
                     command=lambda: print('TODO'))

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


def main():
    config_gui_builder()
