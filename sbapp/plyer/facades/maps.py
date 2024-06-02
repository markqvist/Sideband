'''
Maps
=======
The :class:`Maps` creates a client for accessing the default Maps API.

Holds features such as opening a location by
address & latitude/longitude, create queries, or find directions between
two points

Simple Examples
---------------

Perform a search::

    >>> from plyer import maps
    >>> maps.search('Mexican Restaurant')
    >>> maps.search('Taco Bell', latitude=38.5810606, longitude=-121.493895)

Get directions to a location::

    >>> from plyer import maps
    >>> maps.route('Cupertino', 'San Francisco')
    >>> maps.route('41.9156316,-72.6130726', '42.65228271484,-73.7577362060')

View a specific location::

    >>> from plyer import maps
    >>> maps.open_by_address('25 Leshin Lane, Hightstown, NJ')
    >>> maps.open_by_lat_long(30.451468, -91.187149)
    >>> maps.open_by_lat_long(30.451468, -91.187149, name='Home')

Supported Platforms
-------------------
macOS, iOS
---------------
'''


class Maps:
    '''
    Maps facade.
    '''

    def open_by_address(self, address, **kwargs):
        '''
        Open the specificed location by address in the default Maps API
        '''
        self._open_by_address(address, **kwargs)

    def open_by_lat_long(self, latitude, longitude, **kwargs):
        '''
        Open the specificed location by latitude & longitude coordinates
        in the default Maps API
        '''
        self._open_by_lat_long(latitude, longitude, **kwargs)

    def search(self, query, **kwargs):
        '''
        The query. This parameter is treated as if its value had been typed
        into the Maps search field by the user.

        Note that query=* is not supported
        '''
        self._search(query, **kwargs)

    def route(self, saddr, daddr, **kwargs):
        '''
        To provide navigation directions from one location to another.

        :param saddr: The source address to be used as the starting
        point for directions.

        :param daddr: The destination address to be used as the
        destination point for directions.
        '''
        self._route(saddr, daddr, **kwargs)

    def _open_by_address(self, address, **kwargs):
        raise NotImplementedError()

    def _open_by_lat_long(self, latitude, longitude, **kwargs):
        raise NotImplementedError()

    def _search(self, query, **kwargs):
        raise NotImplementedError()

    def _route(self, saddr, daddr, **kwargs):
        raise NotImplementedError()
