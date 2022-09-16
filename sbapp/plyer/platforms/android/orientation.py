from jnius import autoclass
from plyer.platforms.android import activity
from plyer.facades import Orientation

ActivityInfo = autoclass('android.content.pm.ActivityInfo')


class AndroidOrientation(Orientation):

    def _set_landscape(self, **kwargs):
        reverse = kwargs.get('reverse')
        if reverse:
            activity.setRequestedOrientation(
                ActivityInfo.SCREEN_ORIENTATION_REVERSE_LANDSCAPE)
        else:
            activity.setRequestedOrientation(
                ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE)

    def _set_portrait(self, **kwargs):
        reverse = kwargs.get('reverse')
        if reverse:
            activity.setRequestedOrientation(
                ActivityInfo.SCREEN_ORIENTATION_REVERSE_PORTRAIT)
        else:
            activity.setRequestedOrientation(
                ActivityInfo.SCREEN_ORIENTATION_PORTRAIT)

    def _set_sensor(self, **kwargs):
        mode = kwargs.get('mode')

        if mode == 'any':
            activity.setRequestedOrientation(
                ActivityInfo.SCREEN_ORIENTATION_SENSOR)
        elif mode == 'landscape':
            activity.setRequestedOrientation(
                ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE)
        elif mode == 'portrait':
            activity.setRequestedOrientation(
                ActivityInfo.SCREEN_ORIENTATION_SENSOR_PORTRAIT)


def instance():
    return AndroidOrientation()
