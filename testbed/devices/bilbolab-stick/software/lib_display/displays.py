import atexit
import os
import threading
import time
from datetime import datetime
import spidev

from lib_display.LCD_1inch3 import LCD_1inch3
from lib_display.LCD_0inch96 import LCD_0inch96

from PIL import Image,ImageDraw,ImageFont

# BIG DISPLAY
DISPLAY_BIG_RST = 27
DISPLAY_BIG_DC = 22
DISPLAY_BIG_BL = 19
DISPLAY_BIG_bus = 1
DISPLAY_BIG_device = 0

# SMALL DISPLAY 1
SMALL_DISPLAY_1_RST =24
SMALL_DISPLAY_1_DC = 4
SMALL_DISPLAY_1_BL = 13
SMALL_DISPLAY_1_bus = 0
SMALL_DISPLAY_1_device = 0

# SMALL DISPLAY 2
SMALL_DISPLAY_2_RST =23
SMALL_DISPLAY_2_DC =5
SMALL_DISPLAY_2_BL = 12
SMALL_DISPLAY_2_bus = 0
SMALL_DISPLAY_2_device = 1

# ======================================================================================================================
class BigDisplay:
    disp: LCD_1inch3
    size = (240, 240)

    def __init__(self):
        self.disp = LCD_1inch3(spi=spidev.SpiDev(DISPLAY_BIG_bus, DISPLAY_BIG_device),
                               spi_freq=90000000,
                               rst=DISPLAY_BIG_RST,
                               dc=DISPLAY_BIG_DC,
                               bl=DISPLAY_BIG_BL)

        self.ssid = ("", "WHITE")
        self.password = ("", "WHITE")
        self.ip = ("", "WHITE")
        self.bridge = ("", "WHITE")
        self.internet_status = ("No Internet", "RED")
        self.time_string = ""

        self.image = Image.new("RGB", (self.size[0], self.size[1]), "BLACK")
        self.draw = ImageDraw.Draw(self.image)


        atexit.register(self.close)

    def init(self):
        self.disp.Init()
        self.disp.clear()
        self.disp.bl_DutyCycle(100)

    def setSSID(self, ssid, color="WHITE"):
        self.ssid = (ssid, color)
        self.updateImageBuffer()

    def setPassword(self, password, color="WHITE"):
        self.password = (password, color)
        self.updateImageBuffer()

    def setIP(self, ip, color="WHITE"):
        self.ip = (ip, color)
        self.updateImageBuffer()

    def setBridge(self, bridge, color="WHITE"):
        self.bridge = (bridge, color)
        self.updateImageBuffer()

    def setInternet(self, is_connected):
        if is_connected:
            self.internet_status = ("Internet", "LIGHTGREEN")
        else:
            self.internet_status = ("No Internet", "RED")
        self.updateImageBuffer()

    def updateTime(self):
        self.time_string = datetime.now().strftime("%H:%M:%S")
        self.updateImageBuffer()

    def updateImageBuffer(self):
        self.draw.rectangle((0, 0, self.size[0], self.size[1]), fill="BLACK")

        # Resolve logo path dynamically
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "images", "bilbo_logo_stick.png")

        # Load and display the logo
        logo = Image.open(logo_path).resize((240, 80))
        self.image.paste(logo, (0, 0))

        # Load fonts
        font_path = os.path.join(script_dir, "Fonts", "Roboto-Bold.ttf")
        font = ImageFont.truetype(font_path, 22)
        font2 = ImageFont.truetype(font_path, 22)

        # Display parameters
        y_offset = 90
        self.draw.text((10, y_offset), f"SSID:", font=font, fill="WHITE")
        self.draw.text((80, y_offset), f"{self.ssid[0]}", font=font, fill=self.ssid[1])
        y_offset += 30
        self.draw.text((10, y_offset), f"PWD:", font=font, fill="WHITE")
        self.draw.text((80, y_offset), f"{self.password[0]}", font=font, fill=self.password[1])
        y_offset += 30
        self.draw.text((10, y_offset), f"IP:", font=font, fill="WHITE")
        self.draw.text((80, y_offset), f"{self.ip[0]}", font=font, fill=self.ip[1])
        y_offset += 30
        self.draw.text((10, y_offset), f"BRDG:", font=font, fill="WHITE")
        self.draw.text((80, y_offset), f"{self.bridge[0]}", font=font, fill=self.bridge[1])

        # Draw separator lines
        self.draw.line((0, 86, 240, 86), fill="GRAY", width=2)
        self.draw.line((0, 210, 240, 210), fill="GRAY", width=2)

        # Display time and internet status
        self.draw.rectangle((0, 220, 240, 240), fill="BLACK")  # Clear the time area
        self.draw.text((10, 210), self.internet_status[0], font=font2, fill=self.internet_status[1])
        self.draw.text((150, 210), self.time_string, font=font2, fill="WHITE")

    def update(self):
        # Rotate and display image
        image_show = self.image.rotate(90, expand=True)
        self.disp.ShowImage(image_show)

    def start(self):
        self.updateImageBuffer()
        self.update()

    def close(self):
        self.disp.module_exit()


