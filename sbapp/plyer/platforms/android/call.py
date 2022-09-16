'''
Android Call
-----------
'''

from jnius import autoclass
from plyer.facades import Call
from plyer.platforms.android import activity

Intent = autoclass('android.content.Intent')
uri = autoclass('android.net.Uri')


class AndroidCall(Call):

    def _makecall(self, **kwargs):

        intent = Intent(Intent.ACTION_CALL)
        tel = kwargs.get('tel')
        intent.setData(uri.parse("tel:{}".format(tel)))
        activity.startActivity(intent)

    def _dialcall(self, **kwargs):
        intent_ = Intent(Intent.ACTION_DIAL)
        activity.startActivity(intent_)


def instance():
    return AndroidCall()
