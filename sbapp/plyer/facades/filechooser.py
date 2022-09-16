'''
Native filechooser dialog facade.
=================================

open_file, save_file and choose_dir accept a number of arguments
listed below. They return either a list of paths (normally
absolute), or None if no file was selected or the operation was
canceled and no result is available.

Arguments:
    * **path** *(string or None)*: a path that will be selected
        by default, or None
    * **multiple** *(bool)*: True if you want the dialog to
        allow multiple file selection. (Note: Windows doesn't
        support multiple directory selection)
    * **filters** *(iterable)*: either a list of wildcard patterns
        or of sequences that contain the name of the filter and any
        number of wildcards that will be grouped under that name
        (e.g. [["Music", "*mp3", "*ogg", "*aac"], "*jpg", "*py"])
    * **preview** *(bool)*: True if you want the file chooser to
        show a preview of the selected file, if supported by the
        back-end.
    * **title** *(string or None)*: The title of the file chooser
        window, or None for the default title.
    * **icon** *(string or None)*: Path to the icon of the file
        chooser window (where supported), or None for the back-end's
        default.
    * **show_hidden** *(bool)*: Force showing hidden files (currently
        supported only on Windows)
    * **on_selection** *(func)*: Callback for fetching the selection.

Important: these methods will return only after user interaction.
Use threads or you will stop the mainloop if your app has one.

.. versionchanged:: 1.4.0
    Added Android implementation for open_file()
    Added ``on_selection`` kwarg for callback function

Supported Plaforms
------------------
Android, iOS, macOS, Linux, Windows
'''


class FileChooser:
    '''
    File Chooser facade.
    '''

    def open_file(self, *args, **kwargs):
        """
        Open the file chooser in "open" mode.
        """
        return self._file_selection_dialog(mode="open", *args, **kwargs)

    def save_file(self, *args, **kwargs):
        """
        Open the file chooser in "save" mode. Confirmation will be asked
        when a file with the same name already exists.
        """
        return self._file_selection_dialog(mode="save", *args, **kwargs)

    def choose_dir(self, *args, **kwargs):
        """
        Open the directory chooser. Note that on Windows this is very
        limited. Consider writing your own chooser if you target that
        platform and are planning on using unsupported features.
        """
        return self._file_selection_dialog(mode="dir", *args, **kwargs)

    # private

    def _file_selection_dialog(self, **kwargs):
        raise NotImplementedError()
