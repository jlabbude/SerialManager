# Abeeway Tracker Configurator

## About
Python project useful if you want to configure multiple serial devices at once through their CLI. Right now, it's designed to be used to configure Abeeway's trackers.
![](https://i.ibb.co/HptPP0S/Screenshot-2024-05-15-15-25-08.png)

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
- 2.4.1

## Known issues
- GUI doesn't stall user action when talking to devices properly, making it able to break communication with serial ports by forcing multiple calls to same serial port
  - (as far as I've looked, this doesn't kill the already established communication)
- Line break (\n) characters are not being rendered properly at integrated terminal
- For some 

## Future goals
- [ ] Support for multiple firmware versions
- [ ] Support for different types of devices
- [ ] Support for flashing the firmware of these devices
