'''
TestCPU
=======

Tested platforms:

* Windows
* Linux - nproc
'''

import unittest
from os import environ
from os.path import join
from mock import patch, Mock
from textwrap import dedent

from plyer.tests.common import PlatformTest, platform_import, splitpath


class MockedKernelCPU:
    def __init__(self, *args, **kwargs):
        self.fname = args[0] if args else ''
        self.cpu_path = join('/sys', 'devices', 'system', 'cpu')
        self.cores = 16
        self.indicies = 4

    def __enter__(self, *args):
        file_value = None
        cpu_path = self.cpu_path
        spath = splitpath(self.fname)

        if self.fname == join(cpu_path, 'present'):
            file_value = Mock()
            file_value.read.return_value = self.present
        elif spath[5] == 'cache' and spath[7] == 'level':
            file_value = Mock()
            # force bytes, because reading files as bytes
            file_value.read.return_value = str(
                self.index_types[spath[4]][spath[6]][spath[7]]
            ).encode('utf-8')
        return file_value

    def __exit__(self, *args):
        pass

    @property
    def present(self):
        rng = list(range(self.cores))
        start = str(rng[0])
        end = str(rng[-1])
        if start == end:  # cores == 1 --> b'0'
            value = str(start)
        else:  # cores > 1 --> b'0-n'
            value = str('-'.join([start, end]))
        return value.encode('utf-8')

    @property
    def listdir(self):
        return ['index{}'.format(i) for i in range(self.indicies)]

    @property
    def index_types(self):
        # assign L1 to index0-1, L2 to 2, L3 to 3
        types = {0: 1, 1: 1, 2: 2, 3: 3}

        return {
            'cpu{}'.format(c): {
                'index{}'.format(i): {
                    'level': types[i]
                }
                for i in range(self.indicies)
            }
            for c in range(self.cores)
        }


class MockedNProc:
    '''
    Mocked object used instead of 'nproc' binary in the Linux specific API
    plyer.platforms.linux.cpu. The same output structure is tested for
    the range of <min_version, max_version>.

    .. note:: Extend the object with another data sample if it does not match.
    '''

    min_version = '8.21'
    max_version = '8.21'
    logical_cores = 99

    def __init__(self, *args, **kwargs):
        # only to ignore all args, kwargs
        pass

    @staticmethod
    def communicate():
        '''
        Mock Popen.communicate, so that 'nproc' isn't used.
        '''
        return (str(MockedNProc.logical_cores).encode('utf-8'), )

    @staticmethod
    def whereis_exe(binary):
        '''
        Mock whereis_exe, so that it looks like
        Linux NProc binary is present on the system.
        '''
        return binary == 'nproc'

    @staticmethod
    def logical():
        '''
        Return percentage from mocked data.
        '''
        return int(MockedNProc.logical_cores)


class MockedProcinfo:
    # docs:
    # https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
    # /tree/arch/x86/kernel/cpu/proc.c
    sockets = 1  # physical id
    physical = 2  # core id
    threads_per_core = 2  # Intel specs document for i7-4500U
    logical = physical * threads_per_core  # processor

    def __init__(self, *args, **kwargs):
        self.fname = args[0] if args else ''

        self.output = []
        __step = 0  # 0,1,0,1 -> 0,0,1,1
        for soc in range(self.sockets):
            for log in range(self.logical):
                if log != 0 and not log % self.physical:
                    __step += 1
                self.output.append((dedent(
                    '''\
                    processor\t: {logical}
                    vendor_id\t: GenuineIntel
                    cpu family\t: 6
                    model\t\t: 69
                    model name\t: Intel(R) Core(TM) i7-4500U CPU @ 1.80GHz
                    stepping\t: 1
                    microcode\t: 0x17
                    cpu MHz\t\t: 774.000
                    cache size\t: 4096 KB
                    physical id\t: {socket}
                    siblings\t: 4
                    core id\t\t: {physical}
                    cpu cores\t: {threads_per_core}
                    apicid\t\t: {logical}
                    initial apicid\t: 0
                    fpu\t\t: yes
                    fpu_exception\t: yes
                    cpuid level\t: 13
                    wp\t\t: yes
                    flags\t\t: fpu vme de pse tsc msr pae mce cx8 ...
                    bogomips\t: 3591.40
                    clflush size\t: 64
                    cache_alignment\t: 64
                    address sizes\t: 39 bits physical, 48 bits virtual
                    power management:
                    \n'''
                )).format(**{
                    'socket': soc,
                    'physical': __step,
                    'logical': log,
                    'threads_per_core': self.threads_per_core
                }))
        self.output = ''.join(self.output).encode('utf-8')

    def __enter__(self, *args):
        file_value = None

        if self.fname == '/proc/cpuinfo':
            file_value = Mock()
            file_value.readlines.return_value = self.output.split(
                '\n'.encode('utf-8')
            )
        return file_value

    def __exit__(self, *args):
        pass


class TestCPU(unittest.TestCase):
    '''
    TestCase for plyer.cpu.
    '''

    def test_cpu_linux_physical(self):
        cpu = platform_import(
            platform='linux',
            module_name='cpu',
            whereis_exe=lambda b: b == 'nproc'
        ).instance()

        stub = MockedProcinfo
        target = 'builtins.open'

        with patch(target=target, new=stub):
            sb = stub()
            self.assertEqual(
                cpu.physical, sb.physical
            )

    def test_cpu_linux_logical(self):
        '''
        Test mocked Linux NProc for plyer.cpu.
        '''
        cpu = platform_import(
            platform='linux',
            module_name='cpu',
            whereis_exe=MockedNProc.whereis_exe
        )
        cpu.Popen = MockedNProc
        cpu = cpu.instance()

        self.assertEqual(
            cpu.logical, MockedNProc.logical()
        )

    @PlatformTest('linux')
    def test_cpu_linux_cache(self):
        cpu = platform_import(
            platform='linux',
            module_name='cpu',
            whereis_exe=lambda b: b == 'nproc'
        ).instance()

        stub = MockedKernelCPU
        target = 'builtins.open'
        sub_target = 'plyer.platforms.linux.cpu.listdir'

        with patch(target=target, new=stub):
            with patch(target=sub_target, return_value=stub().listdir):
                sb = stub()
                self.assertEqual(
                    cpu.cache, {
                        'L1': sb.cores * 2,
                        'L2': sb.cores,
                        'L3': sb.cores
                    }
                )

    @PlatformTest('win')
    def test_cpu_win_logical(self):
        cpu = platform_import(
            platform='win',
            module_name='cpu'
        )

        cpu = cpu.instance()
        self.assertEqual(
            cpu.logical,
            # https://docs.microsoft.com/en-us/previous-versions/
            # windows/it-pro/windows-xp/bb490954(v=technet.10)
            int(environ['NUMBER_OF_PROCESSORS'])
        )


if __name__ == '__main__':
    unittest.main()
