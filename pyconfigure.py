import serial
import glob
import threading
import re
import time
from cfgdicts import abeewaycfgdict

baud_rate = 9600
serial_port_array = glob.glob("/dev/ttyACM*")
config_file = 'configlong.cfg'

def get_deveui(serial_port, baud_rate):
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        ser.write(b'123\r')
        ser.write(b'lora info\r')
        output = ser.read(500).decode('utf-8')
        p = re.compile(r"DevEUI: (.*)")
        return p.search(output).group(1)

def set_config_on_device(serial_port, baud_rate):
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        ser.write(b'123\r')
        #ser.write(b'system skip\r')
        #time.sleep(5)
        with open(config_file, 'rb') as config:
            for line in config:
                ser.write(line.strip())
                ser.write(b'\r')
    ser.close()
    print("config set %s" % serial_port)
        #ser.write(b'system reset\r')

def get_config_value_from_dev(config, parameter):
    if parameter is not None:
        match_line = re.search(r".*%s\s*=\s*(\d+)" % parameter, config)
        #print(match_line)
        #print(match_line.group(1))
        return int(match_line.group(1))

def config_show_at_device(serial_port, baud_rate):
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        ser.write(b'123\r')
        ser.write(b'config show\r')
        output = ser.read(8000)
        ser.close()
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

def parallel_process(target):
    threads = []
    for serial_port in serial_port_array:
        thread = threading.Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def check_config_discrepancy(serial_port, baud_rate):
    with open(config_file, 'r') as config:
        for line in config:
            device_config = config_show_at_device(serial_port=serial_port, baud_rate=baud_rate)
            config_parameter_cfg = get_config_parameter_from_cfg(line)
            config_value_cfg = get_config_value_from_cfg(config_parameter_cfg, line)
            config_name = abeewaycfgdict.config_dict.get(config_parameter_cfg)
            config_value_dev = get_config_value_from_dev(device_config, config_name)
            deveui = str(get_deveui(serial_port=serial_port, baud_rate=baud_rate)   )
            if config_parameter_cfg is not None or config_value_cfg is not None:
                if config_value_cfg == config_value_dev:
                    print(f"Done: {deveui}")
                    return True
                else:
                    print(f"Config error: {deveui}")
                    return False

def main():
    #threads = []
    #for serial_port in serial_port_array:
    #    thread = threading.Thread(target=set_config_on_device, args=(serial_port, baud_rate))
    #    threads.append(thread)
    #    thread.start()
    #for thread in threads:
    #    thread.join()

    threads_check = []
    for serial_port in serial_port_array:
        #check_config_discrepancy(serial_port=serial_port, baud_rate=baud_rate)
        thread1 = threading.Thread(target=check_config_discrepancy, args=(serial_port, baud_rate))
        threads_check.append(thread1)
        thread1.start()
    for thread in threads_check:
        thread1.join()

if __name__ == '__main__':
    main()