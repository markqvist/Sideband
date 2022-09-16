from jnius import autoclass
from jnius import cast
from jnius import java_method
from jnius import PythonJavaClass

from plyer.platforms.android import activity
from plyer.facades import Proximity

ActivityInfo = autoclass('android.content.pm.ActivityInfo')
Context = autoclass('android.content.Context')
Sensor = autoclass('android.hardware.Sensor')
SensorManager = autoclass('android.hardware.SensorManager')


class ProximitySensorListener(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self):
        super().__init__()
        service = activity.getSystemService(Context.SENSOR_SERVICE)
        self.SensorManager = cast('android.hardware.SensorManager', service)

        self.sensor = self.SensorManager.getDefaultSensor(
            Sensor.TYPE_PROXIMITY)
        self.value = None

    def enable(self):
        self.SensorManager.registerListener(
            self, self.sensor,
            SensorManager.SENSOR_DELAY_NORMAL
        )

    def disable(self):
        self.SensorManager.unregisterListener(self, self.sensor)

    @java_method('(Landroid/hardware/SensorEvent;)V')
    def onSensorChanged(self, event):
        self.value = event.values[0]

    @java_method('(Landroid/hardware/Sensor;I)V')
    def onAccuracyChanged(self, sensor, accuracy):
        pass


class AndroidProximity(Proximity):

    listener = None

    def _enable(self, **kwargs):
        if not self.listener:
            self.listener = ProximitySensorListener()
            self.listener.enable()

    def _disable(self, **kwargs):
        if self.listener:
            self.listener.disable()
            delattr(self, 'listener')

    def _get_proximity(self):
        if self.listener:
            value = self.listener.value
            # value is 0.0 when proxime sensor is covered. In other case
            # value is 5.0 because in smartphone, optical proximity sensors
            # are used.
            return value < 5.0


def instance():
    return AndroidProximity()
