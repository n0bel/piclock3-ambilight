# piclock3-ambilight

A strip of WS2812 LEDs behind a
[PiClock3](https://github.com/n0bel/PiClock3), lit to go with it.  PiClock
v1 turned a rainbow around its strip once a minute, and that's the look
this starts with.

The effects and the bits sent to the strip are tested.  It hasn't lit a
real strip yet.

## Looks, effects and palettes

A **look** is what the strip shows: an effect, the palette it draws with,
and how fast it moves.

```yaml
looks:
  rainbow: {effect: turn, palette: rainbow, period: 60}
```

An **effect** is how the colors move:

| effect | |
|---|---|
| `dark` | no light |
| `solid` | the palette's first color |
| `gradient` | the palette spread along the strip, still |
| `turn` | that gradient moving along the strip, once around in `period` seconds |
| `breathe` | each color fading up and down in turn, one every `period` seconds |

A **palette** is a list of colors, by name or as `'#ff6a00'`.  Any effect
draws in any palette, so a few effects and a few palettes make a lot of
looks.

These ship, and a config adds its own beside them:

| look | effect | palette |
|---|---|---|
| `rainbow` | turn, a minute | red, yellow, lime, cyan, blue, magenta |
| `sunset` | breathe, 8 seconds | orange, rose, purple |
| `ocean` | turn, 30 seconds | three blues |
| `warm` | solid | a warm white |
| `night` | solid | a dim red |
| `dark` | dark | |

## Naming it in a config

It's a service: it draws nothing on the screen, so it goes under
`services:` and takes no region.

```yaml
services:
  ambilight:
    plugin: plugins.Ambilight
    leds: 27
    look: rainbow
    pages:
      night-page: night
    palettes:
      harbor: ['#003049', '#d62828', '#f77f00', '#fcbf49']
    looks:
      harbor: {effect: turn, palette: harbor, period: 20}
```

| setting | |
|---|---|
| `leds` | how many LEDs the strip has |
| `look` | the look on every page `pages` doesn't name |
| `pages` | a look for a page, by the page's name |
| `palettes` | palettes of your own, beside the ones that ship |
| `looks` | looks of your own, beside the ones that ship |
| `brightness` | 0 to 1, and 0.5 unless you say |
| `order` | the order the strip takes red, green and blue in, `grb` for most |
| `device` | the SPI device, `/dev/spidev0.0` |
| `rate` | frames a second, 30 |

`examples/ambilight.yaml` is a clock of two pages, each with its own look.

## Wiring

The strip's data line goes to the SPI data pin, **GPIO10, header pin 19**,
and its ground to a ground pin, such as **pin 20**.

**Power the strip from its own 5V supply,** not from the Pi.  Each LED can
draw 60 mA at full white, so 27 of them can want 1.6 A.  Join the supply's
ground to the Pi's.

A WS2812 wants its data at 5V, and the Pi gives 3.3V.  Many strips take it
anyway.  If yours flickers or shows wrong colors, a 74AHCT125 between the
pin and the strip lifts the data to 5V.

## Installing

Needs PiClock3 2026.10.09 or later.  Then, on the Pi:

```
cd ~/PiClock3
git clone https://github.com/n0bel/piclock3-ambilight plugins/Ambilight
sudo apt install python3-spidev
```

python3-spidev comes with Raspberry Pi OS, so apt usually has nothing to
do.  SPI has to be turned on, with a line in `/boot/firmware/config.txt`
(`/boot/config.txt` on Bullseye):

```
dtparam=spi=on
```

**Hold the core clock still,** on a Pi 3 or 4.  The SPI clock is divided
from it, and left alone it changes, and with it the timing the strip
reads.  On a Pi 3:

```
core_freq=250
```

On a Pi 4:

```
core_freq=500
core_freq_min=500
```

Then reboot.  Your user has to be in the `spi` group, as the first user
on Raspberry Pi OS is.  The Pi 5 hasn't been tried.

**More than 435 LEDs** is more than spidev sends at once unless it's told
otherwise.  Add `spidev.bufsiz=65536` to the end of the line in
`/boot/firmware/cmdline.txt`, and reboot.

## Tests

```
python3 tests/effectstest.py
```

## How it drives the strip

A WS2812 reads each bit as a short or a long pulse.  Three SPI bits at
2.4 MHz make either one, `100` for a 0 and `110` for a 1, so SPI does the
timing.  That needs no root, no compiled library, and works the same on a
Pi 3, 4 and 5.  PiClock v1 used rpi_ws281x, which needs root, and on a
Pi 5 a kernel module too.

## License

MIT, the same as PiClock3.
