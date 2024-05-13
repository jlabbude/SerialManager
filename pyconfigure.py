import serial
import glob
import threading
import re
import time
from cfgdicts import abeewaycfgdict

baud_rate = 9600
serial_port_array = glob.glob("/dev/ttyACM*")
config_file = 'configlong.cfg'


def reset_dev(serial_port, br):
    with serial.Serial(serial_port, br, timeout=1) as ser:
        ser.write(b'123\r')

        ser.write(b'system reset\r')
        ser.close()


def start_dev(serial_port, br):
    with serial.Serial(serial_port, br, timeout=1) as ser:
        ser.write(b'123\r')
        ser.write(b'system skip\r')
        time.sleep(5)
        ser.close()


def get_deveui(serial_port, br):
    with serial.Serial(serial_port, br, timeout=1) as ser:
        ser.write(b'123\r')
        ser.write(b'123\r')
        ser.write(b'system log off\r')
        ser.write(b'lora info\r')
        output = ser.read(1000).decode('utf-8')
        p = re.compile(r"DevEUI: (.*)")
        deveui = p.search(output)
        if deveui is not None:
            return deveui.group(1)


def set_config_on_device(serial_port, br):
    with serial.Serial(serial_port, br, timeout=1) as ser:
        ser.write(b'123\r')
        with open(config_file, 'rb') as config:
            for line in config:
                ser.write(line.strip())
                ser.write(b'\r')
        ser.write(b'config save\r')
        ser.write(b'system buzzer 6\r')
        ser.close()


def get_config_value_from_dev(config, parameter):
    if parameter is not None:
        match_line = re.search(r".*%s\s*=\s*(-?\d+)" % parameter, config)
        if match_line is not None:
            return int(match_line.group(1))


def config_show_at_device(serial_port, br):
    with serial.Serial(serial_port, br, timeout=1) as ser:
        ser.write(b'123\r')
        ser.write(b'config show\r')
        output = ser.read(8000)
        ser.close()
        return output.decode('utf-8')


def get_config_value_from_cfg(parameter, line):
    if parameter is not None:
        pattern = r"config set %d (.*)" % parameter
        p = re.compile(pattern)
        match = p.search(line)
        if match:
            return int(match.group(1))


def get_config_parameter_from_cfg(line):
    p = re.compile("config set (.*) ")
    match = p.search(line)
    if match:
        return int(match.group(1))


def parallel_process(target):
    threads = []
    for serial_port in serial_port_array:
        thread = threading.Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def check_config_discrepancy(serial_port, br):
    with open(config_file, 'r') as config:
        for line in config:
            config_parameter_cfg = get_config_parameter_from_cfg(line)
            config_value_cfg = get_config_value_from_cfg(config_parameter_cfg, line)
            config_name = abeewaycfgdict.config_dict.get(config_parameter_cfg)
            deveui = str(get_deveui(serial_port=serial_port, br=br))
            if config_parameter_cfg is not None or config_value_cfg is not None:
                device_config = config_show_at_device(serial_port=serial_port, br=br)
                config_value_dev = get_config_value_from_dev(device_config, config_name)
                if config_value_cfg != config_value_dev:
                    print(f"Config error: {deveui}")
                    print(f"[{config_name} : {config_value_cfg}] -> [{config_value_dev}]")
                    return False
    print(f"Done: {deveui}")
    return True


def main():
    threads = []
    for serial_port in serial_port_array:
        thread = threading.Thread(target=start_dev, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    threads = []
    for serial_port in serial_port_array:
        thread = threading.Thread(target=set_config_on_device, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    threads = []
    for serial_port in serial_port_array:
        thread = threading.Thread(target=check_config_discrepancy, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
