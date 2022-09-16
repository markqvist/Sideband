from subprocess import Popen, PIPE
from plyer.facades import Processors
from plyer.utils import whereis_exe

from os import environ


class LinuxProcessors(Processors):
    def _get_state(self):
        old_lang = environ.get('LANG')
        environ['LANG'] = 'C'

        status = {"Number_of_Processors": None}

        dev = "--all"
        nproc_process = Popen(
            ["nproc", dev],
            stdout=PIPE
        )
        output = nproc_process.communicate()[0]

        environ['LANG'] = old_lang

        if not output:
            return status

        status['Number_of_Processors'] = output.rstrip()

        return status


def instance():
    import sys
    if whereis_exe('nproc'):
        return LinuxProcessors()
    sys.stderr.write("nproc not found.")
    return Processors()
