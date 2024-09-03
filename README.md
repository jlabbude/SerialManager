# Serial Device Manager

## About
**Python package made primarily to automate tasks related to configuring serial devices, and uploading them to cloud services.**

> [!WARNING]
> Right now it only supports the creation and implementation of configs to Abeeway's Smart Badge, and the ability to upload devices to ThingPark Community.

![Configuring window](https://i.ibb.co/HptPP0S/Screenshot-2024-05-15-15-25-08.png)
![Config creation window](https://i.ibb.co/xGx9Yfy/Screenshot-20240714-190949.png)

## Installation

To install I recommend you use the package installer for Python - **pip**

```bash
  pip install serialmanager
```

## Usages

```bash
  serialmgr abeeway config
```

Run this command to open the GUI related to device configuring.

---

```bash
 serialmgr abeeway upload
```

Run this command to open the GUI related to building a CSV to upload info about the configured devices to a cloud service, in this case, ThingPark.

---

```bash
 serialmgr abeeway create-cfg
```

Run this command to open the GUI related to creating a config file. **Firmware 2.4-1**

## Compatibility

### Operating Systems
> [!NOTE]
> This doesn't mean another Windows version or Linux Distro isn't going to work, it's just that I haven't tested anywhere else
- Linux
  - Arch (**KDE**/**XFCE**)
- Windows
  - 11

### Devices
- Abeeway Smart Badge
  - A310
  - U310

### Firmware Version
> [!NOTE]
> Other firmware versions work, but since configs values/parameters come and go with each version, the application's behaviour may vary depending on which version you have.

- Smart Badge U310/A310
  - 2.4.1

## Known issues
- GUI doesn't stall user action when talking to devices properly, making it able to break communication with serial ports by forcing multiple calls to same serial port
  - (as far as I've looked, this doesn't kill the already established communication)
- Start device command is fairly unstable for reasons unknown at the moment
- Devices with firmware versions above or below 2.4-1 will report config error due to not having that config parameter 

## Future goals
- [X] Change config file to yaml from cfg and add GUI to manipule it
- [X] Add search bar to `create-cfg`
- [ ] Automate join process
- [ ] Language selection
- [ ] Support for multiple firmware versions
- [ ] Support for different types of devices
- [ ] Support for flashing the firmware of these devices
