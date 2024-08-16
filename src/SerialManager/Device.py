import os
import re
from time import sleep

import tkinter as tk
from SerialManager import ConsoleButtons
from serial import Serial

from SerialManager.Config import Config


class Device:

    # TODO find a way to choose which password to use.
    # Right now the current dilemma stands:
    # -> can't know if device has been configured (and thus, had its password altered) without knowing its DevEUI;
    # -> can't know DevEUI without inputting password first;
    # -> can't input password without knowing which one to use.

    def __init__(self, gui_instance: ConsoleButtons, root: tk.Tk):
        self.gui = gui_instance
        self.root = root

    @staticmethod
    def input_password(ser: Serial) -> None:
        new_pass = Config.get_new_pass()
        ser.write(b'123\r')
        ser.write(b'123\r')
        ser.write(new_pass)
        ser.write(new_pass)
        ser.write(b'system log off\r')

    @staticmethod
    def reset_dev(serial_port: str, br: int) -> None:
        with Serial(serial_port, br, timeout=1) as ser:
            Device.input_password(ser)
            ser.write(b'system reset\r')
            ser.close()

    @staticmethod
    def start_dev(serial_port: str, br: int) -> None:
        with Serial(serial_port, br, timeout=1) as ser:
            Device.input_password(ser)
            ser.write(b'system skip\r')
            sleep(6)
            ser.write(b'system log off\r')
            output = ser.read(1000).decode('utf-8')
            match = re.search(r"user>", output)
            if not match:
                ser.close()
                Device.start_dev(serial_port=serial_port, br=br)

    @staticmethod
    def alarm(serial_port: str, br: int) -> None:
        with Serial(serial_port, br) as ser:
            Device.input_password(ser)
            ser.write(b'system buzzer 10\r')

    def start_or_reset(self) -> None:
        from SerialManager.main import serial_parallel_process
        file_dialog = tk.Toplevel(self.root)
        file_dialog.title("Select")
        tk.Label(file_dialog, text="Start or reset?").pack(pady=10)
        (tk.Button(file_dialog,
                   text="Start",
                   command=lambda: serial_parallel_process(target=Device.start_dev),
                   bg='lightgreen')
         .pack(side="left", padx=20, pady=20))
        (tk.Button(file_dialog,
                   text="Reset",
                   command=lambda: serial_parallel_process(target=Device.reset_dev),
                   bg='lightcoral')
         .pack(side="right", padx=20, pady=20))

    @staticmethod
    def get_deveui(serial_port: str, br: int) -> str:
        with Serial(serial_port, br, timeout=1) as ser:
            Device.input_password(ser)
            ser.write(b'lora info\r')
            output = ser.read(1000).decode('utf-8')
            p = re.compile(r"DevEUI: (.*)")
            deveui = p.search(output)
            return deveui.group(1).strip() if deveui is not None else Device.get_deveui(serial_port=serial_port, br=br)

    @staticmethod
    def set_config_on_device(serial_port: str, br: int) -> None:
        with Serial(serial_port, br, timeout=1) as ser:
            Device.input_password(ser)
            config_file = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils"), "config.cfg")
            with open(config_file, 'rb') as config:
                for line in config:
                    ser.write(line.strip())
                    ser.write(b'\r')
            ser.write(b'config save\r')
            ser.write(b'system buzzer 8\r')
            ser.close()

    # This doesn't actually talk to the device directly, rather it just grabs the value from a string
    # Might move it back to the main module
    @staticmethod
    def get_config_value_from_dev(config_name: str, parameter: int) -> int:
        if parameter is not None:
            match_line = re.search(r".*\s+%s\s*=\s*(-?\d+)" % parameter, config_name)
            if match_line is not None:
                return int(match_line.group(1))

    @staticmethod
    def config_show_at_device(serial_port: str, br: int) -> str:
        with Serial(serial_port, br, timeout=1) as ser:
            Device.input_password(ser)
            ser.write(b'system log off\r')
            ser.write(b'config show\r')
            output = ser.read(16000)
            ser.close()
            return output.decode('utf-8')
