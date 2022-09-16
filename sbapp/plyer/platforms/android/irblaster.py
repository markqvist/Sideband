from jnius import autoclass

from plyer.facades import IrBlaster
from plyer.platforms.android import activity, SDK_INT, ANDROID_VERSION

if SDK_INT >= 19:
    Context = autoclass('android.content.Context')
    ir_manager = activity.getSystemService(Context.CONSUMER_IR_SERVICE)
else:
    ir_manager = None


class AndroidIrBlaster(IrBlaster):
    def _exists(self):
        if ir_manager and ir_manager.hasIrEmitter():
            return True
        return False

    @property
    def multiply_pulse(self):
        '''Android 4.4.3+ uses microseconds instead of period counts
        '''
        return not (SDK_INT == 19
                    and int(str(ANDROID_VERSION.RELEASE).rsplit('.', 1)[-1])
                    < 3)

    def _get_frequencies(self):
        if not ir_manager:
            return None

        if hasattr(self, '_frequencies'):
            return self._frequencies

        ir_frequencies = ir_manager.getCarrierFrequencies()
        if not ir_frequencies:
            return []

        frequencies = []
        for freqrange in ir_frequencies:
            freq = (freqrange.getMinFrequency(), freqrange.getMaxFrequency())
            frequencies.append(freq)

        self._frequencies = frequencies
        return frequencies

    def _transmit(self, frequency, pattern, mode):
        if self.multiply_pulse and mode == 'period':
            pattern = self.periods_to_microseconds(frequency, pattern)
        elif not self.multiply_pulse and mode == 'microseconds':
            pattern = self.microseconds_to_periods(frequency, pattern)
        ir_manager.transmit(frequency, pattern)


def instance():
    return AndroidIrBlaster()
