from urllib.parse import parse_qsl


class SensorBusy(Exception):
    pass


class SensorConnectionError(ConnectionError):
    pass


class Sensor(object):
    # defaulting to 1 minute access interval
    measurement_interval = 60
    type = None
    label = None

    def __init__(self, url):
        self.type = url.scheme
        params = dict(parse_qsl(url.query))
        self.measurement_interval = params.get('interval', self.measurement_interval)
        self.label = params.get('label')

    def get_metrics(self):
        raise NotImplementedError()

    def __str__(self):
        return '<%s at %s>' % (self.type, id(self))
