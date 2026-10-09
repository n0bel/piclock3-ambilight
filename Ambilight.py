"""A WS2812 strip behind the clock, lit with a look.

A look is an effect, the palette it draws with, and how fast it moves.  The
page being looked at picks the look, so a night page can dim the strip.
"""
import logging
import time

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

from PiClock3.Service import Service

from . import effects
from . import strip

logger = logging.getLogger(__name__)


class Ambilight(Service):

    def __init__(self, piclock, name, config):
        super().__init__(piclock, name, config)
        self.strip = None
        self.timer = None
        self.palettes = {}
        # said once, rather than on every frame
        self.warned = set()

    def start(self):
        for key, colors in self.config['palettes'].items():
            self.palettes[key] = [self.rgb(key, c) for c in colors]
        try:
            self.strip = strip.Strip(self.config['device'])
        except ImportError:
            logger.error('%s: spidev is not installed, so the strip stays'
                         ' dark.  sudo apt install python3-spidev',
                         self.name)
            return
        except OSError as e:
            logger.error('%s: %s: %s.  Is SPI turned on?  See the README',
                         self.name, self.config['device'], e)
            return
        QApplication.instance().aboutToQuit.connect(self.dark)
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(int(1000 / self.config['rate']))

    def rgb(self, palette, name):
        color = QColor(str(name))
        if not color.isValid():
            logger.error('%s: palette %s: %r is not a color', self.name,
                         palette, name)
            return effects.DARK
        return (color.redF(), color.greenF(), color.blueF())

    def lookName(self):
        """the look the page being looked at asks for"""
        for page, frame in self.piclock.pages.items():
            if frame.isVisible():
                return self.config['pages'].get(page, self.config['look'])
        return self.config['look']

    def tick(self):
        name = self.lookName()
        look = self.config['looks'].get(name)
        if look is None:
            self.warn(name, 'no look called %s' % name)
            look = {'effect': 'dark'}
        colors = self.palettes.get(look.get('palette'))
        if look['effect'] != 'dark' and colors is None:
            self.warn(name, 'look %s: no palette called %s'
                      % (name, look.get('palette')))
        frame = effects.frame(look['effect'], colors, look.get('period', 60),
                              self.config['leds'], time.time())
        self.strip.show(strip.encode(frame, self.config['order'],
                                     self.config['brightness']))

    def warn(self, key, message):
        if key not in self.warned:
            self.warned.add(key)
            logger.error('%s: %s', self.name, message)

    def dark(self):
        """off when the clock stops, rather than frozen on its last frame"""
        frame = [effects.DARK] * self.config['leds']
        self.strip.show(strip.encode(frame, self.config['order'], 0))
        self.strip.close()
