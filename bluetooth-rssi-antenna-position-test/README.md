# Bluetooth RSSI Antenna Position Test

This project documents a measurement-based approach to improve Bluetooth headset reception by comparing different PC antenna positions.

## Problem

The Bluetooth connection to my headset was not stable in all areas of my apartment.

## Goal

The goal was to find an antenna position that provides better Bluetooth reception across the apartment.

## Method

A Python tool was used to display the live Bluetooth RSSI value of the connected headset.

The tool also read the RSSI value aloud during testing. This made it possible to move around the apartment and compare signal strength without constantly looking at the screen.

Different antenna positions were tested. Aluminum foil was also tested as a simple reflector to see whether the signal could be directed into a specific area.

## Result

The aluminum foil did not improve the signal in this setup. In some positions, it made the signal worse.

The best improvement came from changing the antenna position. The measured relative RSSI improved from about -12 dB to about -8 dB.

## What this project shows

This project shows a systematic approach to a technical problem:

- Observe the problem
- Create a measurement method
- Test different conditions
- Compare the results
- Identify what improves the situation
- Choose the best practical solution

## Tools

- Python
- Bluetooth RSSI measurement
- Audio output for live measurement feedback

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

## Note

Parts of the code were developed with assistance from OpenAI Codex. The project idea, testing, measurements, evaluation, and documentation were done by Thomas Ganslmeier.
