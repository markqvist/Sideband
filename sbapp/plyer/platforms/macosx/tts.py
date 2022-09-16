import subprocess
from plyer.facades import TTS
from plyer.utils import whereis_exe


class NativeSayTextToSpeech(TTS):
    '''Speaks using the native OSX 'say' command
    '''
    def _speak(self, **kwargs):
        subprocess.call(["say", kwargs.get('message')])


class EspeakTextToSpeech(TTS):
    '''Speaks using the espeak program
    '''
    def _speak(self, **kwargs):
        subprocess.call(["espeak", kwargs.get('message')])


def instance():
    if whereis_exe('say'):
        return NativeSayTextToSpeech()
    elif whereis_exe('espeak'):
        return EspeakTextToSpeech()
    return TTS()
