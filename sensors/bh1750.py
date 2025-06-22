#!/usr/bin/python
#---------------------------------------------------------------------
# bh1750.py
# Read value of bh1750 sensor
#
# Author : Phien Nguyen (Mark)
# Date   : 15 June 2025
#---------------------------------------------------------------------
import smbus
import time


BH1750_ADDR = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value

# Start measurement at 4lx resolution. Time typically 16ms.
CONTINUOUS_LOW_RES_MODE = 0x13
# Start measurement at 1lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_1 = 0x10
# Start measurement at 0.5lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_2 = 0x11
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_1 = 0x20
# Start measurement at 0.5lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_2 = 0x21
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_LOW_RES_MODE = 0x23

class BH1750:
    def __init__(self):
        # self.bus = smbus.SMBus(0)  # Pi rev 1 use i2c-0
        self.bus = smbus.SMBus(1)  # Pi rev 2 use i2c-1

    def convert_to_number(self, data):
        # Simple function to convert 2 bytes of data
        # into a decimal number. Optional parameter 'decimals'
        # will round to specified number of decimal places.
        result=(data[1] + (256 * data[0])) / 1.2
        return (result)

    def read_light(self):
        # Read data from I2C interface
        data = self.bus.read_i2c_block_data(BH1750_ADDR, ONE_TIME_HIGH_RES_MODE_1)
        return self.convert_to_number(data)


if __name__=="__main__":
    bh1750 = BH1750()
    while True:
        light_level = bh1750.read_light()
        print(f"BH1750 - light level: {light_level:.1f} lx")
        time.sleep(1)