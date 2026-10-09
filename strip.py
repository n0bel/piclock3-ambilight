"""A WS2812 strip on the SPI data line.

The strip reads each bit as a short or a long pulse, and three SPI bits at
2.4 MHz make either one: 100 is a 0, 110 is a 1.  So each byte of color
goes out as three bytes, and SPI does the timing.  That needs no root and
works the same on a Pi 3, 4 and 5.
"""

SPEED = 2400000

# low for longer than the strip needs to take the next frame as new: 300
# microseconds, which newer WS2812B parts want
RESET = bytes(90)


def expand(byte):
    """one byte of color as the three SPI bytes that send it"""
    bits = 0
    for i in range(7, -1, -1):
        bits = (bits << 3) | (0b110 if byte >> i & 1 else 0b100)
    return bits.to_bytes(3, 'big')


TABLE = [expand(b) for b in range(256)]


def encode(frame, order, brightness):
    """a frame as the bytes to send, the colors in the strip's order"""
    pick = ['rgb'.index(c) for c in order]
    out = bytearray(RESET)
    for color in frame:
        for i in pick:
            level = min(max(color[i] * brightness, 0.0), 1.0)
            out += TABLE[int(level * 255 + 0.5)]
    out += RESET
    return bytes(out)


class Strip:

    def __init__(self, device):
        import spidev
        bus, chip = device.rsplit('spidev', 1)[1].split('.')
        self.spi = spidev.SpiDev()
        self.spi.open(int(bus), int(chip))
        self.spi.max_speed_hz = SPEED
        self.spi.mode = 0

    def show(self, data):
        self.spi.writebytes2(data)

    def close(self):
        self.spi.close()
