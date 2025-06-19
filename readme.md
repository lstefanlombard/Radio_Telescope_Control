# Telescope Control Script

This script provides a GUI for controlling an ASCOM-compatible telescope mount via the ASCOM platform. The GUI allows you to set RA/Dec coordinates, scan sizes, step sizes, and scan time. You can also retrieve RA and Dec values from Stellarium.

## Prerequisites
- Python 3.x
- ASCOM Platform (download from [ASCOM Standards](https://ascom-standards.org/))
- ASCOM driver for your specific telescope mount
- Required Python packages:
  - `pywin32` for ASCOM communication
  - `tkinter` for the GUI
  - `requests` for Stellarium API integration
  - `watchdog` for file monitoring
  - `csv` for data logging

## Installation
1. Install the required Python packages:
```bash
pip install pywin32 watchdog requests
```
2. Download and install the ASCOM Platform from the official website.
3. Install the appropriate ASCOM driver for your telescope mount.

## Usage
1. Edit the script to use your mount's ASCOM ProgID:
   ```python
   My_Mount="ASCOM.OnStep.Telescope"
   ```
   Replace `"ASCOM.OnStep.Telescope"` with your mount's driver ProgID.

2. Run the script:
   ```bash
   python telescope_control.py
   ```
3. Use the GUI to set coordinates, scan sizes, and start the scan.

## Troubleshooting
- If the script fails to connect to the mount, ensure that:
  - The ASCOM Platform and the correct driver are installed.
  - You have selected the correct ProgID for your mount.
  - You have the necessary permissions to access COM objects.

## Attribution
Written by lstefanlombard

## Also see
[HLine3D](https://github.com/AP-HLine-3D/HLine3D)



