#!/usr/bin/env python3
import argparse
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime


MAC_RE = re.compile(r"Device\s+([0-9A-Fa-f:]{17})\s+(.+)")
RSSI_RE = re.compile(r"RSSI return value:\s*(-?\d+)")


def run(command, timeout=5):
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def run_quiet(command, timeout=5):
    return subprocess.run(
        command,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )


def require_tool(name):
    if shutil.which(name) is None:
        print(f"Missing: {name} is not installed or not in PATH.", file=sys.stderr)
        sys.exit(2)


def available_tool(name):
    return shutil.which(name) is not None


def connected_devices():
    result = run(["bluetoothctl", "devices", "Connected"])
    devices = []
    for line in result.stdout.splitlines():
        match = MAC_RE.search(line.strip())
        if match:
            devices.append((match.group(1).upper(), match.group(2).strip()))
    return devices


def device_info(mac):
    result = run(["bluetoothctl", "info", mac])
    return result.stdout


def choose_device(requested_mac=None, requested_name=None):
    devices = connected_devices()
    if requested_mac:
        mac = requested_mac.upper()
        for device_mac, name in devices:
            if device_mac == mac:
                return device_mac, name
        return mac, "(specified device)"

    if requested_name:
        needle = requested_name.lower()
        matches = [(mac, name) for mac, name in devices if needle in name.lower()]
        if matches:
            return matches[0]

    if not devices:
        print("No connected Bluetooth device found.", file=sys.stderr)
        print("Connect your headset and start the program again.", file=sys.stderr)
        sys.exit(1)

    audio_candidates = []
    for mac, name in devices:
        info = device_info(mac)
        if "Icon: audio" in info or "Audio Sink" in info or "Headset" in info:
            audio_candidates.append((mac, name))

    if len(audio_candidates) == 1:
        return audio_candidates[0]
    if audio_candidates:
        return audio_candidates[0]
    return devices[0]


def read_rssi(mac):
    result = run(["hcitool", "rssi", mac], timeout=3)
    output = (result.stdout + result.stderr).strip()
    match = RSSI_RE.search(output)
    if not match:
        raise RuntimeError(output or "no RSSI value received")
    return int(match.group(1))


def quality_label(rssi):
    if rssi >= 8:
        return "very strong"
    if rssi >= 0:
        return "strong"
    if rssi >= -6:
        return "medium"
    if rssi >= -12:
        return "weak"
    return "very weak"


def bar(rssi, width=28):
    # Classic Bluetooth reports a relative RSSI around the receiver's ideal range.
    minimum, maximum = -20, 12
    clipped = max(minimum, min(maximum, rssi))
    filled = round((clipped - minimum) / (maximum - minimum) * width)
    return "#" * filled + "-" * (width - filled)


def clear_screen():
    print("\033[2J\033[H", end="")


def default_sink():
    if not available_tool("pactl"):
        return None
    result = run(["pactl", "get-default-sink"])
    sink = result.stdout.strip()
    return sink or None


def monitor_sink():
    if not available_tool("pactl"):
        return None
    result = run(["pactl", "list", "short", "sinks"])
    sinks = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            sinks.append(parts[1])
    for sink in sinks:
        if "hdmi" in sink.lower():
            return sink
    return default_sink()


def speech_sink_inputs():
    result = run(["pactl", "list", "short", "sink-inputs"], timeout=2)
    inputs = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if parts and parts[0].isdigit():
            inputs.append(parts[0])
    return inputs


def move_new_speech_inputs(before_inputs, sink):
    if not sink or not available_tool("pactl"):
        return
    before = set(before_inputs)
    deadline = time.time() + 1.0
    while time.time() < deadline:
        current = speech_sink_inputs()
        new_inputs = [input_id for input_id in current if input_id not in before]
        if new_inputs:
            for input_id in new_inputs:
                run_quiet(["pactl", "move-sink-input", input_id, sink], timeout=2)
            return
        time.sleep(0.05)


def say_number(number, sink=None):
    before_inputs = speech_sink_inputs() if sink else []
    process = subprocess.Popen(
        ["spd-say", "-o", "espeak-ng", "-w", "-r", "20", "--", str(number)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    move_new_speech_inputs(before_inputs, sink)
    return process


def describe_sink(sink):
    if not sink:
        return "default"
    if "hdmi" in sink.lower():
        return "monitor/HDMI"
    return sink


def main():
    parser = argparse.ArgumentParser(
        description="Live display of Bluetooth signal strength for a connected headset."
    )
    parser.add_argument("mac", nargs="?", help="Bluetooth MAC, e.g. C8:7B:23:5C:41:E4")
    parser.add_argument("-n", "--name", help="Part of the device name, useful if multiple devices are connected")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="Refresh interval in seconds")
    parser.add_argument("--speak", action="store_true", help="Read the current RSSI value aloud")
    parser.add_argument(
        "--speak-sink",
        choices=["monitor", "default"],
        default="monitor",
        help="Audio output for --speak",
    )
    parser.add_argument("--once", action="store_true", help="Measure once and exit")
    args = parser.parse_args()

    require_tool("bluetoothctl")
    require_tool("hcitool")
    if args.speak and not available_tool("spd-say"):
        print("Missing: spd-say is required for --speak.", file=sys.stderr)
        print("Install it with e.g.: sudo apt install speech-dispatcher", file=sys.stderr)
        sys.exit(2)
    speak_sink = None
    if args.speak:
        speak_sink = monitor_sink() if args.speak_sink == "monitor" else default_sink()

    mac, name = choose_device(args.mac, args.name)
    running = True

    def stop(_signum, _frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    while running:
        now = datetime.now().strftime("%H:%M:%S")
        try:
            rssi = read_rssi(mac)
            if args.speak:
                say_number(rssi, speak_sink)
            status = quality_label(rssi)
            body = [
                "Bluetooth Signal Live",
                "",
                f"Device:     {name}",
                f"MAC:        {mac}",
                f"Time:       {now}",
                "",
                f"RSSI:       {rssi:+d} dB relative",
                f"Quality:    {status}",
                f"[{bar(rssi)}]",
                "",
                "Quit: Ctrl+C",
            ]
        except Exception as exc:
            body = [
                "Bluetooth Signal Live",
                "",
                f"Device:     {name}",
                f"MAC:        {mac}",
                f"Time:       {now}",
                "",
                f"Error:      {exc}",
                "",
                "Is the headset still connected?",
                "Quit: Ctrl+C",
            ]

        if args.once:
            print("\n".join(body))
            return

        clear_screen()
        print("\n".join(body), flush=True)
        time.sleep(max(0.2, args.interval))

    print("\nStopped.")


if __name__ == "__main__":
    main()
