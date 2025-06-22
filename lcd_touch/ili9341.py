#!/usr/bin/python
#---------------------------------------------------------------------
# ili9341.py
# Control LCD with ili9341
#
# Author : Phien Nguyen (Mark)
# Date   : 15 June 2025
#---------------------------------------------------------------------
import time
from gpiozero import LED
import spidev
from . import font


# Resolution of LCD
ILI9341_WIDTH = 320
ILI9341_HEIGHT = 240

ILI9341_MADCTL_MY = 0x80
ILI9341_MADCTL_MX = 0x40
ILI9341_MADCTL_MV = 0x20
ILI9341_MADCTL_ML = 0x10
ILI9341_MADCTL_RGB = 0x00
ILI9341_MADCTL_BGR = 0x08
ILI9341_MADCTL_MH = 0x04
ILI9341_ROTATION = (ILI9341_MADCTL_MX | ILI9341_MADCTL_BGR)
ILI9341_LANDSCAPE_90 = (ILI9341_MADCTL_MV | ILI9341_MADCTL_BGR)

ILI9341_BLACK = 0x0000
ILI9341_BLUE = 0x001F
ILI9341_RED = 0xF800
ILI9341_GREEN = 0x07E0
ILI9341_CYAN = 0x07FF
ILI9341_MAGENTA = 0xF81F
ILI9341_YELLOW = 0xFFE0
ILI9341_WHITE = 0xFFFF

