#!/usr/bin/python
#---------------------------------------------------------------------
# smart_node.py
# Create a simple Node with Raspberry Pi 5
#
# Author : Phien Nguyen (Mark)
# Date   : 22 June 2025
#---------------------------------------------------------------------
import signal
import time
import sys
import threading
import board
import datetime

from lcd_touch import ili9341
from lcd_touch import xpt2046
from sensors import dht11
from sensors import bh1750
from mqtt import mqtt_client
from actuators import led


is_running = True
bh1750_sens = None

# dht11 connect to GPIO4 (pin 7)
dht11_sens = None
DHT11_PIN = board.D4

# LCD ILI9341 connection
LCD_DC_PIN_ID = 18
LCD_RESET_PIN_ID = 23
LCD_CHIP_ID = 0         # ILI9341 connect to CE0

# LCD ILI9341 display parameters
LCD_RESOLUTION_X = 320
LCD_RESOLUTION_Y = 240
LCD_DISPLAY_ANGLE = 0
ili9341_lcd = None

# LED connect to PWM0
LED_PWM_PIN = 0
LED_DEFAULT_BRIGHTNESS = 50
LED_CHIP_ID = 0
led_ctrl = None

light_level = None
temperature = None
humid = None

mqtt_client_obj = None

def lcd_update_temperature(value):
    ili9341_lcd.write_string(150, 120, "    ", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(150, 120, f"{value:.1f}", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)
    
def lcd_update_humid(value):
    ili9341_lcd.write_string(150, 150, "  ", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(150, 150, f"{value}", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)
    
def lcd_update_light_level(value):
    ili9341_lcd.write_string(150, 180, "      ", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(150, 180, f"{value:.1f}", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)

def lcd_update_led_status(status):
    ili9341_lcd.write_string(150, 210, "   ", ili9341.font.font_11x18, ili9341.ILI9341_RED, ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(150, 210, status, ili9341.font.font_11x18, ili9341.ILI9341_RED, ili9341.ILI9341_BLACK)

def lcd_update_time(time):
    ili9341_lcd.write_string(220, 0, "   ", ili9341.font.font_11x18, ili9341.ILI9341_WHITE, ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(220, 0, time, ili9341.font.font_11x18, ili9341.ILI9341_WHITE, ili9341.ILI9341_BLACK)

def task_update_sensors():
    global light_level, temperature, humid
    lcd_light_level = 0
    lcd_temperature = 0
    lcd_humid = 0
    lcd_led_status = ""
    while is_running:
        light_level = bh1750_sens.read_light()
        try:
            temperature = dht11_sens.get_temperature()
            humid = dht11_sens.get_humidity()
            if temperature == None:
                temperature = lcd_temperature
            if humid == None:
                humid = lcd_humid

        except RuntimeError as e:
            print(f"DHT11 - RuntimeError: {e}")

        except Exception as e:
            print(f"DHT11 - Exception: {e}")  

        if light_level > 100:
            led_ctrl.led_off()
        else:
            led_ctrl.led_on()
        print(f"Light level: {light_level:.1f} lx, Temperature: {temperature:.1f} degree C, Humid: {humid}%")

        if light_level != lcd_light_level:
            lcd_update_light_level(light_level)
            lcd_light_level = light_level
        if temperature != lcd_temperature:
            lcd_update_temperature(temperature)
            lcd_temperature = temperature
        if humid != lcd_humid:
            lcd_update_humid(humid)
            lcd_humid = humid
        if led_ctrl.led_status != lcd_led_status:
            lcd_update_led_status(led_ctrl.led_status)
            lcd_led_status = led_ctrl.led_status

        curr_time = datetime.datetime.now()
        lcd_update_time(f"{curr_time.hour:02}:{curr_time.minute:02}:{curr_time.second:02}")
        time.sleep(1)

def task_update_mqtt():
    while is_running:
        if temperature is not None and humid is not None and light_level is not None:
            curr_time = datetime.datetime.now()
            str_mqtt = f"{curr_time.hour:02}:{curr_time.minute:02}:{curr_time.second:02} - Light level: {light_level:.1f} lx, Temperature: {temperature:.1f} degree C, Humid: {humid}%"
            mqtt_client_obj.publish(mqtt_topic_weather, str_mqtt, 0)
            time.sleep(10)

def mqtt_message_callback(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

if __name__ == "__main__":
    bh1750_sens = bh1750.BH1750()
    dht11_sens = dht11.DHT11(DHT11_PIN)
    led_ctrl = led.Led(LED_PWM_PIN, LED_DEFAULT_BRIGHTNESS, LED_CHIP_ID)
    led_ctrl.led_off()

    ili9341_lcd = ili9341.ILI9341(LCD_DC_PIN_ID, LCD_RESET_PIN_ID, LCD_CHIP_ID, LCD_RESOLUTION_X, LCD_RESOLUTION_Y, LCD_DISPLAY_ANGLE)
    ili9341_lcd.init()
    ili9341_lcd.fill_screen(ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(0, 120, "Temperature: ", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(0, 150, "Humid: ", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(0, 180, "Light level: ", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(0, 210, "LED status: ", ili9341.font.font_11x18, ili9341.ILI9341_RED, ili9341.ILI9341_BLACK)

    ili9341_lcd.write_string(200, 120, "degree C", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(180, 150, "%", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)
    ili9341_lcd.write_string(225, 180, "Lux", ili9341.font.font_11x18, ili9341.ILI9341_MAGENTA, ili9341.ILI9341_BLACK)

    mqtt_user = "smartnode"
    mqtt_password = "smartnode"
    mqtt_cluster_URL = "xxxxx.s1.eu.hivemq.cloud"
    mqtt_topic_weather = "weather"
    mqtt_subscribe_HiveMQ = "hiveMQ"

    mqtt_client_obj = mqtt_client.MQTTClient(user=mqtt_user, password=mqtt_password, cluster_URL=mqtt_cluster_URL)
    mqtt_client_obj.set_message_callback(mqtt_message_callback)
    mqtt_client_obj.subscribe_channel(mqtt_subscribe_HiveMQ, 0)
    mqtt_client_obj.start_thread_subscribe()

    thread_sensor = threading.Thread(target=task_update_sensors)
    thread_mqtt = threading.Thread(target=task_update_mqtt)
    thread_sensor.start()
    thread_mqtt.start()

    while True:
        time.sleep(100)