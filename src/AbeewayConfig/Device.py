import serial
import re
from time import sleep

config_file = 'config/configlong.cfg'


class Device:
    def reset_dev(serial_port: str, br: int) -> None:
        with serial.Serial(serial_port, br, timeout=1) as ser:
            ser.write(b'123\r')
            ser.write(b'system reset\r')
            ser.close()

    def start_dev(serial_port: str, br: int) -> None:
        with serial.Serial(serial_port, br, timeout=1) as ser:
            ser.write(b'123\r')
            ser.write(b'system skip\r')
            sleep(6)
            ser.write(b'system log off\r')
            ser.close()

    def get_deveui(serial_port: str, br: int) -> int:
        with serial.Serial(serial_port, br, timeout=1) as ser:
            ser.write(b'123\r')
            ser.write(b'123\r')
            ser.write(b'lora info\r')
            output = ser.read(1000).decode('utf-8')
            p = re.compile(r"DevEUI: (.*)")
            deveui = p.search(output)
            if deveui is not None:
                return deveui.group(1)

    def set_config_on_device(serial_port: str, br: int) -> None:
        with serial.Serial(serial_port, br, timeout=1) as ser:
            ser.write(b'123\r')
            with open(config_file, 'rb') as config:
                for line in config:
                    ser.write(line.strip())
                    ser.write(b'\r')
            ser.write(b'config save\r')
            ser.write(b'system buzzer 6\r')
            ser.close()

    # This doesn't actually talk to the device directly, rather it just grabs the value from a string
    # Might move it back to the main module
    def get_config_value_from_dev(config_name: str, parameter: int) -> int:
        if parameter is not None:
            match_line = re.search(r".*%s\s*=\s*(-?\d+)" % parameter, config_name)
            if match_line is not None:
                return int(match_line.group(1))

    def config_show_at_device(serial_port: str, br: int) -> str:
        with serial.Serial(serial_port, br, timeout=1) as ser:
            ser.write(b'123\r')
            ser.write(b'config show\r')
            output = ser.read(8000)
            ser.close()
            return output.decode('utf-8')
