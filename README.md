# Abeeway Tracker Configurator

## About
This is supposed to be a way to easily change the configuration of multiple of Abeeway's smart trackers at once. At the moment it only works on Linux

![](https://i.ibb.co/NC9xHq3/Screenshot-2024-05-15-15-25-08.png)

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
