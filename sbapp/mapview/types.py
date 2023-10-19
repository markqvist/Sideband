# coding=utf-8

__all__ = ["Coordinate", "Bbox"]

from collections import namedtuple

Coordinate = namedtuple("Coordinate", ["lat", "lon"])


class Bbox(tuple):
    def collide(self, *args):
        if isinstance(args[0], Coordinate):
            coord = args[0]
            lat = coord.lat
            lon = coord.lon
        else:
            lat, lon = args
        lat1, lon1, lat2, lon2 = self[:]

        if lat1 < lat2:
            in_lat = lat1 <= lat <= lat2
        else:
            in_lat = lat2 <= lat <= lat2
        if lon1 < lon2:
            in_lon = lon1 <= lon <= lon2
        else:
            in_lon = lon2 <= lon <= lon2

        return in_lat and in_lon
