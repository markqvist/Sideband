'''
Module of Android API for plyer.email.
'''

from jnius import autoclass, cast
from plyer.facades import Email
from plyer.platforms.android import activity

Intent = autoclass('android.content.Intent')
AndroidString = autoclass('java.lang.String')


class AndroidEmail(Email):
    '''
    Implementation of Android email API.
    '''

    def _send(self, **kwargs):
        intent = Intent(Intent.ACTION_SEND)
        intent.setType('text/plain')

        recipient = kwargs.get('recipient')
        subject = kwargs.get('subject')
        text = kwargs.get('text')
        create_chooser = kwargs.get('create_chooser')

        if recipient:
            intent.putExtra(Intent.EXTRA_EMAIL, [recipient])
        if subject:
            android_subject = cast(
                'java.lang.CharSequence',
                AndroidString(subject)
            )
            intent.putExtra(Intent.EXTRA_SUBJECT, android_subject)
        if text:
            android_text = cast(
                'java.lang.CharSequence',
                AndroidString(text)
            )
            intent.putExtra(Intent.EXTRA_TEXT, android_text)

        if create_chooser:
            chooser_title = cast(
                'java.lang.CharSequence',
                AndroidString('Send message with:')
            )
            activity.startActivity(
                Intent.createChooser(intent, chooser_title)
            )
        else:
            activity.startActivity(intent)


def instance():
    '''
    Instance for facade proxy.
    '''
    return AndroidEmail()
