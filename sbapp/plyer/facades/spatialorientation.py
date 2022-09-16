# coding=utf-8


class SpatialOrientation:
    '''Spatial Orientation facade.

    Computes the device's orientation based on the rotation matrix.

    .. versionadded:: 1.3.1
    '''

    @property
    def orientation(self):
        '''Property that returns values of the current device orientation
        as a (azimuth, pitch, roll) tuple.

        Azimuth, angle of rotation about the -z axis. This value represents the
        angle between the device's y axis and the magnetic north pole.
        The range of values is -π to π.

        Pitch, angle of rotation about the x axis. This value represents the
        angle between a plane parallel to the device's screen and a plane
        parallel to the ground.
        The range of values is -π to π.

        Roll, angle of rotation about the y axis. This value represents the
        angle between a plane perpendicular to the device's screen and a plane
        perpendicular to the ground.
        The range of values is -π/2 to π/2.

        Returns (None, None, None) if no data is currently available.

        Supported Platforms:: Android
        '''
        return self._get_orientation() or (None, None, None)

    def _get_orientation(self):
        raise NotImplementedError()

    def enable_listener(self):
        '''Enable the orientation sensor.
        '''
        self._enable_listener()

    def _enable_listener(self, **kwargs):
        raise NotImplementedError()

    def disable_listener(self):
        '''Disable the orientation sensor.
        '''
        self._disable_listener()

    def _disable_listener(self, **kwargs):
        raise NotImplementedError()
