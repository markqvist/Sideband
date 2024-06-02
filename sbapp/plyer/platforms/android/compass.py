'''
Android Compass
---------------------
'''

from plyer.facades import Compass
from jnius import PythonJavaClass, java_method, autoclass, cast
from plyer.platforms.android import activity

Context = autoclass('android.content.Context')
Sensor = autoclass('android.hardware.Sensor')
SensorManager = autoclass('android.hardware.SensorManager')


class MFUSensorListener(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self):
        super().__init__()
        service = activity.getSystemService(Context.SENSOR_SERVICE)
        self.SensorManager = cast('android.hardware.SensorManager', service)

        self.sensor = self.SensorManager.getDefaultSensor(
            Sensor.TYPE_MAGNETIC_FIELD_UNCALIBRATED)
        self.values = [None, None, None, None, None, None]

    def enable(self):
        self.SensorManager.registerListener(
            self, self.sensor,
            SensorManager.SENSOR_DELAY_NORMAL
        )

    def disable(self):
        self.SensorManager.unregisterListener(self, self.sensor)

    @java_method('(Landroid/hardware/SensorEvent;)V')
    def onSensorChanged(self, event):
        self.values = event.values[:6]

    @java_method('(Landroid/hardware/Sensor;I)V')
    def onAccuracyChanged(self, sensor, accuracy):
        pass


class MagneticFieldSensorListener(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self):
        super().__init__()
        self.SensorManager = cast(
            'android.hardware.SensorManager',
            activity.getSystemService(Context.SENSOR_SERVICE)
        )
        self.sensor = self.SensorManager.getDefaultSensor(
            Sensor.TYPE_MAGNETIC_FIELD
        )

        self.values = [None, None, None]

    def enable(self):
        self.SensorManager.registerListener(
            self, self.sensor,
            SensorManager.SENSOR_DELAY_NORMAL
        )

    def disable(self):
        self.SensorManager.unregisterListener(self, self.sensor)

    @java_method('(Landroid/hardware/SensorEvent;)V')
    def onSensorChanged(self, event):
        self.values = event.values[:3]

    @java_method('(Landroid/hardware/Sensor;I)V')
    def onAccuracyChanged(self, sensor, accuracy):
        # Maybe, do something in future?
        pass


class AndroidCompass(Compass):
    def __init__(self):
        super().__init__()
        self.bState = False

    def _enable(self):
        if (not self.bState):
            self.listenerm = MagneticFieldSensorListener()
            self.listenermu = MFUSensorListener()
            self.listenerm.enable()
            self.listenermu.enable()
            self.bState = True

    def _disable(self):
        if (self.bState):
            self.bState = False
            self.listenerm.disable()
            self.listenermu.disable()
            del self.listenerm
            del self.listenermu

    def _get_orientation(self):
        if (self.bState):
            return tuple(self.listenerm.values)
        else:
            return (None, None, None)

    def _get_field_uncalib(self):
        if (self.bState):
            return tuple(self.listenermu.values)
        else:
            return (None, None, None, None, None, None)

    def __del__(self):
        if self.bState:
            self._disable()
        super().__del__()


def instance():
    return AndroidCompass()
