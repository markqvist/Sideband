'''
Speech to Text
==============

.. versionadded:: 1.4.0

Speech Recognition facade.

In order to check that your device supports voice recognition use method
`exist`.

Variable `language` indicates which language will be used to match words from
 voice.

Use `start` to start voice recognition immediately and `stop` to stop.

.. note::
    Needed permissions for Android: `RECORD_AUDIO` (and `INTERNET` if you want
    online voice recognition API to be used)

.. note::
    On Android platform, after execute `start` method you can hear BEEP!
    Mute sound in order to disable it.

.. note::
    For Android implementation to work there has to be an application with
    `android.speech.RecognitionService` implementation present in the system.
    Mostly it's `com.google.android.googlequicksearchbox` or "Google"
    application (the search bar with the launcher widget).

Offline Speech Recognition on Android
-------------------------------------

Requires any application that provides an
`android.speech.RecognitionService` implementation to the other apps. One of
such applications is on a lot of devices preinstalled Google (quick search
box).

The API prefers offline recognition, but should be able to switch to online
alternative in case you don't have a language package installed (`INTERNET`
permission necessary).

You can enable offline speech recognition this way (Android 8.1):

* open the `Settings` app
* choose `Language & Input` / `Language & Keyboard` (Samsung might include it
  in the `General` category)
* choose `On-Screen keyboard` or `Voice search`
* choose `Google Keyboard`
* choose `Offline Speech recognition`
* download language package if you don't have one already

Simple Examples
---------------

To start listening::

    >>> from plyer import stt
    >>> stt.start()

To retrieve partial results while listening::

    >>> assert stt.listening
    >>> print(stt.partial_results)

To stop listening::

    >>> stt.stop()

To retrieve results after the listening stopped::

    >>> print(stt.results)
'''


class STT:
    '''
    Speech to text facade.
    '''

    _language = 'en-US'
    '''
    Default language in which platform will try to recognize voice.
    In order to change language pick one from list by using
    `supported_languages` method.
    '''

    _supported_languages = [
        'en-US',
        'pl-PL'
    ]

    results = []
    '''
    List of sentences found while listening. It may consist of many similar
    and possible sentences that was recognition program.
    '''

    errors = []
    '''
    List of errors found while listening.
    '''

    partial_results = []
    '''
    List of results found while the listener is still being active.
    '''

    prefer_offline = True
    '''
    Preference whether to use offline language package necessary for
    each platform dependant implementation or online API.
    '''

    listening = False
    '''
    Current state of listening.
    '''

    @property
    def supported_languages(self):
        '''
        Return list of supported languages used in recognition.
        '''

        return self._supported_languages

    @property
    def language(self):
        '''
        Return current language.
        '''

        return self._language

    @language.setter
    def language(self, lang):
        '''
        Set current language.

        Value can not be set if it's not supported. See `supported_languages`
        to get what language you can set.

        .. note::
           We obviously can't check each language, therefore if you find
           that a specific language is available to you and the only limitation
           is our check for the internally defined `supported_languages`, feel
           free to open a pull request for adding your language to the list.
        '''

        if lang in self.supported_languages:
            self._language = lang

    # public methods
    def start(self):
        '''
        Start listening.
        '''

        self.results = []
        self.partial_results = []
        self._start()
        self.listening = True

    def stop(self):
        '''
        Stop listening.
        '''

        self._stop()
        self.listening = False

    def exist(self):
        '''
        Returns a boolean for speech recognition availability.
        '''

        return self._exist()

    # private methods
    def _start(self):
        raise NotImplementedError

    def _stop(self):
        raise NotImplementedError

    def _exist(self):
        raise NotImplementedError
