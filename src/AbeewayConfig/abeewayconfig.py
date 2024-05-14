import os
import shutil
import sys
import time
import tkinter as tk
from glob import glob
from threading import Thread
from tkinter import filedialog, Button, Text

from Config import Config
from Device import Device

baud_rate = 9600
serial_port_array = glob("/dev/ttyACM*")


def import_config(console_output):
    initialdir = "~/Desktop"

    # Open file dialog to select a file
    filename = filedialog.askopenfilename(initialdir=initialdir,
                                          filetypes=[("Text files", "*.txt"),
                                                     ("Config files", "*.cfg")])

    if filename:
        # Destination directory for the config file
        destination_dir = "config"

        # Construct the destination file path
        destination_file = os.path.join(destination_dir, "config.cfg")

        try:
            # Copy the selected file to the destination directory
            shutil.copy(filename, destination_file)
            console_output.insert(tk.END, "Config file imported successfully.")
        except Exception as e:
            console_output.insert(tk.END, "Error:", e)
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


def _parallel_process(target, console_output):
    threads = []
    for serial_port in serial_port_array:
        thread = Thread(target=target, args=(serial_port, baud_rate, console_output))
        threads.append(thread)
        thread.start()
    return threads


def config_process(console_output) -> None:
    serial_parallel_process(target=Device.start_dev)

    serial_parallel_process(target=Device.set_config_on_device)

    _parallel_process(target=Config.check_config_discrepancy, console_output=console_output)
    time.sleep(5)

    serial_parallel_process(target=Device.reset_dev)


def main():
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


if __name__ == '__main__':
    main()
