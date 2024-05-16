import os
import shutil
import sys
import time
import serial.tools.list_ports
import tkinter as tk
from glob import glob
from platform import system
from threading import Thread
from tkinter import filedialog, Button, Text

from .Config import Config
from .Device import Device

baud_rate = 9600


def define_os_specific_params():
    global serial_port_array
    global initialdir
    operating_system = system()
    match operating_system:
        case "Linux":
            serial_port_array = glob("/dev/ttyACM*")
            initialdir = "~/Desktop"
        case "Windows":
            def get_ports():
                ports = serial.tools.list_ports.comports()
                return [port.device for port in ports]
            serial_port_array = get_ports()
            initialdir = "~\\Desktop"


def import_config(console_output):
    filename = filedialog.askopenfilename(initialdir=initialdir,
                                          filetypes=[("Text files", "*.txt"),
                                                     ("Config files", "*.cfg")])
    if filename:
        destination_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
        os.makedirs(destination_dir, exist_ok=True)
        destination_file = os.path.join(destination_dir, "config.cfg")
        try:
            shutil.copy(filename, destination_file)
            console_output.insert(tk.END, "Config file imported successfully.\n")
        except Exception as e:
            console_output.insert(tk.END, "Error:" + str(e) + "\n")
    else:
        console_output.insert(tk.END, "No file selected.\n")


def serial_parallel_process(target):
    threads = []
    for serial_port in serial_port_array:
        thread = Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def discrepancy_parallel_process(target, console_output):
    threads = []
    for serial_port in serial_port_array:
        thread = Thread(target=target, args=(serial_port, baud_rate, console_output))
        threads.append(thread)
        thread.start()
    return threads


def config_process(console_output) -> None:
    # Hacky way of detecting new badges after the program has already started
    define_os_specific_params()

    serial_parallel_process(target=Device.start_dev)

    serial_parallel_process(target=Device.set_config_on_device)

    discrepancy_parallel_process(target=Config.check_config_discrepancy, console_output=console_output)
    time.sleep(5)

    serial_parallel_process(target=Device.reset_dev)


def main():
    define_os_specific_params()
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
                     command=lambda: import_config(console))

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

    sys.stdout = sys.__stdout__
