import time
from smbus import SMBus

from lifeqmon.sensors import Sensor


class Si7021(Sensor):
    def __init__(self, url):
        super().__init__(url)
        smbus_num = int(url.netloc)
        self.bus = SMBus(smbus_num)

    def get_metrics(self):
        # SI7021 address, 0x40(64)
        # 0xF5(245)	Select Relative Humidity NO HOLD master mode
        self.bus.write_byte(0x40, 0xF5)

        time.sleep(0.3)

        # SI7021 address, 0x40(64)
        # Read data back, 2 bytes, Humidity MSB first
        data0 = self.bus.read_byte(0x40)
        data1 = self.bus.read_byte(0x40)

        # Convert the data
        humidity = ((data0 * 256 + data1) * 125 / 65536.0) - 6

        time.sleep(0.3)

        # SI7021 address, 0x40(64)
        # 0xF3(243)	Select temperature NO HOLD master mode
        self.bus.write_byte(0x40, 0xF3)

        time.sleep(0.3)

        # SI7021 address, 0x40(64)
        # Read data back, 2 bytes, Temperature MSB first
        data0 = self.bus.read_byte(0x40)
        data1 = self.bus.read_byte(0x40)

        # Convert the data
        temp = ((data0 * 256 + data1) * 175.72 / 65536.0) - 46.85
        return {'humidity': humidity, 'temperature': temp}
