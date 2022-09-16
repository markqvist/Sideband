from pyobjus import autoclass, objc_str
from pyobjus.dylib_manager import load_framework

from plyer.facades import TTS

load_framework('/System/Library/Frameworks/AVFoundation.framework')
AVSpeechUtterance = autoclass('AVSpeechUtterance')
AVSpeechSynthesizer = autoclass('AVSpeechSynthesizer')
AVSpeechSynthesisVoice = autoclass('AVSpeechSynthesisVoice')


class iOSTextToSpeech(TTS):
    def __init__(self):
        super().__init__()
        self.synth = AVSpeechSynthesizer.alloc().init()
        self.voice = None

    def _set_locale(self, locale="en-US"):
        self.voice = AVSpeechSynthesisVoice.voiceWithLanguage_(
            objc_str(locale)
        )

    def _speak(self, **kwargs):
        message = kwargs.get('message')

        if(not self.voice):
            self._set_locale()

        utterance = \
            AVSpeechUtterance.speechUtteranceWithString_(objc_str(message))

        utterance.voice = self.voice
        self.synth.speakUtterance_(utterance)


def instance():
    return iOSTextToSpeech()
