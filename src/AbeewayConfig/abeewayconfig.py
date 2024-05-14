import glob
import threading
import tkinter

from Config import Config
from Device import Device

baud_rate = 9600
serial_port_array = glob.glob("/dev/ttyACM*")


def serial_parallel_process(target):
    threads = []
    for serial_port in serial_port_array:
        thread = threading.Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def config_process() -> None:
    serial_parallel_process(target=Device.start_dev)

    serial_parallel_process(target=Device.set_config_on_device)

    serial_parallel_process(target=Config.check_config_discrepancy)

    serial_parallel_process(target=Device.reset_dev)


if __name__ == '__main__':
    main()
