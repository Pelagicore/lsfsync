#!/usr/bin/env python3

import enum
import json
import subprocess
import time
import sys


# Values copied from "TellTalePos" enum in some distant source file, in a repo
# far far away (received in mail, no idea where it is defined).
class TelltaleBitPosition(enum.Enum):
    ABS_FAULT = 0
    AIR_BAG = 1
    BRAKE_FAULT = 2
    FOG_LIGHTS = 3
    HIGH_BEAM = 4
    LEFT_TURN = 5
    LOW_BEAM = 6
    PARKING_BREAK = 7
    RIGHT_TURN = 8
    SEAT_BELT = 9
    STABILITY_CONTROL = 10
    TIRE_PRESSURE = 11


_TELLTALE_JSON_KEY_TO_BIT_POSITION = {
    'lowBeamHeadlight': TelltaleBitPosition.LOW_BEAM,
    'highBeamHeadlight': TelltaleBitPosition.HIGH_BEAM,
    'fogLight': TelltaleBitPosition.FOG_LIGHTS,
    'stabilityControl': TelltaleBitPosition.STABILITY_CONTROL,
    'seatBeltFasten': TelltaleBitPosition.SEAT_BELT,
    'leftTurn': TelltaleBitPosition.LEFT_TURN,
    'rightTurn': TelltaleBitPosition.RIGHT_TURN,
    'absFailure': TelltaleBitPosition.ABS_FAULT,
    'parkBrake': TelltaleBitPosition.PARKING_BREAK,
    'tyrePressureLow': TelltaleBitPosition.TIRE_PRESSURE,
    'brakeFailure': TelltaleBitPosition.BRAKE_FAULT,
    'airbagFailure': TelltaleBitPosition.AIR_BAG
}

_TELLTALE_JSON_PATH = '/tmp/lastTelltalesState.json'


def _telltales_from_json_dump() -> int:
    try:
        with open(_TELLTALE_JSON_PATH) as file:
            # Should be just "content = json.load(file)" but file can be corrupt (extra
            # trailing }:s). Not protected against garbage other than } chars...
            content = json.loads(file.read().strip().strip('}') + '}')
    except BaseException:
        return 0

    if not isinstance(content, dict):
        return 0

    bitmask = 0

    for key, value in content.items():
        if key not in _TELLTALE_JSON_KEY_TO_BIT_POSITION:
            continue

        bit_position = _TELLTALE_JSON_KEY_TO_BIT_POSITION[key]
        mask = 1 << bit_position.value

        if value:
            bitmask |= mask
        else:
            bitmask &= ~mask

    return bitmask


def _pci_debug(command, target_bdf):
    subprocess.run(['pci_debug', '-s {}'.format(target_bdf), '-b', '0', '-c', command])


def _write_telltales(value, target_bdf):
    _pci_debug('C 0x2404 ' + hex(value), target_bdf)


def _write_ui_keep_alive(value, target_bdf):
    _pci_debug('C 0x2400 ' + hex(value), target_bdf)


def main():
    pci_vendor = "8086"
    pci_device = "fffd"
    lspci_result = subprocess.run(["lspci", "-d {}:{}".format(pci_vendor, pci_device)], stdout=subprocess.PIPE)
    target_bdf = lspci_result.stdout.decode().split(" ")[0]

    if (not ":" in target_bdf) or (not "." in target_bdf):
        print("Could not find any PCI device with vendor:device = {}:{} aborting!".format(pci_vendor, pci_device))
        sys.exit(1)

    while True:
        _write_telltales(_telltales_from_json_dump(), target_bdf)
        _write_ui_keep_alive(9, target_bdf)
        time.sleep(0.4)
        _write_ui_keep_alive(10, target_bdf)
        time.sleep(0.4)


if __name__ == '__main__':
    main()
