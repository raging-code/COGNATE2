from machine import Pin, I2C
import time

# SSD1306 I2C addresses
SSD1306_I2C_ADDRESS = 0x3C  # or 0x3D

class SSD1306:
    def __init__(self, width, height, i2c, addr=SSD1306_I2C_ADDRESS):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.buffer = bytearray((height // 8) * width)
        self.init_display()
    
    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytes([0x00, cmd]))
    
    def write_data(self, data):
        self.i2c.writeto(self.addr, b'\x40' + data)
    
    def init_display(self):
        # Initialization sequence
        cmds = [
            0xAE,  # Display off
            0xD5, 0x80,  # Set display clock divide
            0xA8, 0x3F,  # Set multiplex
            0xD3, 0x00,  # Set display offset
            0x40,  # Set start line
            0x8D, 0x14,  # Charge pump
            0x20, 0x00,  # Memory mode
            0xA1,  # Segment remap
            0xC8,  # COM scan direction
            0xDA, 0x12,  # COM pins
            0x81, 0xCF,  # Contrast
            0xD9, 0xF1,  # Pre-charge
            0xDB, 0x40,  # VCOM detect
            0xA4,  # Display all on resume
            0xA6,  # Normal display
            0x2E,  # Deactivate scroll
            0xAF   # Display on
        ]
        for cmd in cmds:
            self.write_cmd(cmd)
    
    def pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            page = y // 8
            bit = y % 8
            index = page * self.width + x
            if color:
                self.buffer[index] |= (1 << bit)
            else:
                self.buffer[index] &= ~(1 << bit)
    
    def show(self):
        for i in range(0, len(self.buffer), 16):
            self.write_data(self.buffer[i:i+16])
    
    def fill(self, color):
        self.buffer = bytearray([0xFF if color else 0x00] * len(self.buffer))
    
    def text(self, string, x, y, color=1):
        # Simple 8x8 font implementation
        font = [
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # Space
            0x00, 0x00, 0x5F, 0x00, 0x00, 0x00, 0x00, 0x00,  # !
            # Add more characters as needed
        ]
        for char in string:
            for i in range(8):
                line = font[ord(char) * 8 + i] if ord(char) < len(font)//8 else 0
                for j in range(8):
                    if line & (1 << j):
                        self.pixel(x + j, y + i, color)
            x += 8

# Usage example
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = SSD1306(128, 64, i2c)

# Clear display
oled.fill(0)

# Draw something
oled.text("Hello", 0, 0, 1)
oled.text("World", 0, 8, 1)

# Update display
oled.show()
