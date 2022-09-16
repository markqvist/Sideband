'''
Number of Processors
=======
The :class:`Processors` provides a information on the number of
processors in a system
.. note::
    Deprecated in favor of `cpu`

Simple Example
---------------
To get processors status::
    >>> from plyer import processors
    >>> processors.status
    {'Number_of_Processors': '4'}
Supported Platforms
-------------------
Linux
'''


class Processors:
    '''
    Number of Processors info facade.
    '''

    @property
    def status(self):
        '''
        Property that contains a dict with the following fields:
             * **Number_of_Processors** *(int)*: Number of Processors in
             the system
            .. warning::
                If any of the fields is not readable, it is set as
                None.
        '''
        return self.get_state()

    def get_state(self):
        return self._get_state()

    def _get_state(self):
        raise NotImplementedError()