class ILI9341:
    def __init__(self, dc_pin, reset_pin, chip_id, resolution_x, resolution_y, display_rotation):
        self.dc_pin = LED(dc_pin)
        self.reset_pin = LED(reset_pin)

        self.spi_dev = spidev.SpiDev()
        self.spi_dev.open(0, chip_id)
        self.spi_dev.max_speed_hz = 500000

        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.display_rotation = display_rotation

    def delay_ms(self, ms):
        time.sleep(ms/1000)

    def color_RGB(r, g, b):
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | ((b & 0xF8) >> 3)
    
    def ctrl_dc(self, state):
        if state == True:
            self.dc_pin.on()
        else:
            self.dc_pin.off()

    def reset_lcd(self):
        self.reset_pin.off()
        self.delay_ms(5)
        self.reset_pin.on()

    def spi_dev_transmit(self, data_list):
        CHUNK_SIZE = 4096
        receive_data = []
        for i in range(0, len(data_list), CHUNK_SIZE):
            send_data = data_list[i : i + CHUNK_SIZE]
            try:
                temp_rev = self.spi_dev.xfer2(send_data)
                receive_data.extend(temp_rev)
            except Exception as e:
                print(f"SPI dev transmit error: {e}")
                return []
        return receive_data
    
    def write_command(self, cmd):
        self.ctrl_dc(False)
        self.spi_dev_transmit([cmd])

    def write_data(self, data_list):
        self.ctrl_dc(True)
        self.spi_dev_transmit(data_list)

    def set_address_window(self, x0, y0, x1, y1):
        # Column addr set
        self.write_command(0x2A)
        data_list = [(x0 >> 8) & 0xFF, x0 & 0xFF, (x1 >> 8) & 0xFF, x1 & 0xFF]
        self.write_data(data_list)

        # Row addr set
        self.write_command(0x2B)
        data_list = [(y0 >> 8) & 0xFF, y0 & 0xFF, (y1 >> 8) & 0xFF, y1 & 0xFF]
        self.write_data(data_list)

        # Write to RAM
        self.write_command(0x2C)

    def init(self):
        self.reset_lcd()
        self.write_command(0x01)
        time.sleep(1)

        self.write_command(0xCB)
        data_list = [0x39, 0x2C, 0x00, 0x34, 0x02]
        self.write_data(data_list)

        self.write_command(0xCF)
        data_list = [0x00, 0xC1, 0x30]
        self.write_data(data_list)

        self.write_command(0xE8)
        data_list = [0x85, 0x00, 0x78]
        self.write_data(data_list)

        self.write_command(0xEA)
        data_list = [0x00, 0x00]
        self.write_data(data_list)

        self.write_command(0xED)
        data_list = [0x64, 0x03, 0x12, 0x81]
        self.write_data(data_list)

        self.write_command(0xF7)
        data_list = [0x20]
        self.write_data(data_list)

        self.write_command(0xC0)
        data_list = [0x23]
        self.write_data(data_list)

        self.write_command(0xC1)
        data_list = [0x10]
        self.write_data(data_list)

        self.write_command(0xC5)
        data_list = [0x3E, 0x28]
        self.write_data(data_list)

        self.write_command(0xC7)
        data_list = [0x86]
        self.write_data(data_list)

        self.write_command(0x36)
        data_list = [0x48]
        self.write_data(data_list)

        self.write_command(0x3A)
        data_list = [0x55]
        self.write_data(data_list)

        self.write_command(0xB1)
        data_list = [0x00, 0x18]
        self.write_data(data_list)

        self.write_command(0xB6)
        data_list = [0x08, 0x82, 0x27]
        self.write_data(data_list)

        self.write_command(0xF2)
        data_list = [0x00]
        self.write_data(data_list)

        self.write_command(0x26)
        data_list = [0x01]
        self.write_data(data_list)

        self.write_command(0xE0)
        data_list = [0x0F, 0x31, 0x2B, 0x0C, 0x0E, 0x08, 0x4E, 0xF1,
                            0x37, 0x07, 0x10, 0x03, 0x0E, 0x09, 0x00]
        self.write_data(data_list)

        self.write_command(0xE1)
        data_list = [0x00, 0x0E, 0x14, 0x03, 0x11, 0x07, 0x31, 0xC1,
                            0x48, 0x08, 0x0F, 0x0C, 0x31, 0x36, 0x0F]
        self.write_data(data_list)

        self.write_command(0x11)
        self.delay_ms(120)

        self.write_command(0x29)
        self.write_command(0x36)
        if self.display_rotation == 0:
            lcd_rotation = ILI9341_LANDSCAPE_90
        else:
            lcd_rotation = ILI9341_ROTATION
        data_list = [lcd_rotation]
        self.write_data(data_list)
        
        print(f"ILI9341 init successfull")

    def draw_pixel(self, x, y, color):
        if (x >= self.resolution_x) or (y >= self.resolution_y):
            return
        self.set_address_window(x, y, x+1, y+1)
        data_list = [color >> 8, color & 0xFF]
        self.write_data(data_list)

    def fill_rectangle(self, x, y, w, h, color):
        if(x >= self.resolution_x) or (y >= self.resolution_y):
            return
        if(x + w - 1) >= self.resolution_x:
            w = self.resolution_x - x
        if(y + h - 1) >= self.resolution_y:
            h = self.resolution_y - y
        if w <= 0 or h <= 0:
            return
        
        self.set_address_window(x, y, x+w-1, y+h-1)
        color_bytes = [(color >> 8) & 0xFF, color & 0xFF]
        total_pixels = w * h
        all_pixel_data = []

        for _ in range(total_pixels):
            all_pixel_data.extend(color_bytes)
        self.write_data(all_pixel_data)

    def fill_screen(self, color):
        self.fill_rectangle(0, 0, self.resolution_x, self.resolution_y, color)

    def write_char(self, x, y, char_code, font, color, bgcolor):
        char_index_in_data = (ord(char_code) - 32) * font['height']
        color_on_bytes = [(color >> 8) & 0xFF, color & 0xFF]
        color_off_bytes = [(bgcolor >> 8) & 0xFF, bgcolor & 0xFF]
        self.set_address_window(x, y, x + font['width'] - 1, y + font['height'] - 1)

        all_char_pixel_data = []
        for i in range(font['height']):
            byte_data_row = font['data'][char_index_in_data + i]
            for j in range(font['width']):
                pixel_is_on = (byte_data_row >> (15 - j)) & 0x01
                if pixel_is_on:
                    all_char_pixel_data.extend(color_on_bytes)
                else:
                    all_char_pixel_data.extend(color_off_bytes)

        self.write_data(all_char_pixel_data)    

    def write_string(self, x, y, string_to_write, font, color, bgcolor):
        current_x = x
        current_y = y

        for char_val in string_to_write:
            if char_val == '\n' or (current_x + font['width'] > self.resolution_x):
                current_x = 0
                current_y += font['height']
                if current_y + font['height'] > self.resolution_y:
                    break
                if char_val == ' ':
                    continue

            self.write_char(current_x, current_y, char_val, font, color, bgcolor)
            current_x += font['width']

    def draw_image(self, x, y, w, h, image_data_16bit):
        if (x >= self.resolution_x) or (y >= self.resolution_y):
            return
        if (x + w - 1) >= self.resolution_x:
            return
        if (y + h - 1) >= self.resolution_y:
            return

        if w <= 0 or h <= 0:
            return

        if len(image_data_16bit) != (w * h):
            return

        self.set_address_window(x, y, x + w - 1, y + h - 1)

        all_image_pixel_bytes = []
        for pixel_color_16bit in image_data_16bit:
            all_image_pixel_bytes.append((pixel_color_16bit >> 8) & 0xFF)
            all_image_pixel_bytes.append(pixel_color_16bit & 0xFF)

        self.write_data(all_image_pixel_bytes)

    def invert_color(self, invert):
        self.write_command(0x21 if invert else 0x20)    


if __name__ == "__main__":
    print("Test ILI9341")
    DC_PIN_ID = 18
    RESET_PIN_ID = 23
    CHIP_ID = 0         # ILI9341 connect to CE0
    ili9341_obj = ILI9341(DC_PIN_ID, RESET_PIN_ID, CHIP_ID, 320, 240, 0)
    ili9341_obj.init()
    ili9341_obj.fill_screen(ILI9341_BLACK)
    ili9341_obj.write_string(0, 0, "Temperature: 15 Celsius degree", font.font_7x10, ILI9341_RED, ILI9341_BLACK)
    ili9341_obj.write_string(0, 3*10, "Temperature: 15 Celsius degree", font.font_11x18, ILI9341_GREEN, ILI9341_BLACK)
    ili9341_obj.write_string(0, 3*10+3*18, "Temperature: 15 Celsius degree", font.font_16x26, ILI9341_BLUE, ILI9341_BLACK)
    
    while True:
        time.sleep(2)

