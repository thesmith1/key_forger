"""
The Key Forger, a quick and dirty script that performs a many-to-many mapping of keyboard keys
"""

__author__ = 'Giorgio Fabbro'
__copyright__ = 'Copyright (C) 2019 Giorgio Fabbro'
__license__ = 'GNU General Public License v3.0'
__version__ = '1.0'


from evdev import ecodes as e, InputDevice, list_devices, UInput, categorize
from evdev.events import InputEvent
import asyncio
import argparse
import json


async def listen(dev, ui, config):
    async for ev in dev.async_read_loop():
        if ev.code == e.KEY_ESC:  # Safe exit with ESC
            dev.ungrab()
            exit()
        elif ev.code == e.KEY_RESERVED:  # Synchronization events
            ui.write_event(ev)
            ui.syn()
        elif e.KEY[ev.code][4:] in config.keys() and ev.value == 1:  # Detect only keydown of keys in config file
            out_codes = [e.ecodes['KEY_' + code] for code in config[e.KEY[ev.code][4:]]]
            for code in out_codes:
                new_ev = InputEvent(ev.sec, ev.usec, ev.type, code, 1)
                ui.write_event(new_ev)
            for code in reversed(out_codes):
                new_ev = InputEvent(ev.sec, ev.usec, ev.type, code, 0)
                ui.write_event(new_ev)
            ui.syn()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Map keyboard keys.')
    parser.add_argument('-d', '--device', type=int, help='The number of the device')
    parser.add_argument('-c', '--configuration', type=str, help='The path to the configuration file')

    args = parser.parse_args()

    # Manage missing args
    if args.device is None:
        devices = [InputDevice(path) for path in list_devices()]
        if len(devices) == 0:
            print('No device available, run again with sudo')
        else:
            print('List of all input devices:')
            for device in devices:
                print(device.path, device.name, device.phys)
            print('Launch the program again, specifying the input device\'s number as in \"/dev/input/event*\" with the option -d:')
        exit()
    if args.configuration is None:
        print('Please, specify a configuration file')
        exit()

    # Open device, configuration file and UInput
    dev = InputDevice('/dev/input/event' + str(args.device))
    dev.grab()
    ui = UInput()
    config = {}
    with open(args.configuration) as f:
        config = json.load(f)

    # Main loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(listen(dev, ui, config))
