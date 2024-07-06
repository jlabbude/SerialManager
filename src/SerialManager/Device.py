import os
import re
from time import sleep

from serial import Serial

from SerialManager.Config import Config


class Device:

    # TODO find a way to choose which password to use.
    # Right now the current dilemma stands:
    # -> can't know if device has been configured (and thus, had its password altered) without knowing its DevEUI;
    # -> can't know DevEUI without inputting password first;
    # -> can't input password without knowing which one to use.
    @staticmethod
    def input_password(ser: Serial) -> None:
        new_pass = Config.get_new_pass()
        ser.write(b'123\r')
        ser.write(b'123\r')
        ser.write(new_pass)
        ser.write(new_pass)

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
    def get_deveui(serial_port: str, br: int) -> str:
        with Serial(serial_port, br, timeout=1) as ser:
            Device.input_password(ser)
            ser.write(b'lora info\r')
            output = ser.read(1000).decode('utf-8')
            p = re.compile(r"DevEUI: (.*)")
            deveui = p.search(output)
            if deveui is not None:
                deveui_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "deveui.txt")
                deveui = deveui.group(1).strip()
                if os.path.isfile(deveui_file):
                    with open(deveui_file, 'r+') as deveui_log:
                        deveui_log_content = deveui_log.read().splitlines()
                        if deveui not in deveui_log_content:
                            deveui_log.write(deveui + "\n")
                else:
                    with open(deveui_file, 'a') as deveui_log:
                        deveui_log.write(deveui + "\n")
                return deveui
            else:
                Device.get_deveui(serial_port=serial_port, br=br)

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
            ser.write(b'system buzzer 6\r')
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
