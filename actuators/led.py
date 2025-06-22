#!/usr/bin/python
#---------------------------------------------------------------------
# led.py
# Control LED with PWM
#
# Author : Phien Nguyen (Mark)
# Date   : 15 June 2025
#---------------------------------------------------------------------

from rpi_hardware_pwm import HardwarePWM
import time

class Led:
    def __init__(self, led_pin: int, default_brightness: int, chip: int):
        self.led_pin = led_pin
        self.default_brightness = default_brightness
        self.chip = chip
        self.pwm = HardwarePWM(pwm_channel=self.led_pin, hz=10000, chip=self.chip)
        self.pwm.start(0)

    def get_parameters(self):
        print(f"led_pin: {self.led_pin}")
        print(f"default_brightness: {self.default_brightness}")
        print(f"chip: {self.chip}")

    def led_off(self):
        self.pwm.change_duty_cycle(0)
        self.led_status = "Off"

    def led_on(self):
        self.pwm.change_duty_cycle(self.default_brightness)
        self.led_status = "On"

    def led_change_brightness(self, brightness):
        self.pwm.change_duty_cycle(brightness)

if __name__ == "__main__":
    # LED connect to PWM0
    TEST_LED_PIN = 0
    test_led = Led(TEST_LED_PIN, 50, 0)
    while True:
        test_led.led_off()
        time.sleep(1)
        test_led.led_on()
        time.sleep(1)

        
        


        
