'''
Mac OS X file chooser
---------------------
'''

from plyer.facades import FileChooser
from pyobjus import autoclass, objc_arr, objc_str
from pyobjus.dylib_manager import load_framework, INCLUDE

load_framework(INCLUDE.AppKit)
NSURL = autoclass('NSURL')
NSOpenPanel = autoclass('NSOpenPanel')
NSSavePanel = autoclass('NSSavePanel')
NSOKButton = 1


class MacFileChooser:
    '''A native implementation of file chooser dialogs using Apple's API
    through pyobjus.

    Not implemented features:
    * filters (partial, wildcards are converted to extensions if possible.
        Pass the Mac-specific "use_extensions" if you can provide
        Mac OS X-compatible to avoid automatic conversion)
    * multiple (only for save dialog. Available in open dialog)
    * icon
    * preview
    '''

    mode = "open"
    path = None
    multiple = False
    filters = []
    preview = False
    title = None
    icon = None
    show_hidden = False
    use_extensions = False

    def __init__(self, *args, **kwargs):
        self._handle_selection = kwargs.pop(
            'on_selection', self._handle_selection
        )

        # Simulate Kivy's behavior
        for i in kwargs:
            setattr(self, i, kwargs[i])

    @staticmethod
    def _handle_selection(selection):
        '''
        Dummy placeholder for returning selection from chooser.
        '''
        return selection

    def run(self):
        panel = None
        if self.mode in ("open", "dir", "dir_and_files"):
            panel = NSOpenPanel.openPanel()

            panel.setCanChooseDirectories_(self.mode != "open")
            panel.setCanChooseFiles_(self.mode != "dir")

            if self.multiple:
                panel.setAllowsMultipleSelection_(True)
        elif self.mode == "save":
            panel = NSSavePanel.savePanel()
        else:
            assert False, self.mode

        panel.setCanCreateDirectories_(True)
        panel.setShowsHiddenFiles_(self.show_hidden)

        if self.title:
            panel.setTitle_(objc_str(self.title))

        # Mac OS X does not support wildcards unlike the other platforms.
        # This tries to convert wildcards to "extensions" when possible,
        # ans sets the panel to also allow other file types, just to be safe.
        if self.filters:
            filthies = []
            for f in self.filters:
                if type(f) == str:
                    f = (None, f)
                for s in f[1:]:
                    if not self.use_extensions:
                        if s.strip().endswith("*"):
                            continue
                    pystr = s.strip().split("*")[-1].split(".")[-1]
                    filthies.append(objc_str(pystr))

            ftypes_arr = objc_arr(*filthies)
            # todo: switch to allowedContentTypes
            panel.setAllowedFileTypes_(ftypes_arr)
            panel.setAllowsOtherFileTypes_(not self.use_extensions)

        if self.path:
            url = NSURL.fileURLWithPath_(self.path)
            panel.setDirectoryURL_(url)

        selection = None

        if panel.runModal():
            if self.mode == "save" or not self.multiple:
                selection = [panel.filename().UTF8String()]
            else:
                filename = panel.filenames()
                selection = [
                    filename.objectAtIndex_(x).UTF8String()
                    for x in range(filename.count())]

        self._handle_selection(selection)

        return selection


class MacOSXFileChooser(FileChooser):
    '''
    FileChooser implementation for macOS using NSOpenPanel, NSSavePanel.
    '''
    def _file_selection_dialog(self, **kwargs):
        return MacFileChooser(**kwargs).run()


def instance():
    return MacOSXFileChooser()
