'''
Module of Linux API for plyer.uniqueid.
'''

from os import environ
from subprocess import Popen, PIPE
from plyer.facades import UniqueID
from plyer.utils import whereis_exe


class LinuxUniqueID(UniqueID):
    '''
    Implementation of Linux uniqueid API.
    '''

    def _get_uid(self):
        old_lang = environ.get('LANG')
        environ['LANG'] = 'C'
        stdout = Popen(
            ["lshw", "-quiet"],
            stdout=PIPE, stderr=PIPE
        ).communicate()[0].decode('utf-8')

        output = u''
        for line in stdout.splitlines():
            if 'serial:' not in line:
                continue
            output = line
            break

        environ['LANG'] = old_lang or u''
        result = None

        if output:
            result = output.split()[1]
        return result


def instance():
    '''
    Instance for facade proxy.
    '''
    import sys
    if whereis_exe('lshw'):
        return LinuxUniqueID()
    sys.stderr.write("lshw not found.")
    return UniqueID()
