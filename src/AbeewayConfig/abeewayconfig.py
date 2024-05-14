from glob import glob
from threading import Thread
import tkinter

from Config import Config
from Device import Device

baud_rate = 9600
serial_port_array = glob("/dev/ttyACM*")


def serial_parallel_process(target):
    threads = []
    for serial_port in serial_port_array:
        thread = Thread(target=target, args=(serial_port, baud_rate))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def config_process() -> None:
    serial_parallel_process(target=Device.start_dev)

    serial_parallel_process(target=Device.set_config_on_device)

    serial_parallel_process(target=Config.check_config_discrepancy)

    serial_parallel_process(target=Device.reset_dev)


def main():
    root = tkinter.Tk()

    root.title("Button Example")

    # Create buttons
    button1 = tkinter.Button(root,
                             text="Config Device",
                             command=lambda: config_process())
    button2 = tkinter.Button(root,
                             text="Reset device",
                             command=lambda: serial_parallel_process(target=Device.reset_dev))
    button3 = tkinter.Button(root,
                             text="Start device",
                             command=lambda: serial_parallel_process(target=Device.start_dev))

    button1.pack()
    button2.pack()
    button3.pack()

    root.mainloop()


if __name__ == '__main__':
    main()
