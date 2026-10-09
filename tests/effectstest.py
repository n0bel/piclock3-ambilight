"""Do the effects draw what they say, and does the strip get the right bits?

    python3 tests/effectstest.py

Neither needs a strip or the clock, so this runs on any machine.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(
    __file__))))

import effects  # noqa: E402
import strip  # noqa: E402

RED, GREEN, BLUE = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)


def close(a, b):
    return all(abs(x - y) < 1e-9 for x, y in zip(a, b))


CASES = [
    ('dark is no light',
     lambda: effects.frame('dark', [RED], 60, 3, 0) == [effects.DARK] * 3),
    ('solid is the first color',
     lambda: effects.frame('solid', [RED, BLUE], 60, 4, 0) == [RED] * 4),
    ('around blends halfway between neighbors',
     lambda: close(effects.around([RED, GREEN], 0.25), (0.5, 0.5, 0))),
    ('around goes from the last back to the first',
     lambda: close(effects.around([RED, GREEN], 0.75), (0.5, 0.5, 0))),
    ('gradient starts on the first color',
     lambda: effects.frame('gradient', [RED, GREEN, BLUE], 60, 6, 0)[0]
     == RED),
    ('gradient reaches each color in turn',
     lambda: close(effects.frame('gradient', [RED, GREEN, BLUE], 60, 6,
                                 0)[2], GREEN)),
    ('turn moves the colors toward the start of the strip',
     lambda: close(effects.frame('turn', [RED, GREEN, BLUE], 60, 6, 20)[0],
                   GREEN)),
    ('turn is back where it started after a period',
     lambda: close(effects.frame('turn', [RED, GREEN], 60, 4, 60)[0], RED)),
    ('breathe is dark at the start of a color',
     lambda: close(effects.frame('breathe', [RED], 8, 2, 0)[0],
                   effects.DARK)),
    ('breathe is full halfway through',
     lambda: close(effects.frame('breathe', [RED], 8, 2, 4)[0], RED)),
    ('breathe moves to the next color after a period',
     lambda: close(effects.frame('breathe', [RED, BLUE], 8, 2, 12)[0],
                   BLUE)),
    ('a 1 is sent as 110, a 0 as 100',
     lambda: strip.expand(0b10000000) == bytes([0b11010010, 0b01001001,
                                                0b00100100])),
    ('0 is all short pulses',
     lambda: strip.expand(0) == bytes([0b10010010, 0b01001001,
                                       0b00100100])),
    ('a frame is three bytes per color, between the resets',
     lambda: len(strip.encode([RED] * 5, 'grb', 1))
     == 5 * 9 + 2 * len(strip.RESET)),
    ('grb sends green first',
     lambda: strip.encode([RED], 'grb', 1)[len(strip.RESET):][:3]
     == strip.TABLE[0]),
    ('brightness scales each color',
     lambda: strip.encode([RED], 'rgb', 0.5)[len(strip.RESET):][:3]
     == strip.TABLE[128]),
]


def main():
    failed = 0
    for name, test in CASES:
        ok = test()
        failed += not ok
        print('  %s  %s' % ('ok  ' if ok else 'FAIL', name))
    print('%d cases, %d failed' % (len(CASES), failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
