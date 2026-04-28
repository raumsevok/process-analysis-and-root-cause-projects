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

## AI assistance note

Parts of the code were developed with assistance from OpenAI Codex. The project idea, testing, measurements, evaluation, and documentation were done by Thomas Ganslmeier.
