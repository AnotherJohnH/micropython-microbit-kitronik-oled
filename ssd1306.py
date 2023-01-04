# I2C LCD library for the micro:bit
# Thanks to adafruit_Python_SSD1306 library by Dmitrii (dmitryelj@gmail.com)
# Thanks to lopyi2c.py
# Author: fizban99
# v0.1 beta
# Only supports display type I2C128x64

import microbit
import ustruct

# LCD Control constants
I2C_ADDR = 0x3C
screen = bytearray(513)  # send byte plus pixels
screen[0] = 0x40
zoom = 1

def command(data):
    microbit.i2c.write(I2C_ADDR, b'\x00' + bytearray(data))

def initialize():
    for cmd in [
        [0xAE],                     # SSD1306_DISPLAYOFF
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
        [0xA6],                     # SSD1306_NORMALDISPLAY
        [0xd6, 1],                  # zoom on
        [0xaf]                      # SSD1306_DISPLAYON
    ]:
        command(cmd)

def set_pos(col = 0, page = 0):
    # take upper and lower value of col * 2
    c1, c2 = col * 2 & 0x0F, col >> 3
    command([0xb0 | page])  # page number
    command([0x00 | c1])  # lower start column address
    command([0x10 | c2])  # upper start column address

def set_zoom(v):
    global zoom
    if zoom != v:
        command([0xd6, v])  # zoom on/off
        command([0xa7 - v])  # inverted display
        zoom = v

def refresh():
    set_zoom(1)
    set_pos()
    microbit.i2c.write(I2C_ADDR, screen)

def clear():
    global screen
    for i in range(1, 513):
        screen[i] = 0
    refresh()

def set_px(x, y, color, draw=1):
    page, shift_page = divmod(y, 8)
    ind = x * 2 + page * 128 + 1
    b = screen[ind] | (1 << shift_page) if color else screen[ind] & ~ (1 << shift_page)
    ustruct.pack_into(">BB", screen, ind, b, b)
    if draw:
        set_pos(x, page)
        microbit.i2c.write(I2C_ADDR, bytearray([0x40, b, b]))

def get_px(x, y):
    page, shift_page = divmod(y, 8)
    ind = x * 2 + page * 128 + 1
    b = (screen[ind] & (1 << shift_page)) >> shift_page
    return b
