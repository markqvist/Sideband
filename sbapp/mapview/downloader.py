# coding=utf-8

__all__ = ["Downloader"]

import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from os import environ, makedirs
from os.path import exists, join
from random import choice
from time import time

import requests
from kivy.clock import Clock
from kivy.logger import LOG_LEVELS, Logger

from mapview.constants import CACHE_DIR

import logging
# if "MAPVIEW_DEBUG_DOWNLOADER" in environ:
#     Logger.setLevel(LOG_LEVELS['debug'])
#     Logger.setLevel(LOG_LEVELS['error'])

# user agent is needed because since may 2019 OSM gives me a 429 or 403 server error
# I tried it with a simpler one (just Mozilla/5.0) this also gets rejected
USER_AGENT = 'Kivy-garden.mapview'

import RNS

class Downloader:
    _instance = None
    MAX_WORKERS = 5
    CAP_TIME = 0.064  # 15 FPS

    @staticmethod
    def instance(cache_dir=None):
        if Downloader._instance is None:
            if not cache_dir:
                cache_dir = CACHE_DIR
            Downloader._instance = Downloader(cache_dir=cache_dir)
        return Downloader._instance

    def __init__(self, max_workers=None, cap_time=None, **kwargs):
        self.cache_dir = kwargs.get('cache_dir', CACHE_DIR)
        if max_workers is None:
            max_workers = Downloader.MAX_WORKERS
        if cap_time is None:
            cap_time = Downloader.CAP_TIME
        self.is_paused = False
        self.cap_time = cap_time
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._futures = []
        Clock.schedule_interval(self._check_executor, 1 / 60.0)
        if not exists(self.cache_dir):
            RNS.log("Creating cache dir "+str(self.cache_dir), RNS.LOG_WARNING)
            makedirs(self.cache_dir)

        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("urllib3.response").setLevel(logging.WARNING)
        logging.getLogger("urllib3.connection").setLevel(logging.WARNING)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        
        logging.getLogger("urllib3").propagate = True
        logging.getLogger("requests").propagate = True
        logging.getLogger("urllib3.response").propagate = True
        logging.getLogger("urllib3.connection").propagate = True
        logging.getLogger("urllib3.connectionpool").propagate = True

    def submit(self, f, *args, **kwargs):
        future = self.executor.submit(f, *args, **kwargs)
        self._futures.append(future)

    def download_tile(self, tile):
        # Logger.debug(
        #     "Downloader: queue(tile) zoom={} x={} y={}".format(
        #         tile.zoom, tile.tile_x, tile.tile_y
        #     )
        # )
        future = self.executor.submit(self._load_tile, tile)
        self._futures.append(future)

    def download(self, url, callback, **kwargs):
        # Logger.debug("Downloader: queue(url) {}".format(url))
        future = self.executor.submit(self._download_url, url, callback, kwargs)
        self._futures.append(future)

    def _download_url(self, url, callback, kwargs):
        # Logger.debug("Downloader: download(url) {}".format(url))
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        return callback, (url, response)

    def __to_quad(self, x, y, z):
        quad_key = []
        i = z
        while i > 0:
            digit = 0
            mask = 1 << (i-1)
            if (x & mask) != 0:
                digit += 1
            if (y & mask) != 0:
                digit += 2
            quad_key.append(str(digit))

            i -= 1
        return "".join(quad_key)

    def _load_tile(self, tile):
        if tile.state == "done":
            return
        cache_fn = tile.cache_fn
        if exists(cache_fn):
            # Logger.debug("Downloader: use cache {}".format(cache_fn))
            return tile.set_source, (cache_fn,)
        tile_y = tile.map_source.get_row_count(tile.zoom) - tile.tile_y - 1

        if tile.map_source.quad_key:
            uri = tile.map_source.url.format(
                q=self.__to_quad(tile.tile_x,tile_y,tile.zoom), s=choice(tile.map_source.subdomains)
            )
        else:
            uri = tile.map_source.url.format(
                z=tile.zoom, x=tile.tile_x, y=tile_y, s=choice(tile.map_source.subdomains)
            )

        # Logger.debug("Downloader: download(tile) {}".format(uri))
        response = requests.get(uri, headers={'User-agent': USER_AGENT}, timeout=5)
        try:
            response.raise_for_status()
            data = response.content
            with open(cache_fn, "wb") as fd:
                fd.write(data)
            # Logger.debug("Downloaded {} bytes: {}".format(len(data), uri))
            return tile.set_source, (cache_fn,)
        except Exception as e:
            print("Downloader error: {!r}".format(e))

    def _check_executor(self, dt):
        start = time()
        try:
            for future in as_completed(self._futures[:], 0):
                self._futures.remove(future)
                try:
                    result = future.result()
                except Exception:
                    traceback.print_exc()
                    # make an error tile?
                    continue
                if result is None:
                    continue
                callback, args = result
                callback(*args)

                # capped executor in time, in order to prevent too much
                # slowiness.
                # seems to works quite great with big zoom-in/out
                if time() - start > self.cap_time:
                    break
        except TimeoutError:
            pass
