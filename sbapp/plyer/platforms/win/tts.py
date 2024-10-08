import subprocess
from sbapp.plyer.facades import TTS
from sbapp.plyer.utils import whereis_exe


class EspeakTextToSpeech(TTS):
    ''' Speaks using the espeak program
    '''
    def _speak(self, **kwargs):
        subprocess.call(["espeak", kwargs.get('message')])


def instance():
    if whereis_exe('espeak.exe'):
        return EspeakTextToSpeech()
    return TTS()
