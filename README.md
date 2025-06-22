# Smart Node

This project uses a **Raspberry Pi 5** to:

- Read sensor data from **DHT11** (temperature & humidity) and **BH1750** (light intensity).
- Display the sensor values on an **ILI9341** LCD screen.
- Publish the sensor data to an **MQTT server**.
- Control an **LED** using **PWM**.

---

## Wiring Details

### 🔹 BH1750 Light Sensor

| BH1750 Pin | Raspberry Pi 5 Pin           |
|------------|------------------------------|
| VCC        | Pin 1 (3.3V)                 |
| SCL        | Pin 5 (GPIO 3 / SCL1)        |
| SDA        | Pin 3 (GPIO 2 / SDA1)        |

### 🔹 DHT11 Temperature & Humidity Sensor

| DHT11 Pin | Raspberry Pi 5 Pin           |
|-----------|------------------------------|
| Data      | Pin 7 (GPIO 4)               |

### 🔹 LED (PWM Controlled)

| LED Pin | Raspberry Pi 5 Pin             |
|---------|-------------------------------|
| Anode   | Pin 32 (GPIO 12 / PWM0)        |

### 🔹 ILI9341 LCD (SPI Interface)

| LCD Pin   | Raspberry Pi 5 Pin                  |
|-----------|-------------------------------------|
| LED       | 3.3V                                |
| SCK       | Pin 23 (GPIO 11)                    |
| SDI/MOSI  | Pin 19 (GPIO 10)                    |
| D/C       | Pin 12 (GPIO 18)                    |
| RESET     | Pin 16 (GPIO 23)                    |
| CS        | Pin 24 (GPIO 8 / SPI0_CE0)          |
| GND       | GND                                 |
| VCC       | 5V                                  |

---

## Features

- Real-time sensor readings displayed on LCD.
- MQTT communication for remote monitoring.
- PWM control for LED brightness based on ambient light.
