#!/usr/bin/env python3

import enum
import json


# Values copied from "TellTalePos" enum in some distant source file, in a repo
# far far away (received in mail, no idea where it is defined).
class BitPosition(enum.Enum):
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


_JSON_KEY_TO_BIT_POSITION = {
    'lowBeamHeadlight': BitPosition.LOW_BEAM,
    'highBeamHeadlight': BitPosition.HIGH_BEAM,
    'fogLight': BitPosition.FOG_LIGHTS,
    'stabilityControl': BitPosition.STABILITY_CONTROL,
    'seatBeltFasten': BitPosition.SEAT_BELT,
    'leftTurn': BitPosition.LEFT_TURN,
    'rightTurn': BitPosition.RIGHT_TURN,
    'absFailure': BitPosition.ABS_FAULT,
    'parkBrake': BitPosition.PARKING_BREAK,
    'tyrePressureLow': BitPosition.TIRE_PRESSURE,
    'brakeFailure': BitPosition.BRAKE_FAULT,
    'airbagFailure': BitPosition.AIR_BAG
}

_NEPTUNE_JSON_PATH = '/tmp/lastTelltalesState.json'


def from_neptune_json_dump() -> int:
    with open(_NEPTUNE_JSON_PATH) as file:
        content = json.load(file)

    if not isinstance(content, dict):
        return 0

    bitmask = 0

    for key, value in content.items():
        bit_position = _JSON_KEY_TO_BIT_POSITION[key]
        mask = 1 << bit_position.value

        if value:
            bitmask |= mask
        else:
            bitmask &= ~mask

    return bitmask


def main():
    print(from_neptune_json_dump())


if __name__ == '__main__':
    main()
