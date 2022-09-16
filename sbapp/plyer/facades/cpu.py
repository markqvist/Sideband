'''
CPU
===

Simple Example
---------------

To get CPU count::
    >>> from plyer import cpu
    >>> # 1 socket, 1 core per socket, 2 threads per core
    >>> cpu.sockets   # 1 CPU socket (or slot)
    1
    >>> cpu.physical  # 1 CPU socket * 1 core per socket
    1
    >>> cpu.logical   # 1 CPU socket * 1 core per socket * 2 threads per core
    2

Supported Platforms
-------------------

MacOS
Linux
Windows
'''


class CPU:
    '''
    Facade providing info about sockets, physical and logical
    number of processors.
    '''

    @property
    def sockets(self):
        '''
        Property that contains the count of CPU sockets.
        '''
        return self._sockets()

    @property
    def physical(self):
        '''
        Property that contains the total number of physical cores
        (max core count) in the system.

        .. note:: `sockets * cores per socket`
        '''
        return self._physical()

    @property
    def logical(self):
        '''
        Property that contains the total number of logical cores
        (max thread count) in the system.

        .. note:: `sockets * cores per socket * threads per core`
        '''
        return self._logical()

    @property
    def cache(self):
        '''
        Property that contains the count of L1, L2, L3 caches in the system
        as a dictionary `{'L1': int, 'L2': int, 'L3': int}`.
        '''
        return self._cache()

    @property
    def numa(self):
        '''
        Property that contains the count of NUMA nodes in the system.

        .. note:: https://en.wikipedia.org/wiki/Non-uniform_memory_access
        '''
        return self._numa()

    # private

    def _sockets(self):
        raise NotImplementedError()

    def _physical(self):
        raise NotImplementedError()

    def _logical(self):
        raise NotImplementedError()

    def _cache(self):
        raise NotImplementedError()

    def _numa(self):
        raise NotImplementedError()
