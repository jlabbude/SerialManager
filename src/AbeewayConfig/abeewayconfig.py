import glob
import threading
import re

from Device import Device
from src.AbeewayConfig import smartbadgecfgdict

baud_rate = 9600
serial_port_array = glob.glob("/dev/ttyACM*")
config_file = 'config/configlong.cfg'


def get_config_value_from_cfg(parameter: int, line: str) -> int:
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


def check_config_discrepancy(serial_port, br):
    device_config = Device.config_show_at_device(serial_port=serial_port, br=br)
    deveui = str(Device.get_deveui(serial_port=serial_port, br=br))
    with open(config_file, 'r') as config:
        for line in config:
            config_parameter_cfg = get_config_parameter_from_cfg(line)
            config_value_cfg = get_config_value_from_cfg(config_parameter_cfg, line)
            config_name = smartbadgecfgdict.config_dict.get(config_parameter_cfg)
            if config_parameter_cfg is not None or config_value_cfg is not None:
                config_value_dev = Device.get_config_value_from_dev(device_config, config_name)
                if config_value_cfg != config_value_dev:
                    print(f"Config error: {deveui}")
                    print(f"[{config_name} : {config_value_cfg}] -> [{config_value_dev}]\n")
                    return False
    print(f"Done: {deveui}")
    return True


def main():
    threads = []
    for serial_port in serial_port_array:
        thread = threading.Thread(target=Device.start_dev, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    threads = []
    for serial_port in serial_port_array:
        thread = threading.Thread(target=Device.set_config_on_device, args=(serial_port, baud_rate, config_file))
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
