Bluetooth Signal Live

Small console program that shows the live Bluetooth signal strength of a
connected headset.

Tested setup

Headset: Bose NC 700 HP
MAC address: C8:7B:23:5C:41:E4
Required tools: bluetoothctl, hcitool, pactl, spd-say

Requirements

No Python packages from pip are required.

Install the required system packages on Ubuntu, Linux Mint, or Debian-based
systems:

sudo apt update
sudo apt install python3 bluez pulseaudio-utils speech-dispatcher

Package details:

bluetoothctl and hcitool are included in bluez.
pactl is included in pulseaudio-utils.
spd-say is included in speech-dispatcher.

Start

Run the program:

python3 bt_signal_live.py

Run it directly with the Bose headset:

python3 bt_signal_live.py C8:7B:23:5C:41:E4

Speech Output

Read the current signal value aloud:

python3 bt_signal_live.py --speak

Only the number is spoken, for example -2 or 0.

By default, speech output is routed to the monitor or HDMI audio output.

Use the normal default audio output instead:

python3 bt_signal_live.py --speak --speak-sink default

Refresh Speed

Refresh twice per second:

python3 bt_signal_live.py --interval 0.5

Refresh every two seconds:

python3 bt_signal_live.py --interval 2

Stop

Press Ctrl+C to stop the program.

Note

For classic Bluetooth audio headsets, hcitool rssi usually returns a relative
RSSI link value in dB. It is not an absolutely calibrated dBm value.
