from time import sleep
from jnius import autoclass
from plyer.facades import TTS
from plyer.platforms.android import activity

Locale = autoclass('java.util.Locale')
TextToSpeech = autoclass('android.speech.tts.TextToSpeech')


class AndroidTextToSpeech(TTS):
    def _speak(self, **kwargs):
        tts = TextToSpeech(activity, None)

        tts.setLanguage(Locale.US)

        retries = 0  # First try rarely succeeds due to some timing issue
        message = kwargs.get('message')

        # first try for while loop
        speak_status = tts.speak(
            message, TextToSpeech.QUEUE_FLUSH, None
        )

        # -1 indicates error. Let's wait and then try again
        while retries < 100 and speak_status == -1:
            sleep(0.1)
            retries += 1
            speak_status = tts.speak(
                message, TextToSpeech.QUEUE_FLUSH, None
            )


def instance():
    return AndroidTextToSpeech()
