'''
Module of macOS API for plyer.maps.
'''

from subprocess import Popen, PIPE
from sbapp.plyer.facades import Maps
from urllib.parse import quote_plus


class MacOSMaps(Maps):
    '''
    Implementation of MacOS Maps API.
    '''

    def _open_by_address(self, address, **kwargs):
        '''
        :param address: An address string that geolocation can understand.
        '''

        address = quote_plus(address, safe=',')
        maps_address = 'http://maps.apple.com/?address=' + address

        process = Popen(
            ['open', '-a', 'Maps', maps_address],
            stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

    def _open_by_lat_long(self, latitude, longitude, **kwargs):
        '''
        Open a coordinate span denoting a latitudinal delta and a
        longitudinal delta (similar to MKCoordinateSpan)

        :param name: (optional), will set the name of the dropped pin
        '''

        name = kwargs.get("name", "Selected Location")
        maps_address = 'http://maps.apple.com/?ll={},{}&q={}'.format(
            latitude, longitude, name)

        process = Popen(
            ['open', '-a', 'Maps', maps_address],
            stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

    def _search(self, query, **kwargs):
        '''
        :param query: A string that describes the search object (ex. "Pizza")

        :param latitude: (optional), narrow down query within area,
        MUST BE USED WITH LONGITUDE

        :param longitude: (optional), narrow down query within area,
        MUST BE USED WITH LATITUDE
        '''

        latitude = kwargs.get('latitude')
        longitude = kwargs.get('longitude')

        query = quote_plus(query, safe=',')
        maps_address = 'http://maps.apple.com/?q=' + query

        if latitude is not None and longitude is not None:
            maps_address += '&sll={},{}'.format(latitude, longitude)

        process = Popen(
            ['open', '-a', 'Maps', maps_address],
            stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

    def _route(self, saddr, daddr, **kwargs):
        '''
        :param saddr: can be given as 'address' or 'lat,long'
        :param daddr: can be given as 'address' or 'lat,long'
        '''
        saddr = quote_plus(saddr, safe=',')
        daddr = quote_plus(daddr, safe=',')

        maps_address = 'http://maps.apple.com/?saddr={}&daddr={}'.format(
                                                            saddr, daddr)
        process = Popen(
            ['open', '-a', 'Maps', maps_address],
            stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()


def instance():
    '''
    Instance for facade proxy.
    '''
    return MacOSMaps()
