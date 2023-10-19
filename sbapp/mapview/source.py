# coding=utf-8

__all__ = ["MapSource"]

import hashlib
from math import atan, ceil, cos, exp, log, pi, tan

from kivy.metrics import dp

from mapview.constants import (
    CACHE_DIR,
    MAX_LATITUDE,
    MAX_LONGITUDE,
    MIN_LATITUDE,
    MIN_LONGITUDE,
)
from mapview.downloader import Downloader
from mapview.utils import clamp


class MapSource:
    """Base class for implementing a map source / provider
    """

    attribution_osm = 'Maps & Data © [i][ref=http://www.osm.org/copyright]OpenStreetMap contributors[/ref][/i]'
    attribution_thunderforest = 'Maps © [i][ref=http://www.thunderforest.com]Thunderforest[/ref][/i], Data © [i][ref=http://www.osm.org/copyright]OpenStreetMap contributors[/ref][/i]'

    # list of available providers
    # cache_key: (is_overlay, minzoom, maxzoom, url, attribution)
    providers = {
        "osm": (
            0,
            0,
            19,
            "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            attribution_osm,
        ),
        "osm-hot": (
            0,
            0,
            19,
            "http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
            "",
        ),
        "osm-de": (
            0,
            0,
            18,
            "http://{s}.tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png",
            "Tiles @ OSM DE",
        ),
        "osm-fr": (
            0,
            0,
            20,
            "http://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
            "Tiles @ OSM France",
        ),
        "cyclemap": (
            0,
            0,
            17,
            "http://{s}.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png",
            "Tiles @ Andy Allan",
        ),
        "thunderforest-cycle": (
            0,
            0,
            19,
            "http://{s}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png",
            attribution_thunderforest,
        ),
        "thunderforest-transport": (
            0,
            0,
            19,
            "http://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png",
            attribution_thunderforest,
        ),
        "thunderforest-landscape": (
            0,
            0,
            19,
            "http://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png",
            attribution_thunderforest,
        ),
        "thunderforest-outdoors": (
            0,
            0,
            19,
            "http://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png",
            attribution_thunderforest,
        ),
        # no longer available
        # "mapquest-osm": (0, 0, 19, "http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpeg", "Tiles Courtesy of Mapquest", {"subdomains": "1234", "image_ext": "jpeg"}),
        # "mapquest-aerial": (0, 0, 19, "http://oatile{s}.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.jpeg", "Tiles Courtesy of Mapquest", {"subdomains": "1234", "image_ext": "jpeg"}),
        # more to add with
        # https://github.com/leaflet-extras/leaflet-providers/blob/master/leaflet-providers.js
        # not working ?
        # "openseamap": (0, 0, 19, "http://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
        #    "Map data @ OpenSeaMap contributors"),
    }

    def __init__(
        self,
        url="http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        cache_key=None,
        min_zoom=0,
        max_zoom=19,
        tile_size=256,
        image_ext="png",
        attribution="© OpenStreetMap contributors",
        subdomains="abc",
        **kwargs
    ):
        if cache_key is None:
            # possible cache hit, but very unlikely
            cache_key = hashlib.sha224(url.encode("utf8")).hexdigest()[:10]
        self.url = url
        self.cache_key = cache_key
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.tile_size = tile_size
        self.image_ext = image_ext
        self.attribution = attribution
        self.subdomains = subdomains
        self.cache_fmt = "{cache_key}_{zoom}_{tile_x}_{tile_y}.{image_ext}"
        self.dp_tile_size = min(dp(self.tile_size), self.tile_size * 2)
        self.default_lat = self.default_lon = self.default_zoom = None
        self.bounds = None
        self.cache_dir = kwargs.get('cache_dir', CACHE_DIR)

    @staticmethod
    def from_provider(key, **kwargs):
        provider = MapSource.providers[key]
        cache_dir = kwargs.get('cache_dir', CACHE_DIR)
        options = {}
        is_overlay, min_zoom, max_zoom, url, attribution = provider[:5]
        if len(provider) > 5:
            options = provider[5]
        return MapSource(
            cache_key=key,
            min_zoom=min_zoom,
            max_zoom=max_zoom,
            url=url,
            cache_dir=cache_dir,
            attribution=attribution,
            **options
        )

    def get_x(self, zoom, lon):
        """Get the x position on the map using this map source's projection
        (0, 0) is located at the top left.
        """
        lon = clamp(lon, MIN_LONGITUDE, MAX_LONGITUDE)
        return ((lon + 180.0) / 360.0 * pow(2.0, zoom)) * self.dp_tile_size

    def get_y(self, zoom, lat):
        """Get the y position on the map using this map source's projection
        (0, 0) is located at the top left.
        """
        lat = clamp(-lat, MIN_LATITUDE, MAX_LATITUDE)
        lat = lat * pi / 180.0
        return (
            (1.0 - log(tan(lat) + 1.0 / cos(lat)) / pi) / 2.0 * pow(2.0, zoom)
        ) * self.dp_tile_size

    def get_lon(self, zoom, x):
        """Get the longitude to the x position in the map source's projection
        """
        dx = x / float(self.dp_tile_size)
        lon = dx / pow(2.0, zoom) * 360.0 - 180.0
        return clamp(lon, MIN_LONGITUDE, MAX_LONGITUDE)

    def get_lat(self, zoom, y):
        """Get the latitude to the y position in the map source's projection
        """
        dy = y / float(self.dp_tile_size)
        n = pi - 2 * pi * dy / pow(2.0, zoom)
        lat = -180.0 / pi * atan(0.5 * (exp(n) - exp(-n)))
        return clamp(lat, MIN_LATITUDE, MAX_LATITUDE)

    def get_row_count(self, zoom):
        """Get the number of tiles in a row at this zoom level
        """
        if zoom == 0:
            return 1
        return 2 << (zoom - 1)

    def get_col_count(self, zoom):
        """Get the number of tiles in a col at this zoom level
        """
        if zoom == 0:
            return 1
        return 2 << (zoom - 1)

    def get_min_zoom(self):
        """Return the minimum zoom of this source
        """
        return self.min_zoom

    def get_max_zoom(self):
        """Return the maximum zoom of this source
        """
        return self.max_zoom

    def fill_tile(self, tile):
        """Add this tile to load within the downloader
        """
        if tile.state == "done":
            return
        Downloader.instance(cache_dir=self.cache_dir).download_tile(tile)
