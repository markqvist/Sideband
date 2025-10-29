import re

from collections import namedtuple


class Advertisement(object):
    """Advertisement data record parser

    >>> ad = Advertisement([2, 1, 0x6, 6, 255, 82, 83, 95, 82, 48])
    >>> for data in ad:
    ...     data
    AD(ad_type=1, data=bytearray(b'\\x06'))
    AD(ad_type=255, data=bytearray(b'RS_R0'))
    >>> list(ad)[0].ad_type == Advertisement.ad_types.flags
    True
    """

    AD = namedtuple("AD", ['ad_type', 'data'])

    class ad_types:
        """
        Assigned numbers for some of `advertisement data types
        <https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/>`_.

        flags : "Flags" (0x01)

        complete_local_name : "Complete Local Name" (0x09)

        service_data : "Service Data" (0x16)

        manufacturer_specific_data : "Manufacturer Specific Data" (0xff)
        """
        flags = 0x01
        complete_local_name = 0x09
        service_data = 0x16
        manufacturer_specific_data = 0xff

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return Advertisement.parse(self.data)

    @classmethod
    def parse(cls, data):
        pos = 0
        while pos < len(data):
            length = data[pos]
            if length < 2:
                return
            try:
                ad_type = data[pos + 1]
            except IndexError:
                return
            next_pos = pos + length + 1
            if ad_type:
                segment = slice(pos + 2, next_pos)
                yield Advertisement.AD(ad_type, bytearray(data[segment]))
            pos = next_pos


class Services(dict):
    """Services dict

    >>> services = Services({'service0': {'c1-aa': 0, 'aa-c2-aa': 1},
    ...                      'service1': {'bb-c3-bb': 2}})
    >>> services.search('c3')
    2
    >>> services.search('c4')
    """

    def search(self, pattern, flags=re.IGNORECASE):
        """Search for characteristic by pattern

        :param pattern: regexp pattern
        :param flags: regexp flags, re.IGNORECASE by default
        """
        for characteristics in self.values():
            for uuid, characteristic in characteristics.items():
                if re.search(pattern, uuid, flags):
                    return characteristic
