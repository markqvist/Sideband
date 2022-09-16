from jnius import autoclass
from jnius import cast
from jnius import java_method
from jnius import PythonJavaClass

from plyer.facades import Temperature
from plyer.platforms.android import activity

ActivityInfo = autoclass('android.content.pm.ActivityInfo')
Context = autoclass('android.content.Context')
Sensor = autoclass('android.hardware.Sensor')
SensorManager = autoclass('android.hardware.SensorManager')


class TemperatureSensorListener(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self):
        super().__init__()
        service = activity.getSystemService(Context.SENSOR_SERVICE)
        self.SensorManager = cast('android.hardware.SensorManager', service)

        self.sensor = self.SensorManager.getDefaultSensor(
            Sensor.TYPE_AMBIENT_TEMPERATURE)
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


class AndroidTemperature(Temperature):

    listener = None

    def _get_temperature(self):
        if self.listener and self.listener.value:
            temperature = self.listener.value
            return temperature

    def _enable(self):
        if not self.listener:
            self.listener = TemperatureSensorListener()
            self.listener.enable()

    def _disable(self):
        if self.listener:
            self.listener.disable()
            delattr(self, 'listener')


def instance():
    return AndroidTemperature()
