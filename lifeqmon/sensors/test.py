from time import time

from lifeqmon import Sensor


class Test(Sensor):
    measurement_interval = 1

    def get_metrics(self):
        return {'current_time': time()}
