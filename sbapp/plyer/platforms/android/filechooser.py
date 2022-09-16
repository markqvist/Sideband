'''
Android file chooser
--------------------

Android runs ``Activity`` asynchronously via pausing our ``PythonActivity``
and starting a new one in the foreground. This means
``AndroidFileChooser._open_file()`` will always return the default value of
``AndroidFileChooser.selection`` i.e. ``None``.

After the ``Activity`` (for us it's the file chooser ``Intent``) is completed,
Android moves it to the background (or destroys or whatever is implemented)
and pushes ``PythonActivity`` to the foreground.

We have a custom listener for ``android.app.Activity.onActivityResult()``
via `android` package from `python-for-android` recipe,
``AndroidFileChooser._on_activity_result()`` which is called independently of
any our action (we may call anything from our application in Python and this
handler will be called nevertheless on each ``android.app.Activity`` result
in the system).

In the handler we check if the ``request_code`` matches the code passed to the
``Context.startActivityForResult()`` i.e. if the result from
``android.app.Activity`` is indeed meant for our ``PythonActivity`` and then we
proceed.

Since the ``android.app.Activity.onActivityResult()`` is the only way for us
to intercept the result and we have a handler bound via ``android`` package,
we need to get the path/file/... selection to the user the same way.

Threading + ``Thread.join()`` or ``time.sleep()`` or any other kind of waiting
for the result is not an option because:

1) ``android.app.Activity.onActivityResult()`` might remain unexecuted if
the launched file chooser activity does not return the result (``Activity``
dies/freezes/etc).

2) Thread will be still waiting for the result e.g. an update of a value or
to actually finish, however the result from the call of
``AndroidFileChooser._open_file()`` will be returned nevertheless and anything
using that result will use an incorrect one i.e. the default value of
``AndroidFilechooser.selection`` (``None``).

.. versionadded:: 1.4.0
'''

from os.path import join, basename
from random import randint

from android import activity, mActivity
from jnius import autoclass, cast, JavaException
from plyer.facades import FileChooser
from plyer import storagepath

Environment = autoclass("android.os.Environment")
String = autoclass('java.lang.String')
Intent = autoclass('android.content.Intent')
Activity = autoclass('android.app.Activity')
DocumentsContract = autoclass('android.provider.DocumentsContract')
ContentUris = autoclass('android.content.ContentUris')
Uri = autoclass('android.net.Uri')
Long = autoclass('java.lang.Long')
IMedia = autoclass('android.provider.MediaStore$Images$Media')
VMedia = autoclass('android.provider.MediaStore$Video$Media')
AMedia = autoclass('android.provider.MediaStore$Audio$Media')


