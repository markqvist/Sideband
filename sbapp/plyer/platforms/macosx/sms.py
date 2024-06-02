from subprocess import Popen, PIPE
from sbapp.plyer.facades import Sms as SMS
from sbapp.plyer.utils import whereis_exe


class MacOSSMS(SMS):
    '''
    Implementation of macOS' Messages API
    '''

    def _send(self, **kwargs):
        '''
        Will send `message` to `recipient` via Messages app

        By default, if `mode` is not explicitly set, `iMessage` is used.
        In order to use `SMS` mode, a valid carrier-activated device must
        be connected and configured.
        '''

        recipient = kwargs.get('recipient')
        message = kwargs.get('message')
        mode = kwargs.get('mode')  # Supported modes: iMessage (default), SMS
        if not mode:
            mode = 'iMessage'

        APPLESCRIPT = f"""tell application "Messages"
    set targetService to 1st account whose service type = {mode}
    set targetBuddy to participant "{recipient}" of targetService
    send "{message}" to targetBuddy
end tell"""

        osascript_process = Popen(
            ['osascript', '-e', APPLESCRIPT], stdout=PIPE, stderr=PIPE)
        stdout, stderr = osascript_process.communicate()


def instance():
    import sys
    if whereis_exe('osascript'):
        return MacOSSMS()
    sys.stderr.write('osascript not found.')
    return SMS()
