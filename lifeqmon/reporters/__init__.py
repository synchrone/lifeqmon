import datadog
from datadog import ThreadStats


class Reporter(object):
    gauge = ThreadStats.gauge


class Datadog(Reporter, ThreadStats):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        datadog.initialize()
        self.start()
