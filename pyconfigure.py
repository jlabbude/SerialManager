import serial
import glob
import threading
import re
import time
from cfgdicts import abeewaycfgdict

baud_rate = 9600
serial_port_array = glob.glob("/dev/ttyACM*")
config_file = 'config.cfg'

def set_config_on_device(serial_port, baud_rate):
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        ser.write(b'123\r')
        #ser.write(b'system skip\r')
        #time.sleep(5)
        with open(config_file, 'rb') as config:
            for line in config:
                ser.write(line.strip())
                ser.write(b'\r')
        #ser.write(b'system reset\r')

def get_config_value_from_dev(config, parameter):
    if parameter is not None:
        match_line = re.search(r".*%s\s*=\s*(\d+)" % parameter, config)
        return int(match_line.group(1))

def config_show_at_device(serial_port, baud_rate):
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        ser.write(b'123\r')
        ser.write(b'config show\r')
        output = ser.read(8000)
        return output.decode('utf-8')

def get_config_value_from_cfg(parameter, line):
    if parameter is not None:
        pattern = r"config set %d (.*)" % parameter
        p = re.compile(pattern)
        match  = p.search(line)
        if match:
            return int(match.group(1))

def get_config_parameter_from_cfg(line):
    p = re.compile("config set (.*) ")
    match = p.search(line)
    if match:
        return int(match.group(1))

def parallel_process(target, args):
    threads = []
    for serial_port in serial_port_array:
        thread = threading.Thread(target=target, args=args)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def check_config_discrepancy():
    for serial_port in serial_port_array:
        with open(config_file, 'r') as config:
            for line in config:
                device_config = config_show_at_device(serial_port=serial_port, baud_rate=baud_rate)
                config_parameter_cfg = get_config_parameter_from_cfg(line)
                config_value_cfg = get_config_value_from_cfg(config_parameter_cfg, line)
                config_name = abeewaycfgdict.config_dict.get(config_parameter_cfg)
                config_value_dev = get_config_value_from_dev(device_config, config_name)
                if config_parameter_cfg is not None or config_value_cfg is not None:
                    print(config_value_cfg == config_value_dev, config_name, config_value_dev)

def main():
    for serial_port in serial_port_array:
        parallel_process(target=set_config_on_device, args=(serial_port, baud_rate))
        print("config set")
        check_config_discrepancy()

if __name__ == '__main__':
    main()