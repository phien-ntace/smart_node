#!/usr/bin/python
#---------------------------------------------------------------------
# dht11.py
# Read value of dht11 sensor
#
# Author : Phien Nguyen (Mark)
# Date   : 15 June 2025
#---------------------------------------------------------------------
import time
import board
import adafruit_dht


class DHT11:
    def __init__(self, board_pin):
        self.dht11 = adafruit_dht.DHT11(board_pin)

    def get_temperature(self):
        return self.dht11.temperature
    
    def get_humidity(self):
        return self.dht11.humidity
    

if __name__ == "__main__":
    # Connect dht11 to GPIO4 (pin 7)
    dht11 = DHT11(board.D4)
    
    while True:
        try:
            temp = dht11.dht11.temperature
            humid = dht11.dht11.humidity
            if temp is not None and humid is not None:
                print(f"DHT11 - temperature: {temp:.1f} degree, humid: {humid:.1f}%")
            else:
                print("Could not get temperature and humidity")
        except RuntimeError as e:
            print(f"RuntimeError: {e}")
        except Exception as e:
            print(f"Exception: {e}")       
        
        time.sleep(1)
