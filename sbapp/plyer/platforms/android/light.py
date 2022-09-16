from jnius import autoclass
from jnius import cast
from jnius import java_method
from jnius import PythonJavaClass

from plyer.facades import Light
from plyer.platforms.android import activity

Context = autoclass('android.content.Context')
Sensor = autoclass('android.hardware.Sensor')
SensorManager = autoclass('android.hardware.SensorManager')


class LightSensorListener(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self):
        super().__init__()
        service = activity.getSystemService(Context.SENSOR_SERVICE)
        self.SensorManager = cast('android.hardware.SensorManager', service)
        self.sensor = self.SensorManager.getDefaultSensor(Sensor.TYPE_LIGHT)
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


class AndroidLight(Light):

    listener = None

    def _get_illumination(self):
        if self.listener and self.listener.value:
            light = self.listener.value
            return light

    def _enable(self):
        if not self.listener:
            self.listener = LightSensorListener()
            self.listener.enable()

    def _disable(self):
        if self.listener:
            self.listener.disable()
            delattr(self, 'listener')


def instance():
    return AndroidLight()
