#!/usr/bin/python
#---------------------------------------------------------------------
# xpt2046.py
# Get touchscreen (Not tested yet)
#
# Author : Phien Nguyen (Mark)
# Date   : 21 June 2025
#---------------------------------------------------------------------
from gpiozero import LED
from gpiozero import DigitalInputDevice
import spidev
import time

# Swap READ_X, READ_Y depend on orientation of touchscreen
READ_X = 0x90
READ_Y = 0xD0

ILI9341_TOUCH_SCALE_X = 320
ILI9341_TOUCH_SCALE_Y = 240

ILI9341_TOUCH_MIN_RAW_X = 1500
ILI9341_TOUCH_MAX_RAW_X = 3874
ILI9341_TOUCH_MIN_RAW_Y = 3276
ILI9341_TOUCH_MAX_RAW_Y = 3720

class XPT2046:
    def __init__(self, resolution_x, resolution_y, irq_pin, chip_id):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.irq_pin = irq_pin
        self.chip_id = chip_id
        
        self.irq_pin_status = DigitalInputDevice(self.irq_pin, pull_up=True)
        self.spi_dev = spidev.SpiDev()
        self.spi_dev.open(0, self.chip_id)
        self.spi_dev.max_speed_hz = 500000

    def is_touched(self):
        return self.irq_pin_status.is_active
    
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
    
    def get_touch_coordinate(self):
        avg_x = 0
        avg_y = 0
        n_samples = 0

        for i in range(16):
            if not self.is_touched():
                break
            n_samples += 1
            response_y = self.spi_dev_transmit([READ_Y, 0x00, 0x00])
            time.sleep(0.001)
            response_x = self.spi_dev_transmit([READ_X, 0x00, 0x00])
            if len(response_y) < 3 or len(response_x) < 3:
                continue
            y_raw_val = ((response_y[1] << 8) | response_y[2]) >> 3
            x_raw_val = ((response_x[1] << 8) | response_x[2]) >> 3
            avg_x += x_raw_val
            avg_y += y_raw_val
            time.sleep(0.001)

        if n_samples == 0:
            return False, 0, 0

        raw_x = int(avg_x / n_samples)
        raw_y = int(avg_y / n_samples)

        if raw_x < ILI9341_TOUCH_MIN_RAW_X: raw_x = ILI9341_TOUCH_MIN_RAW_X
        if raw_x > ILI9341_TOUCH_MAX_RAW_X: raw_x = ILI9341_TOUCH_MAX_RAW_X
        if raw_y < ILI9341_TOUCH_MIN_RAW_Y: raw_y = ILI9341_TOUCH_MIN_RAW_Y
        if raw_y > ILI9341_TOUCH_MAX_RAW_Y: raw_y = ILI9341_TOUCH_MAX_RAW_Y

        x_calibrated = int((raw_x - ILI9341_TOUCH_MIN_RAW_X) * self.resolution_x /
                        (ILI9341_TOUCH_MAX_RAW_X - ILI9341_TOUCH_MIN_RAW_X))
        y_calibrated = int((raw_y - ILI9341_TOUCH_MIN_RAW_Y) * self.resolution_y /
                        (ILI9341_TOUCH_MAX_RAW_Y - ILI9341_TOUCH_MIN_RAW_Y))

        return True, x_calibrated, y_calibrated

if __name__ == "__main__":
    print(f"Read touch screen")
    IRQ_PIN = 22
    CHIP_ID = 1     #CE1
    xpt2046_obj = XPT2046(320, 240, IRQ_PIN, CHIP_ID)
    try:
        while True:
            if xpt2046_obj.is_touched:
                success, x, y = xpt2046_obj.get_touch_coordinate()
                if success:
                    print(f"X={x}, Y={y}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass