# Abeeway Tracker Configurator

## About
Python project useful if you want to configure multiple serial devices at once through their CLI. Right now, it's designed to be used to configure Abeeway's trackers.

![](https://i.ibb.co/HptPP0S/Screenshot-2024-05-15-15-25-08.png)

## Installation

To install I recommend you use the package installer for Python - **pip**

```bash
  pip install abeewayconfig
```

## Usage

```bash
  abeewayconfig config
```

Run this command to open the GUI related to device configuring.

```bash
 abeewayconfig upload
```

Run this command to open the GUI related to building a CSV to upload info about the configured devices to a cloud service, in this case, ThingPark.

## Compatibility

### Operating Systems
- Linux
  - Arch
- Windows
  - W11

### Devices
- Abeeway Smart Badge
  - A310
  - U310

### Firmware Version
- Smart Badge U310/A310
  - 2.4.1

## Known issues
- GUI doesn't stall user action when talking to devices properly, making it able to break communication with serial ports by forcing multiple calls to same serial port
  - (as far as I've looked, this doesn't kill the already established communication)

## Future goals
- [ ] Support for multiple firmware versions
- [ ] Support for different types of devices
- [ ] Support for flashing the firmware of these devices
