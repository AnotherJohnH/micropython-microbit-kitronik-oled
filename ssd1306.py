# Library for the micro:bit
# Thanks to adafruit_Python_SSD1306 (dmitryelj@gmail.com)
# lopyi2c.py and fizban99

import microbit

class ssd1306:

   def __init__(self, zoom = 1):
       self.scale       = 2 if zoom else 1
       self.width       = 128 // self.scale
       self.height      = 64 // self.scale
       self.i2c_addr    = 0x3C
       self.buffer_size = 1 + (128 * self.height // 8)
       self.screen      = bytearray(self.buffer_size)
       self.screen[0]   = 0x40

       for cmd in [
             [0xAE],         # DISPLAY - 0b0 => on
             [0xA4],         # DISPLAYALLON_RESUME
             [0xD5, 0xF0],   # DISPLAYCLOCKDIV
             [0xA8, 0x3F],   # MULTIPLEX_RATIO
             [0xD3, 0x00],   # DISPLAYOFFSET
             [0x00],         # STARTLINE  - 0000b
             [0x8D, 0x14],   # CHARGEPUMP
             [0x20, 0b00],   # MEMORYMODE - 00b horizontal addressing
             [0x21, 0, 127], # COLUMNADDR - start, end
             [0x22, 0, 63],  # PAGEADDR   - start, end
             [0xA1],         # SEGREMAP   - 1b
             [0xC8],         # COMSCANDEC - 1000b
             [0xDA, 0x12],   # COMPINS
             [0x81, 0xCF],   # CONTRAST
             [0xD9, 0xF1],   # PRECHARGE
             [0xDB, 0x40],   # VCOMDETECT
             [0xD6, zoom],   # ZOOM
             [0xA6],         # INVERSE - 0b0 => normal
             [0xAF] ]:       # DISPLAY - 0b1 => on
           self.cmnd(cmd)

   def cmnd(self, data):
       microbit.i2c.write(self.i2c_addr, b'\x00' + bytearray(data))

   def data(self, x, y, data):
       self.cmnd([0xB0 | y >> 3])  # page number
       self.cmnd([0x00 | x & 0xF]) # lower start column address
       self.cmnd([0x10 | x >> 4])  # upper start column address
       microbit.i2c.write(self.i2c_addr, data)

   def refresh(self):
       self.data(0, 0, self.screen)

   def getPixel(self, x, y):
       if x < 0 or x >= self.width or y < 0 or y >= self.height:
           return 0

       page  = y // 8
       bit   = y % 8
       index = x * self.scale + page * 128 + 1
       return (self.screen[index] >> bit) & 1

   def clear(self, colour = 0):
       packed_pixels = 0x00 if colour == 0 else 0xFF
       for i in range(1, self.buffer_size):
           self.screen[i] = packed_pixels

   def point(self, x, y, colour = 1, update = False):
       if x < 0 or x >= self.width or y < 0 or y >= self.height:
           return

       page  = y // 8
       mask  = 1 << (y % 8)
       index = x * self.scale + page * 128 + 1

       if colour == 1:
           pixels = self.screen[index] | mask
       else:
           pixels = self.screen[index] & ~mask

       self.screen[index] = pixels
       if self.scale == 2:
           self.screen[index + 1] = pixels

       if update:
           self.data(x * self.scale, y, bytearray([0x40] + [pixels] * self.scale))

   def line(self, x1, y1, x2, y2, colour = 1):
       dx = x2 - x1
       dy = y2 - y1
       if abs(dx) > abs(dy):
           ix = -1 if dx < 0 else 1
           iy = (dy << 16) // abs(dx)
           y  = y1 << 16
           for x in range(x1, x2, ix):
               self.point(x, y >> 16, colour)
               y += iy
       elif dy != 0:
           iy = -1 if dy < 0 else 1
           ix = (dx << 16) // abs(dy)
           x  = x1 << 16
           for y in range(y1, y2, iy):
               self.point(x >> 16, y, colour)
               x += ix

   def span(self, x1, x2, y, colour = 1):
       for x in range(x1, x2):
           self.point(x, y, colour)

   def block(self, x, y, w, h, colour = 1):
       for y in range(y, y + h):
           self.span(x, x + w, y, colour)

   def blit(self, x, y, image):
       start_x = x
       for ch in image:
           if ch == ':':
               x = start_x
               y += 1
           else:
               self.point(x, y, ch == '1')
               x += 1
