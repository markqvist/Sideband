'''
IOS file chooser
--------------------

This module houses the iOS implementation of the plyer FileChooser.

.. versionadded:: 1.4.4
'''

from plyer.facades import FileChooser
from pyobjus import autoclass, protocol
from pyobjus.dylib_manager import load_framework


load_framework('/System/Library/Frameworks/Photos.framework')


class IOSFileChooser(FileChooser):
    '''
    FileChooser implementation for IOS using
    the built-in file browser via UIImagePickerController.

    .. versionadded:: 1.4.0
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._on_selection = None

    def _file_selection_dialog(self, *args, **kwargs):
        """
        Function called when action is required, A "mode" parameter specifies
        which and is one of "open", "save" or "dir".
        """
        self._on_selection = kwargs["on_selection"]
        if kwargs["mode"] == "open":
            self._open()
        else:
            raise NotImplementedError()

    def _get_picker(self):
        """
        Return an instantiated and configured UIImagePickerController.
        """
        picker = autoclass("UIImagePickerController")
        po = picker.alloc().init()
        po.sourceType = 0
        po.delegate = self
        return po

    def _open(self):
        """
        Launch the native iOS file browser. Upon selection, the
        `imagePickerController_didFinishPickingMediaWithInfo_` delegate is
        called where we close the file browser and handle the result.
        """
        picker = self._get_picker()
        UIApplication = autoclass('UIApplication')
        vc = UIApplication.sharedApplication().keyWindow.rootViewController()
        vc.presentViewController_animated_completion_(picker, True, None)

    @protocol('UIImagePickerControllerDelegate')
    def imagePickerController_didFinishPickingMediaWithInfo_(
            self, image_picker, frozen_dict):
        """
        Delegate which handles the result of the image selection process.
        """
        image_picker.dismissViewControllerAnimated_completion_(True, None)

        # Note: We need to call this Objective C class as there is currently
        #       no way to call a non-class function via pyobjus. And here,
        #       we have to use the `UIImagePNGRepresentation` to get the png
        #       representation. For this, please ensure you are using an
        #       appropriate version of kivy-ios.
        native_image_picker = autoclass("NativeImagePicker").alloc().init()
        path = native_image_picker.writeToPNG_(frozen_dict)
        self._on_selection([path.UTF8String()])


def instance():
    return IOSFileChooser()
