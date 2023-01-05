# Library for the micro:bit
# Thanks to adafruit_Python_SSD1306 library by Dmitrii (dmitryelj@gmail.com)
# Thanks to lopyi2c.py
# Thanks to fizban99

import microbit

class ssd1306:
   """ Screen class for SSD1306 I2C OLED 128x64 display """

   BLACK = 0
   WHITE = 1

   def __init__(self, scale = 1):

       self.scale    = scale
       self.width    = 128 // scale
       self.height   = 64 // scale
       self.zoom     = 0 if scale == 1 else 1
       self.i2c_addr = 0x3C

       # send byte plus packed pixels
       self.buffer_size = 1 + (128 * self.height // 8)
       self.screen      = bytearray(self.buffer_size) 
       self.screen[0]   = 0x40

       self.off()

       for cmd in [
            [0xA4],                     # SSD1306_DISPLAYALLON_RESUME
            [0xD5, 0xF0],               # SSD1306_SETDISPLAYCLOCKDIV
            [0xA8, 0x3F],               # SSD1306_SETMULTIPLEX
            [0xD3, 0x00],               # SSD1306_SETDISPLAYOFFSET
            [0 | 0x0],                  # line #SSD1306_SETSTARTLINE
            [0x8D, 0x14],               # SSD1306_CHARGEPUMP
            # 0x20 0x00 horizontal addressing
            [0x20, 0x00],               # SSD1306_MEMORYMODE
            [0x21, 0, 127],             # SSD1306_COLUMNADDR
            [0x22, 0, 63],              # SSD1306_PAGEADDR
            [0xa0 | 0x1],               # SSD1306_SEGREMAP
            [0xc8],                     # SSD1306_COMSCANDEC
            [0xDA, 0x12],               # SSD1306_SETCOMPINS
            [0x81, 0xCF],               # SSD1306_SETCONTRAST
            [0xd9, 0xF1],               # SSD1306_SETPRECHARGE
            [0xDB, 0x40],               # SSD1306_SETVCOMDETECT
            [0xD6, self.zoom],          # SSD1306_ZOOM
         ]:
           self.send(cmd)

       self.normal()
       self.on()
        
   def send(self, data):
       """ Send raw data to screen as bytes """
       microbit.i2c.write(self.i2c_addr, b'\x00' + bytearray(data))

   def on(self):
       """ Turn screen on """
       self.send([0xAF])

   def off(self):
       """ Turn screen off """
       self.send([0xAE])

   def normal(self):
       """ Set normal screen """
       self.send([0xA6])

   def invert(self):
       """ Set inverted screen """
       self.send([0xA7])

   def set_pos(self, x = 0, y = 0):
       """ Set starting pixel for image data """
       x = x * self.scale
       self.send([0xb0 | y >> 3])  # page number
       self.send([0x00 | x & 0xF]) # lower start column address
       self.send([0x10 | x >> 4])  # upper start column address

   def refresh(self):
       """ Refresh display """
       self.set_pos(0, 0)
       microbit.i2c.write(self.i2c_addr, self.screen)

   def clear(self, colour = BLACK):
       packed_pixels = 0x00 if colour == self.BLACK else 0xFF
       for i in range(1, self.buffer_size):
           self.screen[i] = packed_pixels
    
   def point(self, colour, x, y, update = False):
       """ Set colour of a pixel """

       if x < 0 or x >= self.width or y < 0 or y >= self.height:
           return

       page  = y // 8
       bit   = y % 8
       index = x * self.scale + page * 128 + 1

       if colour == self.WHITE:
           pixels = self.screen[index] | (1 << bit)
       else:
           pixels = self.screen[index] & ~(1 << bit)

       for i in range(0, self.scale):
           self.screen[index + i] = pixels

       if update:
           self.set_pos(x, y)
           microbit.i2c.write(self.i2c_addr,
                              bytearray([0x40] + [pixels] * self.scale))

   def getPixel(self, x, y):
       """ Get colour of a pixel """

       if x < 0 or x >= self.width or y < 0 or y >= self.height:
           return self.BLACK

       page  = y // 8
       bit   = y % 8
       index = x * self.scale + page * 128 + 1
       return (self.screen[index] >> bit) & 1

   def span(self, x1, x2, y, colour, update = False):
       """ Draw a horizontal line of pixels """
       for x in range(x1, x2):
           self.point(colour, x, y, update)

   def blit(self, x, y, image, update = False):
       """ """
       start_x = x
       for ch in image:
           if ch == '1':
               self.point(self.WHITE, x, y, update)
               x += 1
           elif ch == ':':
               x = start_x
               y += 1
           else:
               self.point(self.BLACK, x, y, update)
               x += 1
