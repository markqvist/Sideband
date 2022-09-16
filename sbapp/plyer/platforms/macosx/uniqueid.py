'''
Module of MacOS API for plyer.uniqueid.
'''

from os import environ
from subprocess import Popen, PIPE
from plyer.facades import UniqueID
from plyer.utils import whereis_exe


class OSXUniqueID(UniqueID):
    '''
    Implementation of MacOS uniqueid API.
    '''

    def _get_uid(self):
        old_lang = environ.get('LANG')
        environ['LANG'] = 'C'

        ioreg_process = Popen(["ioreg", "-l"], stdout=PIPE)
        grep_process = Popen(
            ["grep", "IOPlatformSerialNumber"],
            stdin=ioreg_process.stdout, stdout=PIPE
        )
        ioreg_process.stdout.close()
        output = grep_process.communicate()[0]

        if old_lang is None:
            environ.pop('LANG')
        else:
            environ['LANG'] = old_lang

        result = None
        if output:
            result = output.split()[3][1:-1]
        return result


def instance():
    '''
    Instance for facade proxy.
    '''
    import sys
    if whereis_exe('ioreg'):
        return OSXUniqueID()
    sys.stderr.write("ioreg not found.")
    return UniqueID()
