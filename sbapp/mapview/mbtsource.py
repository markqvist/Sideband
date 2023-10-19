# coding=utf-8
"""
MBTiles provider for MapView
============================

This provider is based on .mbfiles from MapBox.
See: http://mbtiles.org/
"""

__all__ = ["MBTilesMapSource"]


import io
import sqlite3
import threading

from kivy.core.image import Image as CoreImage
from kivy.core.image import ImageLoader

from mapview.downloader import Downloader
from mapview.source import MapSource


class MBTilesMapSource(MapSource):
    def __init__(self, filename, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.db = sqlite3.connect(filename)

        # read metadata
        c = self.db.cursor()
        metadata = dict(c.execute("SELECT * FROM metadata"))
        if metadata["format"] == "pbf":
            raise ValueError("Only raster maps are supported, not vector maps.")
        self.min_zoom = int(metadata["minzoom"])
        self.max_zoom = int(metadata["maxzoom"])
        self.attribution = metadata.get("attribution", "")
        self.bounds = bounds = None
        cx = cy = 0.0
        cz = 5
        if "bounds" in metadata:
            self.bounds = bounds = tuple(map(float, metadata["bounds"].split(",")))
        if "center" in metadata:
            cx, cy, cz = tuple(map(float, metadata["center"].split(",")))
        elif self.bounds:
            cx = (bounds[2] + bounds[0]) / 2.0
            cy = (bounds[3] + bounds[1]) / 2.0
            cz = self.min_zoom
        self.default_lon = cx
        self.default_lat = cy
        self.default_zoom = int(cz)
        self.projection = metadata.get("projection", "")
        self.is_xy = self.projection == "xy"

    def fill_tile(self, tile):
        if tile.state == "done":
            return
        Downloader.instance(self.cache_dir).submit(self._load_tile, tile)

    def _load_tile(self, tile):
        # global db context cannot be shared across threads.
        ctx = threading.local()
        if not hasattr(ctx, "db"):
            ctx.db = sqlite3.connect(self.filename)

        # get the right tile
        c = ctx.db.cursor()
        c.execute(
            (
                "SELECT tile_data FROM tiles WHERE "
                "zoom_level=? AND tile_column=? AND tile_row=?"
            ),
            (tile.zoom, tile.tile_x, tile.tile_y),
        )
        row = c.fetchone()
        if not row:
            tile.state = "done"
            return

        # no-file loading
        try:
            data = io.BytesIO(row[0])
        except Exception:
            # android issue, "buffer" does not have the buffer interface
            # ie row[0] buffer is not compatible with BytesIO on Android??
            data = io.BytesIO(bytes(row[0]))
        im = CoreImage(
            data,
            ext='png',
            filename="{}.{}.{}.png".format(tile.zoom, tile.tile_x, tile.tile_y),
        )

        if im is None:
            tile.state = "done"
            return

        return self._load_tile_done, (tile, im,)

    def _load_tile_done(self, tile, im):
        tile.texture = im.texture
        tile.state = "need-animation"

    def get_x(self, zoom, lon):
        if self.is_xy:
            return lon
        return super().get_x(zoom, lon)

    def get_y(self, zoom, lat):
        if self.is_xy:
            return lat
        return super().get_y(zoom, lat)

    def get_lon(self, zoom, x):
        if self.is_xy:
            return x
        return super().get_lon(zoom, x)

    def get_lat(self, zoom, y):
        if self.is_xy:
            return y
        return super().get_lat(zoom, y)
