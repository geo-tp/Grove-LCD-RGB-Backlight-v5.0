# Grove-LCD RGB Backlight v5.0 Library for MicroPython

This library is designed to control the **Grove-LCD RGB Backlight V5.0** display using MicroPython.

## Installation

- With [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html)

```
mpremote cp /path/to/rgb_lcd_v5.py :/lib/
```

## Use
```
from rgb_lcd_v5 import Display

display = Display(sda=0, scl=1, i2c_bus=1, freq=400000)
```

## Exemple

- ### Hello World
```
from rgb_lcd_v5 import Display

# Change sda and scl pin if needed
display = Display(sda=0, scl=1)
display.clear()

display.write("Hello World")
```

- ### Backlight Color
```
import time
from rgb_lcd_v5 import Display

display = Display(sda=0, scl=1, i2c_bus=1)
display.clear()
display.write("Red Color")
display.color(255, 0, 0)

```

- ### Backlight Color Blink
```
import time
from rgb_lcd_v5 import Display

display = Display(sda=0, scl=1, i2c_bus=1)

while 1:
    display.color(0, 0, 255) # Blue
    time.sleep(1)
    display.color(0, 255, 0) # Green
    time.sleep(1)
```


- ### Cursor Blink
```
import time
from rgb_lcd_v5 import Display

display = Display(sda=0, scl=1, i2c_bus=1)
display.clear()


while 1:
    display.blink(True)
    time.sleep(1)
    display.blink(False)
```

- ### Autoscroll
```
import time
from rgb_lcd_v5 import Display

display = Display(sda=0, scl=1)
display.clear()

while 1:
    display.setCursor(0, 0)

    # Write at begining of the first line
    for i in range(10):
        display.write(i)
        time.sleep_ms(300)

    display.setCursor(16, 1)
    display.autoscroll(True)

    # Write at the end of the second line
    for i in range(10):
        display.write(i)
        time.sleep_ms(300)

    display.autoscroll(False)
    display.clear()

```

## Scan I2C Pins

- If you don't know what your I2C pins are
```
from rgb_lcd_v5 import scan_i2c_pins

scan_i2c_pins(i2c_bus=1)
```
