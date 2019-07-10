"""
The Key Forger, a quick and dirty script that implements a custom mapping of keyboard keys
"""

__author__ = 'Giorgio Fabbro'
__copyright__ = 'Copyright (C) 2019 Giorgio Fabbro'
__license__ = 'GNU General Public License v3.0'
__version__ = '1.1.0'


from evdev import ecodes as e, InputDevice, list_devices, UInput, categorize
from evdev.events import InputEvent
import asyncio
import argparse
import json

# Is using the script locally?
# Local mode adds functionalities for the main keyboard (e.g. numbers go through i3wm desktops)
IS_LOCAL = False
main_dev_id = 9

digits_str = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
devices = []  # Global handle to all source devices


async def listen(dev, ui, config):
    if int(dev.path[-1]) == main_dev_id:  # Main device
        async for ev in dev.async_read_loop():
            if e.KEY[ev.code][4:] in digits_str and ev.value == 1:  # Change i3wm desktop
                ui.write_event(InputEvent(ev.sec, ev.usec, ev.type, e.KEY_LEFTALT, 1))  # ALT On
                ui.syn()
                ui.write_event(InputEvent(ev.sec, ev.usec, ev.type, ev.code, 1))  # Digit On
                ui.syn()
                ui.write_event(InputEvent(ev.sec, ev.usec, ev.type, ev.code, 0))  # Digit Off
                ui.syn()
                ui.write_event(InputEvent(ev.sec, ev.usec, ev.type, e.KEY_LEFTALT, 0))  # ALT Off
                ui.syn()
            else:
                ui.write_event(ev)  # Passthrough
    else:  # Secondary device
        async for ev in dev.async_read_loop():
            if ev.code == e.KEY_ESC:  # Safe exit with ESC
                for device in devices:
                    device.ungrab()
                exit()
            elif ev.code == e.KEY_RESERVED:  # Synchronization events
                ui.write_event(ev)
            elif e.KEY[ev.code][4:] in config.keys() and ev.value == 1:  # Detect only keydown of keys in config file
                out_codes = [e.ecodes['KEY_' + code] for code in config[e.KEY[ev.code][4:]]]
                for code in out_codes:
                    new_ev = InputEvent(ev.sec, ev.usec, ev.type, code, 1)
                    ui.write_event(new_ev)
                    ui.syn()
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
        available_devices = [InputDevice(path) for path in list_devices()]
        if len(available_devices) == 0:
            print('No device available, run again with sudo')
        else:
            print('List of all input devices:')
            for device in available_devices:
                print(device.path, device.name, device.phys)
            print('Launch the program again, specifying the input device\'s number as in \"/dev/input/event*\" with the option -d:')
        exit()
    if args.configuration is None:
        print('Please, specify a configuration file')
        exit()

    # Open device, configuration file and UInput
    dev = InputDevice('/dev/input/event' + str(args.device))
    dev.grab()
    devices.append(dev)
    ui = UInput()
    config = {}
    with open(args.configuration) as f:
        config = json.load(f)

    if IS_LOCAL:
        main_dev = InputDevice('/dev/input/event' + str(main_dev_id))
        main_dev.grab()
        devices.append(main_dev)

    for device in devices:
        asyncio.ensure_future(listen(device, ui, config))

    # Main loop
    loop = asyncio.get_event_loop()
    loop.run_forever()
