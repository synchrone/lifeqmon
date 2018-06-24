from time import time, sleep
from typing import List, Dict
from urllib.parse import urlparse
from lifeqmon.reporters import Reporter
from lifeqmon.sensors import Sensor, SensorBusy
from logging import getLogger
from pydoc import locate

logger = getLogger(__name__)


class LifeQMon(object):
    sensors = list()  # type: List[Sensor]
    reporter = None  # type: Reporter
    last_measurements = {}  # type: Dict[Sensor,int]

    def __init__(self, add_sensors: List[str]=list(), reporter: Reporter=None, metric_namespace='lifeqmon'):
        self.metric_namespace = metric_namespace

        for s in add_sensors:
            self.add_sensor(s)

        if reporter:
            self.reporter = reporter

    def add_sensor(self, url: str):
        url = urlparse(url)
        driver_name = '.'.join([__name__, 'sensors', url.scheme, url.scheme.title()])

        logger.debug('loading '+driver_name)
        cls = locate(driver_name)
        sensor = cls(url)
        self.sensors.append(sensor)

    def _get_measurements(self):
        for s in self.sensors:
            if time() - self.last_measurements.get(s, 0) > s.measurement_interval:
                self._report_metrics(s)
                self.last_measurements[s] = time()
            else:
                logger.debug('Not measuring %s (time:%d < last_measurement:%d + interval:%d)' % (str(s), time(), self.last_measurements[s], s.measurement_interval))

    def loop(self):
        min_interval = min(map(lambda s: s.measurement_interval, self.sensors))
        logger.debug('Looping every %d sec.' % min_interval)

        while True:
            self._get_measurements()
            sleep(min_interval)

    def _report_metrics(self, s: Sensor):
        logger.info('Measuring %s (%s)' % (s, s.label))
        try:
            metrics = s.get_metrics()
        except SensorBusy:
            logger.warning('SensorBusy: '+str(s))
            return

        if len(metrics) > 0:
            logger.debug('Publishing %d metrics' % len(metrics))

        for name, value in metrics.items():
            logger.debug('%s=%s', name, value)
            self.reporter.gauge('.'.join([self.metric_namespace, s.type, name]), value, tags=['label:'+str(s.label)])
