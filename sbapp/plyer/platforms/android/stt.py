from android.runnable import run_on_ui_thread

from jnius import autoclass
from jnius import java_method
from jnius import PythonJavaClass

from plyer.facades import STT
from plyer.platforms.android import activity

ArrayList = autoclass('java.util.ArrayList')
Bundle = autoclass('android.os.Bundle')
Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
RecognizerIntent = autoclass('android.speech.RecognizerIntent')
RecognitionListener = autoclass('android.speech.RecognitionListener')
SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')

SpeechResults = SpeechRecognizer.RESULTS_RECOGNITION


class SpeechListener(PythonJavaClass):
    __javainterfaces__ = ['android/speech/RecognitionListener']

    # class variables because PythonJavaClass class failed
    # to see them later in getters and setters
    _error_callback = None
    _result_callback = None
    _partial_result_callback = None
    _volume_callback = None

    def __init__(self):
        super().__init__()

        # overwrite class variables in the object
        self._error_callback = None
        self._result_callback = None
        self._partial_result_callback = None
        self._volume_callback = None

    # error handling
    @property
    def error_callback(self):
        return self._error_callback

    @error_callback.setter
    def error_callback(self, callback):
        '''
        Set error callback. It is called when error occurs.

        :param callback: function with one parameter for error message
        '''

        self._error_callback = callback

    # result handling
    @property
    def result_callback(self):
        return self._result_callback

    @result_callback.setter
    def result_callback(self, callback):
        '''
        Set result callback. It is called when results are received.

        :param callback: function with one parameter for lists of strings
        '''

        self._result_callback = callback

    @property
    def partial_result_callback(self):
        return self._partial_result_callback

    @partial_result_callback.setter
    def partial_result_callback(self, callback):
        '''
        Set partial result callback. It is called when partial results are
        received while the listener is still in listening mode.

        :param callback: function with one parameter for lists of strings
        '''

        self._partial_result_callback = callback

    # voice changes handling
    @property
    def volume_callback(self):
        return self._volume_callback

    @volume_callback.setter
    def volume_callback(self, callback):
        '''
        Set volume voice callback.

        It is called when loudness of the voice changes.

        :param callback: function with one parameter for volume RMS dB (float).
        '''
        self._volume_callback = callback

    # Implementation Java Interfaces
    @java_method('()V')
    def onBeginningOfSpeech(self):
        pass

    @java_method('([B)V')
    def onBufferReceived(self, buffer):
        pass

    @java_method('()V')
    def onEndOfSpeech(self):
        pass

    @java_method('(I)V')
    def onError(self, error):
        msg = ''
        if error == SpeechRecognizer.ERROR_AUDIO:
            msg = 'audio'
        if error == SpeechRecognizer.ERROR_CLIENT:
            msg = 'client'
        if error == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS:
            msg = 'insufficient_permissions'
        if error == SpeechRecognizer.ERROR_NETWORK:
            msg = 'network'
        if error == SpeechRecognizer.ERROR_NETWORK_TIMEOUT:
            msg = 'network_timeout'
        if error == SpeechRecognizer.ERROR_NO_MATCH:
            msg = 'no_match'
        if error == SpeechRecognizer.ERROR_RECOGNIZER_BUSY:
            msg = 'recognizer_busy'
        if error == SpeechRecognizer.ERROR_SERVER:
            msg = 'server'
        if error == SpeechRecognizer.ERROR_SPEECH_TIMEOUT:
            msg = 'speech_timeout'

        if msg and self.error_callback:
            self.error_callback('error:' + msg)

    @java_method('(ILandroid/os/Bundle;)V')
    def onEvent(self, event_type, params):
        pass

    @java_method('(Landroid/os/Bundle;)V')
    def onPartialResults(self, results):
        texts = []
        matches = results.getStringArrayList(SpeechResults)
        for match in matches.toArray():
            if isinstance(match, bytes):
                match = match.decode('utf-8')
            texts.append(match)

        if texts and self.partial_result_callback:
            self.partial_result_callback(texts)

    @java_method('(Landroid/os/Bundle;)V')
    def onReadyForSpeech(self, params):
        pass

    @java_method('(Landroid/os/Bundle;)V')
    def onResults(self, results):
        texts = []
        matches = results.getStringArrayList(SpeechResults)
        for match in matches.toArray():
            if isinstance(match, bytes):
                match = match.decode('utf-8')
            texts.append(match)

        if texts and self.result_callback:
            self.result_callback(texts)

    @java_method('(F)V')
    def onRmsChanged(self, rmsdB):
        if self.volume_callback:
            self.volume_callback(rmsdB)


class AndroidSpeech(STT):
    '''
    Android Speech Implementation.

    Android class `SpeechRecognizer`'s listening deactivates automatically.

    Class methods `_on_error()`, `_on_result()` listeners. You can find
    documentation here:
    https://developer.android.com/reference/android/speech/RecognitionListener
    '''

    def _on_error(self, msg):
        self.errors.append(msg)
        self.stop()

    def _on_result(self, messages):
        self.results.extend(messages)
        self.stop()

    def _on_partial(self, messages):
        self.partial_results.extend(messages)

    @run_on_ui_thread
    def _start(self):
        intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        intent.putExtra(
            RecognizerIntent.EXTRA_CALLING_PACKAGE,
            activity.getPackageName()
        )

        # language preferences
        intent.putExtra(
            RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, self.language
        )
        intent.putExtra(
            RecognizerIntent.EXTRA_LANGUAGE_MODEL,
            RecognizerIntent.LANGUAGE_MODEL_WEB_SEARCH
        )

        # results settings
        intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1000)
        intent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, True)
        if self.prefer_offline:
            intent.putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, True)

        # listener and callbacks
        listener = SpeechListener()
        listener.error_callback = self._on_error
        listener.result_callback = self._on_result
        listener.partial_result_callback = self._on_partial

        # create recognizer and start
        self.speech = SpeechRecognizer.createSpeechRecognizer(activity)
        self.speech.setRecognitionListener(listener)
        self.speech.startListening(intent)

    @run_on_ui_thread
    def _stop(self):
        if not self.speech:
            return

        # stop listening
        self.speech.stopListening()

        # free object
        self.speech.destroy()
        self.speech = None

    def _exist(self):
        return bool(
            SpeechRecognizer.isRecognitionAvailable(activity)
        )


def instance():
    return AndroidSpeech()
