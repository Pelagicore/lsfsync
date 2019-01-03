#!/usr/bin/env python3

import enum
import json
import subprocess
import time


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
            content = json.load(file)
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


def _pci_debug(command):
    subprocess.run(['/home/root/pci_debug', '-s', '01:00.0', '-b', '0', '-c', command])


def _write_telltales(value):
    _pci_debug('C 0x2404 ' + hex(value))


def _write_ui_keep_alive(value):
    _pci_debug('C 0x2400 ' + hex(value))


def main():
    while True:
        _write_telltales(_telltales_from_json_dump())
        _write_ui_keep_alive(9)
        time.sleep(0.4)
        _write_ui_keep_alive(10)
        time.sleep(0.4)


if __name__ == '__main__':
    main()
