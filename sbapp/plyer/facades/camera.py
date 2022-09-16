'''
Camera
======

The :class:`Camera` is to capture pictures and make videos.

.. note::
        - On Android the `CAMERA` , `WRITE_EXTERNAL_STORAGE`,
          `READ_EXTERNAL_STORAGE` permissions are needed.

Simple Examples
---------------

Setup callback function.

    >>> from os.path import exists, join
    >>> from plyer import camera
    >>> def camera_callback(filepath):
    >>>     if(exists(filepath)):
    >>>         print "saved"
    >>>     else:
    >>>         print "unable to save."
    >>> filepath = 'path/to/your/file'
    >>> # e.g: filepath = join(App.get_running_app().user_data_dir, file_name)

To take picture::

    >>> file_name = "test.jpg"
    >>> camera.take_picture(filename=file_name,
    >>>                     on_complete=camera_callback)

Ta take a video::

    >>> file_name = "test.mp4"
    >>> camera.take_video(filename=file_name,
    >>>                   on_complete=camera_callback)

Supported Platforms
-------------------
Android, iOS

'''


class Camera:
    '''
    Camera facade.
    '''

    def take_picture(self, filename, on_complete):
        '''Ask the OS to capture a picture, and store it at filename.

        When the capture is done, on_complete will be called with the filename
        as an argument. If the callback returns True, the filename will be
        unlinked.

        :param filename: Name of the image file
        :param on_complete: Callback that will be called when the operation is
            done

        :type filename: str
        :type on_complete: callable
        '''
        self._take_picture(filename=filename, on_complete=on_complete)

    def take_video(self, filename, on_complete):
        '''Ask the OS to capture a video, and store it at filename.

        When the capture is done, on_complete will be called with the filename
        as an argument. If the callback returns True, the filename will be
        unlinked.

        :param filename: Name of the video file
        :param on_complete: Callback that will be called when the operation is
            done

        :type filename: str
        :type on_complete: callable
        '''
        self._take_video(filename=filename, on_complete=on_complete)

    # private

    def _take_picture(self, **kwargs):
        raise NotImplementedError()

    def _take_video(self, **kwargs):
        raise NotImplementedError()
