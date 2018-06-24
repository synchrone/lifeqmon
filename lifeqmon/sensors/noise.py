import signal
import logging
import threading

from soundmeter import meter
from lifeqmon import Sensor, SensorBusy

# ok, meter module is mangling with signals, so:
# Register signal handlers
sigint_handler = signal.getsignal(signal.SIGINT)
sigalrm_handler = signal.getsignal(signal.SIGALRM)
from soundmeter.meter import Meter  # noqa
signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGALRM, sigalrm_handler)

logger = logging.getLogger(__name__)


class ProgrammableMeter(Meter):
    callback = None

    def __init__(self, *args, monitor=None, **kwargs):
        if callable(monitor):
            self.callback = monitor
        super().__init__(*args, **kwargs)

    def monitor(self, rms):
        self.callback(rms)

    def meter(self, rms):
        pass  # disable cli reporting


class Noise(Sensor):
    measurement_interval = 0.5
    rms = None

    def __init__(self, url):
        super().__init__(url)

        def monitor():
            meter.INPUT_DEVICE_INDEX = int(url.netloc)
            meter.CHANNELS = 1  # mic is usually mono
            meter.AUDIO_SEGMENT_LENGTH = self.measurement_interval
            meter.FRAMES_PER_BUFFER = 8096

            logger.debug('Starting soundmeter thread with %s' % {
                'input_device_index': meter.INPUT_DEVICE_INDEX,
                'channels': meter.CHANNELS,
                'segment_length': meter.AUDIO_SEGMENT_LENGTH
            })

            while True:
                try:
                    m = ProgrammableMeter(monitor=self.update_metrics)
                    m.start()
                except OSError as e:
                    if e.errno == -9981:
                        logging.exception('buffer overflow, continuing')
                    else:
                        logging.exception('error measuring noise')
                        break
        threading.Thread(target=monitor, daemon=True).start()

    def update_metrics(self, rms):
        self.rms = rms

    def get_metrics(self):
        if self.rms is None:
            raise SensorBusy('Initial measuring in progress')
        return {'rms': self.rms}
