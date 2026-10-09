"""What each LED shows at a moment, for each effect.

A frame is a list of (red, green, blue), each 0 to 1, one per LED.  Nothing
here knows about the strip or the clock, so an effect can be tried on any
machine.
"""
import math

DARK = (0.0, 0.0, 0.0)


def around(colors, x):
    """the color x of the way around the palette, 0 <= x < 1, blending
    between neighbors and from the last back to the first"""
    place = (x % 1.0) * len(colors)
    index = int(place)
    a = colors[index % len(colors)]
    b = colors[(index + 1) % len(colors)]
    part = place - index
    return tuple(a[i] + (b[i] - a[i]) * part for i in range(3))


def frame(effect, colors, period, count, now):
    """one frame of an effect, now in seconds"""
    if effect == 'dark' or not colors:
        return [DARK] * count
    if effect == 'solid':
        return [colors[0]] * count
    if effect == 'gradient':
        return [around(colors, i / count) for i in range(count)]
    if effect == 'turn':
        # PiClock v1's rainbow: the colors move toward the start of the
        # strip, once around in period seconds
        shift = now / period
        return [around(colors, i / count + shift) for i in range(count)]
    if effect == 'breathe':
        step = now / period
        color = colors[int(step) % len(colors)]
        # up from dark and back, smoothly, once per color
        level = (1 - math.cos(2 * math.pi * (step % 1.0))) / 2
        return [tuple(c * level for c in color)] * count
    raise ValueError('no effect called %r' % effect)
