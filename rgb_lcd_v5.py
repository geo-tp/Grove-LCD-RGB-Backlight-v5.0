import time
from machine import I2C, Pin, ADC


class Screen(object):
    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(self, i2c, address, oneline=False, charsize=LCD_5x8DOTS):

        self.i2c = i2c
        self.address = address

        self.disp_func = self.LCD_DISPLAYON # | 0x10
        if not oneline:
            self.disp_func |= self.LCD_2LINE
        elif charsize != 0:
            # for 1-line displays you can choose another dotsize
            self.disp_func |= self.LCD_5x10DOTS

        # wait for display init after power-on
        time.sleep_ms(50) # 50ms

        # send function set
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)
        time.sleep_us(4500) ##time.sleep(0.0045) # 4.5ms
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)
        time.sleep_us(150) ##time.sleep(0.000150) # 150µs = 0.15ms
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)
        self.cmd(self.LCD_FUNCTIONSET | self.disp_func)

        # turn on the display
        self.disp_ctrl = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.display(True)

        # clear it
        self.clear()

        # set default text direction (left-to-right)
        self.disp_mode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.cmd(self.LCD_ENTRYMODESET | self.disp_mode)


    def cmd(self, command):
        assert command >= 0 and command < 256
        command = bytearray([command])
        self.i2c.writeto_mem(self.address, 0x80, bytearray([]))
        self.i2c.writeto_mem(self.address, 0x80, command)


    def write_char(self, c):
        assert c >= 0 and c < 256
        c = bytearray([c])
        self.i2c.writeto_mem(self.address, 0x40, c)

    def write(self, text):
        for char in text:
            self.write_char(ord(char))

    def cursor(self, state):
        if state:
            self.disp_ctrl |= self.LCD_CURSORON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_CURSORON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def setCursor(self, col, row):
        col = (col | 0x80) if row == 0 else (col | 0xc0)
        self.cmd(col)

    def autoscroll(self, state):
        if state:
            self.disp_mode |= self.LCD_ENTRYSHIFTINCREMENT
            print(self.disp_mode)
            self.cmd(self.LCD_ENTRYMODESET  | 3)
        else:
            self.disp_mode &= ~self.LCD_ENTRYSHIFTINCREMENT
            self.cmd(self.LCD_ENTRYMODESET   | self.disp_mode)

    def blink(self, state):
        if state:
            self.disp_ctrl |= self.LCD_BLINKON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_BLINKON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def display(self, state):
        if state:
            self.disp_ctrl |= self.LCD_DISPLAYON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)
        else:
            self.disp_ctrl &= ~self.LCD_DISPLAYON
            self.cmd(self.LCD_DISPLAYCONTROL  | self.disp_ctrl)

    def clear(self):
        self.cmd(self.LCD_CLEARDISPLAY)
        time.sleep_ms(2) # 2ms

    def home(self):
        self.cmd(self.LCD_RETURNHOME)
        time.sleep_ms(2) # 2m


class Backlight(object):
    REG_RED = 0x06
    REG_GREEN = 0x07
    REG_BLUE = 0x08

    def __init__(self, i2c, address):
        if not isinstance(i2c, I2C):
            raise TypeError

        self.i2c = i2c
        self.address = int(address)

        # Backlight on
        self.set_register(0x04, 0x15)


    def blinkLed(self):
        self.set_register(0x04, 0x2a) # blink every seconds
        self.set_register(0x01, 0x06) # 50% duty cycle
        self.set_register(0x02, 0x7f) # 50% duty cycle


    def set_register(self, addr, value):
        value = bytearray([value])
        self.i2c.writeto_mem(self.address, addr, bytearray([]))
        self.i2c.writeto_mem(self.address, addr, value)

    def set_color(self, red, green, blue):
        r = int(red)
        g = int(green)
        b = int(blue)
        self.set_register(self.REG_RED, r)
        self.set_register(self.REG_GREEN, g)
        self.set_register(self.REG_BLUE, b)


class Display(object):
    backlight = None
    screen = None


    def __init__(self, lcd_addr=0x3e, rgb_addr=0x30):
        print(int(lcd_addr), int(rgb_addr))
        self.i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)

        self.backlight = Backlight(self.i2c, rgb_addr)
        self.screen =  Screen(self.i2c, lcd_addr)

    def write(self, text):
        self.screen.write(text)

    def cursor(self, state):
        self.screen.cursor(state)

    def blink(self, state):
        self.screen.blink(state)

    def blinkLed(self):
        self.backlight.blinkLed()

    def autoscroll(self, state):
        self.screen.autoscroll(state)

    def display(self, state):
        self.screen.display(state)

    def clear(self):
        self.screen.clear()

    def home(self):
        self.screen.home()

    def color(self, r, g, b):
        self.backlight.set_color(r, g, b)

    def setCursor(self, col, row):
        self.screen.setCursor(col, row)

def test_i2c_pins():
    valid_configurations = []
    for scl_pin in range(32):  # Test SCL pins up to 32
        for sda_pin in range(32):  # Test SDA pins up to 32
            if scl_pin == sda_pin:
                continue  # Skip testing with the same pins for SCL and SDA
            try:
                # Attempt to create an I2C bus with the current pin configuration
                i2c = I2C(1, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)
                devices = i2c.scan()
                if devices:
                    print(f"SCL Pin: {scl_pin}, SDA Pin: {sda_pin}, Devices Found: {devices}")
                    valid_configurations.append((scl_pin, sda_pin, devices))
                else:
                    print(f"SCL Pin: {scl_pin}, SDA Pin: {sda_pin}, No devices found")
            except Exception as e:
                print(f"Failed to initialize I2C with SCL Pin: {scl_pin}, SDA Pin: {sda_pin} - Error: {e}")
            finally:
                time.sleep(0.1)  # Small delay to prevent too fast initialization

    return valid_configurations

