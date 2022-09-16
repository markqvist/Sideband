from jnius import autoclass
from jnius import cast
from jnius import java_method
from jnius import PythonJavaClass
from math import exp
from plyer.facades import Humidity
from plyer.platforms.android import activity

ActivityInfo = autoclass('android.content.pm.ActivityInfo')
Context = autoclass('android.content.Context')
Sensor = autoclass('android.hardware.Sensor')
SensorManager = autoclass('android.hardware.SensorManager')


class RelativeHumiditySensorListener(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self):
        super().__init__()
        service = activity.getSystemService(Context.SENSOR_SERVICE)
        self.SensorManager = cast('android.hardware.SensorManager', service)

        self.sensor = self.SensorManager.getDefaultSensor(
            Sensor.TYPE_RELATIVE_HUMIDITY)
        self.value = None

    def enable(self):
        self.SensorManager.registerListener(self, self.sensor,
                                            SensorManager.SENSOR_DELAY_NORMAL)

    def disable(self):
        self.SensorManager.unregisterListener(self, self.sensor)

    @java_method('(Landroid/hardware/SensorEvent;)V')
    def onSensorChanged(self, event):
        self.value = event.values[0]

    @java_method('(Landroid/hardware/Sensor;I)V')
    def onAccuracyChanged(self, sensor, accuracy):
        pass


class AmbientTemperatureSensorListener(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self):
        super().__init__()
        service = activity.getSystemService(Context.SENSOR_SERVICE)
        self.SensorManager = cast('android.hardware.SensorManager', service)

        self.sensor = self.SensorManager.getDefaultSensor(
            Sensor.TYPE_AMBIENT_TEMPERATURE)
        self.value = None

    def enable(self):
        self.SensorManager.registerListener(self, self.sensor,
                                            SensorManager.SENSOR_DELAY_NORMAL)

    def disable(self):
        self.SensorManager.unregisterListener(self, self.sensor)

    @java_method('(Landroid/hardware/SensorEvent;)V')
    def onSensorChanged(self, event):
        self.value = event.values[0]

    @java_method('(Landroid/hardware/Sensor;I)V')
    def onAccuracyChanged(self, sensor, accuracy):
        pass


class AndroidHumidity(Humidity):

    def __init__(self):
        self.state = False

    def _get_humidity(self):
        if self.state:
            m = 17.62
            Tn = 243.12
            Ta = 216.7
            Rh = self.listener_r.value
            Tc = self.listener_a.value
            A = 6.112
            K = 273.15
            humidity = (Ta * (Rh / 100) * A * exp(m * Tc / (Tn + Tc))
                        / (K + Tc))
            return humidity

    def _enable(self):
        if not self.state:
            self.listener_r = RelativeHumiditySensorListener()
            self.listener_a = AmbientTemperatureSensorListener()
            self.listener_r.enable()
            self.listener_a.enable()
            self.state = True

    def _disable(self):
        if self.state:
            self.listener_r.disable()
            self.listener_a.disable()
            self.state = False
            delattr(self, 'listener_r')
            delattr(self, 'listener_a')


def instance():
    return AndroidHumidity()
