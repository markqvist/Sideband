'''
Module of Linux API for plyer.cpu.
'''

from os.path import join
from os import environ, listdir
from subprocess import Popen, PIPE
from plyer.facades import CPU
from plyer.utils import whereis_exe


class LinuxCPU(CPU):
    '''
    Implementation of Linux CPU API.
    '''

    def _sockets(self):
        # physical CPU sockets (or slots) on motherboard
        sockets = []  # list of CPU ids from kernel

        # open Linux kernel data file for CPU
        with open('/proc/cpuinfo', 'rb') as fle:
            lines = fle.readlines()

        # go through the lines and obtain physical CPU ids
        for line in lines:
            line = line.decode('utf-8')
            if 'physical id' not in line:
                continue
            cpuid = line.split(':')[1].strip()
            sockets.append(cpuid)

        # total sockets is the length of unique CPU ids from kernel
        sockets = len(set(sockets))
        return sockets

    def _physical(self):
        # cores
        physical = []  # list of CPU ids from kernel

        # open Linux kernel data file for CPU
        with open('/proc/cpuinfo', 'rb') as fle:
            lines = fle.readlines()

        # go through the lines and obtain CPU core ids
        for line in lines:
            line = line.decode('utf-8')
            if 'core id' not in line:
                continue
            cpuid = line.split(':')[1].strip()
            physical.append(cpuid)

        # total cores (socket * core per socket)
        # is the length of unique CPU core ids from kernel
        physical = len(set(physical))
        return physical

    def _logical(self):
        # cores * threads
        logical = None
        old_lang = environ.get('LANG', '')
        environ['LANG'] = 'C'

        _logical = Popen(['nproc', '--all'], stdout=PIPE)
        output = _logical.communicate()[0].decode('utf-8').strip()
        if output:
            logical = int(output)

        environ['LANG'] = old_lang
        return logical

    def _cache(self):
        values = {key: 0 for key in ('L1', 'L2', 'L3')}
        cpu_path = join('/sys', 'devices', 'system', 'cpu')

        # get present cores from kernel device
        with open(join(cpu_path, 'present')) as fle:
            present = fle.read().decode('utf-8')
        present = present.strip().split('-')

        if len(present) == 2:
            present = range(int(present[1]) + 1)
        else:
            present = [present[0]]

        cores = ['cpu{}'.format(i) for i in present]
        for core in cores:
            indicies = [
                # get 'indexN' files from 'cache' folder assuming
                # the filename is in range index0 to index99
                # in case a wild 'index_whatevercontent' file appears
                fle for fle in listdir(join(cpu_path, core, 'cache'))
                if fle.startswith('index') and len(fle) <= len('index') + 2
            ]

            for index in indicies:
                index_type = join(cpu_path, core, 'cache', index, 'level')
                with open(index_type, 'rb') as fle:
                    cache_level = fle.read().decode('utf-8').strip()
                values['L{}'.format(cache_level)] += 1
        return values

    @staticmethod
    def _numa():
        return


def instance():
    '''
    Instance for facade proxy.
    '''
    import sys
    if whereis_exe('nproc'):
        return LinuxCPU()
    sys.stderr.write("nproc not found.")
    return CPU()
