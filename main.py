import sys

from lifeqmon import LifeQMon
from lifeqmon.reporters import Datadog
import logging


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    lm = LifeQMon(
        [
            'si7021://1',
            'mhz19:///dev/serial0',
            'noise://2'
        ],
        Datadog(constant_tags=['host:localhost'])
    )

    lm.loop()
