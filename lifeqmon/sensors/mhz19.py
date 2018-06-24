#!/usr/bin/python
import serial
import time
from lifeqmon.sensors import Sensor, SensorBusy, SensorConnectionError


def crc8(a):
    crc = 0x00
    count = 1
    b = bytearray(a)
    if len(b) < 9:
        return -1

    while count < 8:
        crc += b[count]
        count = count + 1
    # Truncate to 8 bit
    crc %= 256
    # Invert number with xor
    crc = ~crc & 0xFF
    crc += 1
    return crc


class Mhz19(Sensor):
    measurement_interval = 60

    def __init__(self, url):
        super().__init__(url)
        port = url.path or '/dev/serial0'
        self.port = serial.Serial(port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE, timeout=1.0)

    def get_metrics(self):
        self.port.write([0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
        time.sleep(0.1)
        s = self.port.read(9)
        z = bytearray(s)

        if len(s) < 9:
            raise SensorConnectionError('Too few bytes received from %s' % self.port.port)

        if not (s[0] == 0xff and s[1] == 0x86):
            raise SensorConnectionError('Unknown packet received, bytes=%d:%d:%d:%d:%d:%d:%d:%d' % (z[0], z[1], z[2], z[3], z[4], z[5], z[6], z[7]))

        crc = crc8(s)
        if crc != z[8]:
            if all(e == 0x67 for e in z):
                raise SensorBusy('MH-Z19 is warming up')
            raise SensorBusy('CRC error calculated=%d, bytes=%d:%d:%d:%d:%d:%d:%d:%d crc=%dn' % (
                crc, z[0], z[1], z[2], z[3], z[4], z[5], z[6], z[7], z[8]))

        co2value = s[2] * 256 + s[3]
        temperature = s[4] - 40
        return {'co2': co2value, 'temperature': temperature}