class AndroidFileChooser(FileChooser):
    '''
    FileChooser implementation for Android using
    the built-in file browser via Intent.

    .. versionadded:: 1.4.0
    '''

    # filechooser activity <-> result pair identification
    select_code = None

    # default selection value
    selection = None

    # select multiple files
    multiple = False

    # mime types
    mime_type = {
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument." +
                "wordprocessingml.document",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": "application/vnd.openxmlformats-officedocument." +
                "presentationml.presentation",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument." +
                "spreadsheetml.sheet",
        "text": "text/*",
        "pdf": "application/pdf",
        "zip": "application/zip",
        "image": "image/*",
        "video": "video/*",
        "audio": "audio/*",
        "application": "application/*"}

    selected_mime_type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.select_code = randint(123456, 654321)
        self.selection = None

        # bind a function for a response from filechooser activity
        activity.bind(on_activity_result=self._on_activity_result)

    @staticmethod
    def _handle_selection(selection):
        '''
        Dummy placeholder for returning selection from
        ``android.app.Activity.onActivityResult()``.

        .. versionadded:: 1.4.0
        '''
        return selection

    def _open_file(self, **kwargs):
        '''
        Running Android Activity is non-blocking and the only call
        that blocks is onActivityResult running in GUI thread

        .. versionadded:: 1.4.0
        '''

        # set up selection handler
        # startActivityForResult is async
        # onActivityResult is sync
        self._handle_selection = kwargs.pop(
            'on_selection', self._handle_selection
        )
        self.selected_mime_type = \
            kwargs.pop("filters")[0] if "filters" in kwargs else ""

        # create Intent for opening
        file_intent = Intent(Intent.ACTION_GET_CONTENT)
        if not self.selected_mime_type or \
            type(self.selected_mime_type) != str or \
                self.selected_mime_type not in self.mime_type:
            file_intent.setType("*/*")
        else:
            file_intent.setType(self.mime_type[self.selected_mime_type])
        file_intent.addCategory(
            Intent.CATEGORY_OPENABLE
        )

        # use putExtra to allow multiple file selection
        if kwargs.get('multiple', self.multiple):
            file_intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, True)

        # start a new activity from PythonActivity
        # which creates a filechooser via intent
        mActivity.startActivityForResult(
            Intent.createChooser(file_intent, cast(
                'java.lang.CharSequence',
                String("FileChooser")
            )),
            self.select_code
        )

    def _on_activity_result(self, request_code, result_code, data):
        '''
        Listener for ``android.app.Activity.onActivityResult()`` assigned
        via ``android.activity.bind()``.

        .. versionadded:: 1.4.0
        '''

        # not our response
        if request_code != self.select_code:
            return

        if result_code != Activity.RESULT_OK:
            # The action had been cancelled.
            return

        selection = []
        # Process multiple URI if multiple files selected
        try:
            for count in range(data.getClipData().getItemCount()):
                ele = self._resolve_uri(
                    data.getClipData().getItemAt(count).getUri()) or []
                selection.append(ele)
        except Exception:
            selection = [self._resolve_uri(data.getData()), ]

        # return value to object
        self.selection = selection
        # return value via callback
        self._handle_selection(selection)

    @staticmethod
    def _handle_external_documents(uri):
        '''
        Selection from the system filechooser when using ``Phone``
        or ``Internal storage`` or ``SD card`` option from menu.

        .. versionadded:: 1.4.0
        '''

        file_id = DocumentsContract.getDocumentId(uri)
        file_type, file_name = file_id.split(':')

        # internal SD card mostly mounted as a files storage in phone
        internal = storagepath.get_external_storage_dir()

        # external (removable) SD card i.e. microSD
        external = storagepath.get_sdcard_dir()
        try:
            external_base = basename(external)
        except TypeError:
            external_base = basename(internal)

        # resolve sdcard path
        sd_card = internal

        # because external might have /storage/.../1 or other suffix
        # and file_type might be only a part of the real folder in /storage
        if file_type in external_base or external_base in file_type:
            sd_card = external
        elif file_type == "home":
            sd_card = join(Environment.getExternalStorageDirectory(
            ).getAbsolutePath(), Environment.DIRECTORY_DOCUMENTS)

        return join(sd_card, file_name)

    @staticmethod
    def _handle_media_documents(uri):
        '''
        Selection from the system filechooser when using ``Images``
        or ``Videos`` or ``Audio`` option from menu.

        .. versionadded:: 1.4.0
        '''

        file_id = DocumentsContract.getDocumentId(uri)
        file_type, file_name = file_id.split(':')
        selection = '_id=?'

        if file_type == 'image':
            uri = IMedia.EXTERNAL_CONTENT_URI
        elif file_type == 'video':
            uri = VMedia.EXTERNAL_CONTENT_URI
        elif file_type == 'audio':
            uri = AMedia.EXTERNAL_CONTENT_URI
        return file_name, selection, uri

    @staticmethod
    def _handle_downloads_documents(uri):
        '''
        Selection from the system filechooser when using ``Downloads``
        option from menu. Might not work all the time due to:

        1) invalid URI:

        jnius.jnius.JavaException:
            JVM exception occurred: Unknown URI:
            content://downloads/public_downloads/1034

        2) missing URI / android permissions

        jnius.jnius.JavaException:
            JVM exception occurred:
            Permission Denial: reading
            com.android.providers.downloads.DownloadProvider uri
            content://downloads/all_downloads/1034 from pid=2532, uid=10455
            requires android.permission.ACCESS_ALL_DOWNLOADS,
            or grantUriPermission()

        Workaround:
            Selecting path from ``Phone`` -> ``Download`` -> ``<file>``
            (or ``Internal storage``) manually.

        .. versionadded:: 1.4.0
        '''

        # known locations, differ between machines
        downloads = [
            'content://downloads/public_downloads',
            'content://downloads/my_downloads',

            # all_downloads requires separate permission
            # android.permission.ACCESS_ALL_DOWNLOADS
            'content://downloads/all_downloads'
        ]

        file_id = DocumentsContract.getDocumentId(uri)
        try_uris = [
            ContentUris.withAppendedId(
                Uri.parse(down), Long.valueOf(file_id)
            )
            for down in downloads
        ]

        # try all known Download folder uris
        # and handle JavaExceptions due to different locations
        # for content:// downloads or missing permission
        path = None
        for down in try_uris:
            try:
                path = AndroidFileChooser._parse_content(
                    uri=down, projection=['_data'],
                    selection=None,
                    selection_args=None,
                    sort_order=None
                )

            except JavaException:
                import traceback
                traceback.print_exc()

            # we got a path, ignore the rest
            if path:
                break

        # alternative approach to Downloads by joining
        # all data items from Activity result
        if not path:
            for down in try_uris:
                try:
                    path = AndroidFileChooser._parse_content(
                        uri=down, projection=None,
                        selection=None,
                        selection_args=None,
                        sort_order=None,
                        index_all=True
                    )

                except JavaException:
                    import traceback
                    traceback.print_exc()

                # we got a path, ignore the rest
                if path:
                    break
        return path

    def _resolve_uri(self, uri):
        '''
        Resolve URI input from ``android.app.Activity.onActivityResult()``.

        .. versionadded:: 1.4.0
        '''

        uri_authority = uri.getAuthority()
        uri_scheme = uri.getScheme().lower()

        path = None
        file_name = None
        selection = None
        downloads = None

        # This does not allow file selected from google photos or gallery
        # or even any other file explorer to work
        # not a document URI, nothing to convert from
        # if not DocumentsContract.isDocumentUri(mActivity, uri):
        #     return path

        if uri_authority == 'com.android.externalstorage.documents':
            return self._handle_external_documents(uri)

        # in case a user selects a file from 'Downloads' section
        # note: this won't be triggered if a user selects a path directly
        #       e.g.: Phone -> Download -> <some file>
        elif uri_authority == 'com.android.providers.downloads.documents':
            path = downloads = self._handle_downloads_documents(uri)

        elif uri_authority == 'com.android.providers.media.documents':
            file_name, selection, uri = self._handle_media_documents(uri)

        # parse content:// scheme to path
        if uri_scheme == 'content' and not downloads:
            try:
                path = self._parse_content(
                    uri=uri, projection=['_data'], selection=selection,
                    selection_args=file_name, sort_order=None
                )
            except JavaException:  # handles array error for selection_args
                path = self._parse_content(
                    uri=uri, projection=['_data'], selection=selection,
                    selection_args=[file_name], sort_order=None
                )

        # nothing to parse, file:// will return a proper path
        elif uri_scheme == 'file':
            path = uri.getPath()

        return path

    @staticmethod
    def _parse_content(
            uri, projection, selection, selection_args, sort_order,
            index_all=False
    ):
        '''
        Parser for ``content://`` URI returned by some Android resources.

        .. versionadded:: 1.4.0
        '''

        result = None
        resolver = mActivity.getContentResolver()
        read = Intent.FLAG_GRANT_READ_URI_PERMISSION
        write = Intent.FLAG_GRANT_READ_URI_PERMISSION
        persist = Intent.FLAG_GRANT_READ_URI_PERMISSION

        # grant permission for our activity
        mActivity.grantUriPermission(
            mActivity.getPackageName(),
            uri,
            read | write | persist
        )

        if not index_all:
            cursor = resolver.query(
                uri, projection, selection,
                selection_args, sort_order
            )

            idx = cursor.getColumnIndex(projection[0])
            if idx != -1 and cursor.moveToFirst():
                result = cursor.getString(idx)
        else:
            result = []
            cursor = resolver.query(
                uri, projection, selection,
                selection_args, sort_order
            )
            while cursor.moveToNext():
                for idx in range(cursor.getColumnCount()):
                    result.append(cursor.getString(idx))
            result = '/'.join(result)
        return result

    def _file_selection_dialog(self, **kwargs):
        mode = kwargs.pop('mode', None)
        if mode == 'open':
            self._open_file(**kwargs)


def instance():
    return AndroidFileChooser()
