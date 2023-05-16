# Ivy2

![20230516_133925](https://github.com/dtgreene/ivy2/assets/24302976/1e9d4931-caf8-4aab-a176-1239dbba6856)


A Python API to control the [Canon Ivy 2 mini photo printer](https://www.usa.canon.com/shop/p/ivy-2-mini-photo-printer).

Note: So far, this has only been tested on a Raspberry PI 3b+.  The underlying PyBluez library should be cross-compatible but the pairing process will likely vary from platform to platform.

### Installation steps (Raspberry PI)

1. Install deb packages
```
sudo apt install bluetooth bluez libbluetooth-dev
```

2. Install pip packages
```
pip install -r requirements.txt
```

3. Disable legacy pairing

This will need to be done each time the computer reboots.  Otherwise you may get an "Invalid exchange" error when trying to connect with the printer.

```
sudo hciconfig 0 sspmode 0
```

4. Pair with the printer

This only needs to be done the first time.  

Start the BlueZ CLI 
```
bluetoothctl
```

If this is your first time messing with Bluetooth on the PI, first register an agent:
- `agent on`
- `default-agent`

Turn on the printer and wait abotu 30 seconds. Then enable scanning:
- `scan on`

You should start to see local Bluetooth devices popping up.  Most of the devices will just show a mac address but the printer should have the name listed as well making it easy to spot.  You should see something like this:

```
[NEW] Device 04:7F:0E:B7:46:0B Canon (46:0B) Mini Printer
             ^ mac address
```

Once you've located the printer, take note of the mac address and attempt to pair:
- `pair <mac-addr>`
- `trust <mac-addr>`

You can now disable scanning and exit the BlueZ CLI:
- `scan off`
- `exit`

### Usage

See [example.py](example.py) for basic usage.
