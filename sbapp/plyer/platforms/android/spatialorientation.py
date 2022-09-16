from jnius import autoclass
from jnius import cast
from jnius import java_method
from jnius import PythonJavaClass
from plyer.platforms.android import activity
from plyer.facades import SpatialOrientation

Context = autoclass('android.content.Context')
Sensor = autoclass('android.hardware.Sensor')
SensorManager = autoclass('android.hardware.SensorManager')


class AccelerometerSensorListener(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self):
        super().__init__()
        self.SensorManager = cast(
            'android.hardware.SensorManager',
            activity.getSystemService(Context.SENSOR_SERVICE)
        )
        self.sensor = self.SensorManager.getDefaultSensor(
            Sensor.TYPE_ACCELEROMETER
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
        pass


class MagnetometerSensorListener(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self):
        super().__init__()
        service = activity.getSystemService(Context.SENSOR_SERVICE)
        self.SensorManager = cast('android.hardware.SensorManager', service)

        self.sensor = self.SensorManager.getDefaultSensor(
            Sensor.TYPE_MAGNETIC_FIELD)
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
        pass


class AndroidSpOrientation(SpatialOrientation):

    def __init__(self):
        self.state = False

    def _get_orientation(self):
        if self.state:
            rotation = [0] * 9
            inclination = [0] * 9
            gravity = []
            geomagnetic = []
            gravity = self.listener_a.values
            geomagnetic = self.listener_m.values
            if gravity[0] is not None and geomagnetic[0] is not None:
                ff_state = SensorManager.getRotationMatrix(
                    rotation, inclination,
                    gravity, geomagnetic
                )
                if ff_state:
                    values = [0, 0, 0]
                    values = SensorManager.getOrientation(
                        rotation, values
                    )
                return values

    def _enable_listener(self, **kwargs):
        if not self.state:
            self.listener_a = AccelerometerSensorListener()
            self.listener_m = MagnetometerSensorListener()
            self.listener_a.enable()
            self.listener_m.enable()
            self.state = True

    def _disable_listener(self, **kwargs):
        if self.state:
            self.listener_a.disable()
            self.listener_m.disable()
            self.state = False
            delattr(self, 'listener_a')
            delattr(self, 'listener_m')


def instance():
    return AndroidSpOrientation()