# ======================================================================================================================
class SmallDisplayRobots:
    size = (160, 80)  # Maintain original size
    disp: LCD_0inch96
    devices: dict
    display_refresh_interval = 5  # Time in seconds to switch colors or remove devices

    def __init__(self, id, title):
        self.devices = {}
        self.image = None
        self.device_colors = {}  # Tracks temporary colors of devices
        self.title = title
        if id == 1:
            self.disp = LCD_0inch96(spi=spidev.SpiDev(SMALL_DISPLAY_2_bus,
                                                      SMALL_DISPLAY_2_device),
                                     spi_freq=40000000,
                                     rst=SMALL_DISPLAY_2_RST,
                                     dc=SMALL_DISPLAY_2_DC,
                                     bl=SMALL_DISPLAY_2_BL)
        else:
            self.disp = LCD_0inch96(spi=spidev.SpiDev(SMALL_DISPLAY_1_bus,
                                                      SMALL_DISPLAY_1_device),
                                     spi_freq=40000000,
                                     rst=SMALL_DISPLAY_1_RST,
                                     dc=SMALL_DISPLAY_1_DC,
                                     bl=SMALL_DISPLAY_1_BL)

        self.device_mutex = threading.Lock()
        atexit.register(self.close)

    def init(self):
        self.disp.Init()
        self.disp.clear()
        self.disp.bl_DutyCycle(100)

    def addDevice(self, device):
        with self.device_mutex:
            self.devices[device['ip']] = device
            self.device_colors[device['ip']] = "LIGHTGREEN"  # Initial color
        self.updateImageBuffer()

        # Schedule color change to white after 5 seconds
        threading.Timer(self.display_refresh_interval, self._setDeviceColor, args=(device['ip'], "WHITE")).start()

    def removeDevice(self, device):

        if isinstance(device, dict):
            ip = device['ip']
        else:
            ip = device
        if ip in self.devices:
            self.device_colors[ip] = "RED"  # Mark for red
            self.updateImageBuffer()

            # Schedule removal after 5 seconds
            threading.Timer(self.display_refresh_interval, self._removeDeviceFromDisplay, args=(ip,)).start()

    def _setDeviceColor(self, ip, color):
        if ip in self.device_colors:
            self.device_colors[ip] = color
            self.updateImageBuffer()

    def _removeDeviceFromDisplay(self, ip):
        with self.device_mutex:
            if ip in self.devices:
                del self.devices[ip]
            if ip in self.device_colors:
                del self.device_colors[ip]
        self.updateImageBuffer()

    def updateImageBuffer(self):
        # Swap width and height for pre-rotated drawing
        self.image = Image.new("RGB", (self.size[1], self.size[0]), "BLACK")
        draw = ImageDraw.Draw(self.image)

        # Resolve font path dynamically
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "Fonts", "Roboto-Bold.ttf")

        font_small = ImageFont.truetype(font_path, 10)

        # Draw header
        draw.text((15, 5), self.title, font=ImageFont.truetype(font_path, 16), fill="WHITE")
        draw.line((0, 30, self.size[0], 30), fill="GRAY", width=2)

        # Function to find the max font size that fits the text within the width
        def get_dynamic_font_size(text, max_width, font_path, initial_size=16):
            size = initial_size
            font = ImageFont.truetype(font_path, size)
            while size > 1:
                bbox = font.getbbox(text)  # Get the bounding box of the text
                text_width = bbox[2] - bbox[0]
                if text_width <= max_width:
                    break
                size -= 1
                font = ImageFont.truetype(font_path, size)
            return font

        # Draw robots
        y_offset = 35
        with self.device_mutex:
            for ip, data in self.devices.items():
                if y_offset + 20 > self.size[0]:
                    break  # Avoid overflow

                color = self.device_colors.get(ip, "WHITE")

                # Dynamically adjust font size for hostname
                hostname_font = get_dynamic_font_size(data['hostname'], self.size[1] - 5, font_path)
                draw.text((5, y_offset), data['hostname'], font=hostname_font, fill=color)
                text_height = hostname_font.getbbox(data['hostname'])[3] - hostname_font.getbbox(data['hostname'])[1]
                y_offset += text_height + 5  # Move down by the height of the text

                # IP Address
                draw.text((5, y_offset), data['ip'], font=font_small, fill=color)
                ip_text_height = font_small.getbbox(data['ip'])[3] - font_small.getbbox(data['ip'])[1]
                y_offset += ip_text_height + 5

                # Separator line
                draw.line((0, y_offset, self.size[0], y_offset), fill="GRAY", width=1)
                y_offset += 5

    def update(self):
        # No rotation needed now, as we directly painted in the rotated orientation
        image_show = self.image.rotate(90, expand=True)
        self.disp.ShowImage(image_show)

    def start(self):
        self.updateImageBuffer()
        self.update()

    def close(self):
        self.disp.module_exit()



if __name__ == '__main__':
    # disp = BigDisplay()
    disp2 = SmallDisplay(1)
    disp3 = SmallDisplay(2)
    # disp.init()
    # disp.start()
    disp2.init()
    disp3.init()
    disp2.start()
    disp3.start()

    while True:
        time.sleep(1)