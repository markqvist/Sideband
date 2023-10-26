# coding=utf-8

__all__ = ["MapView", "MapMarker", "MapMarkerPopup", "MapLayer", "MarkerMapLayer"]

import webbrowser
from itertools import takewhile
from math import ceil
from os.path import dirname, join

from kivy.clock import Clock
from kivy.compat import string_types
from kivy.graphics import Canvas, Color, Rectangle
from kivy.graphics.transformation import Matrix
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget

from mapview import Bbox, Coordinate
from mapview.constants import (
    CACHE_DIR,
    MAX_LATITUDE,
    MAX_LONGITUDE,
    MIN_LATITUDE,
    MIN_LONGITUDE,
)
from mapview.source import MapSource
from mapview.utils import clamp

Builder.load_string(
    """
<MapMarker>:
    size_hint: None, None
    source: root.source
    size: list(map(dp, self.texture_size))
    allow_stretch: True

<CustomMapMarker>:
    size_hint: None, None
    source: root.source
    size: list(map(dp, self.texture_size))
    allow_stretch: True
    on_release: root.app.map_display_telemetry()

<MapView>:
    canvas.before:
        StencilPush
        Rectangle:
            pos: self.pos
            size: self.size
        StencilUse
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size
    canvas.after:
        StencilUnUse
        Rectangle:
            pos: self.pos
            size: self.size
        StencilPop

    ClickableLabel:
        text: root.map_source.attribution if hasattr(root.map_source, "attribution") else ""
        size_hint: None, None
        size: self.texture_size[0] + sp(8), self.texture_size[1] + sp(4)
        font_size: "10sp"
        right: [root.right, self.center][0]
        color: 0, 0, 0, 1
        markup: True
        canvas.before:
            Color:
                rgba: .8, .8, .8, .8
            Rectangle:
                pos: self.pos
                size: self.size


<MapViewScatter>:
    auto_bring_to_front: False
    do_rotation: False
    scale_min: 0.2
    scale_max: 3.

<MapMarkerPopup>:
    RelativeLayout:
        id: placeholder
        y: root.top
        center_x: root.center_x
        size: root.popup_size

"""
)


class ClickableLabel(Label):
    def on_ref_press(self, *args):
        webbrowser.open(str(args[0]), new=2)


class Tile(Rectangle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_dir = kwargs.get('cache_dir', CACHE_DIR)

    @property
    def cache_fn(self):
        map_source = self.map_source
        fn = map_source.cache_fmt.format(
            image_ext=map_source.image_ext,
            cache_key=map_source.cache_key,
            **self.__dict__
        )
        return join(self.map_source.cache_dir, fn)

    def set_source(self, cache_fn):
        try:
            self.source = cache_fn
            self.state = "need-animation"
        except:
            pass

class CustomMapMarker(ButtonBehavior, Image):
    """A marker on a map, that must be used on a :class:`MapMarker`
    """

    anchor_x = NumericProperty(0.5)
    """Anchor of the marker on the X axis. Defaults to 0.5, mean the anchor will
    be at the X center of the image.
    """

    anchor_y = NumericProperty(0)
    """Anchor of the marker on the Y axis. Defaults to 0, mean the anchor will
    be at the Y bottom of the image.
    """

    lat = NumericProperty(0)
    """Latitude of the marker
    """

    lon = NumericProperty(0)
    """Longitude of the marker
    """

    source = StringProperty(join(dirname(__file__), "icons", "marker.png"))
    """Source of the marker, defaults to our own marker.png
    """

    icon_bg = ListProperty()

    # (internal) reference to its layer
    _layer = None

    def __init__(self, **kwargs):
        if "icon_bg" in kwargs:
            bg = kwargs["icon_bg"]
            if len(bg) >= 3:
                lim = 0.5
                lum = (bg[0]+bg[1]+bg[2])/3
                if lum >= lim:
                    self.source = join(dirname(__file__), "icons", "marker_dark.png")
                else:
                    self.source = join(dirname(__file__), "icons", "marker_dark.png")

        super(CustomMapMarker, self).__init__(**kwargs)
        self.texture_update()

    def detach(self):
        if self._layer:
            self._layer.remove_widget(self)
            self._layer = None

class MapMarker(ButtonBehavior, Image):
    """A marker on a map, that must be used on a :class:`MapMarker`
    """

    anchor_x = NumericProperty(0.5)
    """Anchor of the marker on the X axis. Defaults to 0.5, mean the anchor will
    be at the X center of the image.
    """

    anchor_y = NumericProperty(0)
    """Anchor of the marker on the Y axis. Defaults to 0, mean the anchor will
    be at the Y bottom of the image.
    """

    lat = NumericProperty(0)
    """Latitude of the marker
    """

    lon = NumericProperty(0)
    """Longitude of the marker
    """

    source = StringProperty(join(dirname(__file__), "icons", "marker.png"))
    """Source of the marker, defaults to our own marker.png
    """

    # (internal) reference to its layer
    _layer = None

    def __init__(self, **kwargs):
        super(MapMarker, self).__init__(**kwargs)
        self.texture_update()

    def detach(self):
        if self._layer:
            self._layer.remove_widget(self)
            self._layer = None


class MapMarkerPopup(MapMarker):
    is_open = BooleanProperty(False)
    placeholder = ObjectProperty(None)
    popup_size = ListProperty([100, 100])

    def add_widget(self, widget):
        if not self.placeholder:
            self.placeholder = widget
            if self.is_open:
                super().add_widget(self.placeholder)
        else:
            self.placeholder.add_widget(widget)

    def remove_widget(self, widget):
        if widget is not self.placeholder:
            self.placeholder.remove_widget(widget)
        else:
            super().remove_widget(widget)

    def on_is_open(self, *args):
        self.refresh_open_status()

    def on_release(self, *args):
        self.is_open = not self.is_open

    def refresh_open_status(self):
        if not self.is_open and self.placeholder.parent:
            super().remove_widget(self.placeholder)
        elif self.is_open and not self.placeholder.parent:
            super().add_widget(self.placeholder)


class MapLayer(Widget):
    """A map layer, that is repositionned everytime the :class:`MapView` is
    moved.
    """

    viewport_x = NumericProperty(0)
    viewport_y = NumericProperty(0)

    def reposition(self):
        """Function called when :class:`MapView` is moved. You must recalculate
        the position of your children.
        """
        pass

    def unload(self):
        """Called when the view want to completly unload the layer.
        """
        pass


class MarkerMapLayer(MapLayer):
    """A map layer for :class:`MapMarker`
    """

    order_marker_by_latitude = BooleanProperty(True)

    def __init__(self, **kwargs):
        self.markers = []
        super().__init__(**kwargs)

    def insert_marker(self, marker, **kwargs):
        if self.order_marker_by_latitude:
            before = list(
                takewhile(lambda i_m: i_m[1].lat < marker.lat, enumerate(self.children))
            )
            if before:
                kwargs['index'] = before[-1][0] + 1

        super().add_widget(marker, **kwargs)

    def add_widget(self, marker):
        marker._layer = self
        self.markers.append(marker)
        self.insert_marker(marker)

    def remove_widget(self, marker):
        marker._layer = None
        if marker in self.markers:
            self.markers.remove(marker)
        super().remove_widget(marker)

    def reposition(self):
        if not self.markers:
            return
        mapview = self.parent
        set_marker_position = self.set_marker_position
        bbox = None
        # reposition the markers depending the latitude
        markers = sorted(self.markers, key=lambda x: -x.lat)
        margin = max((max(marker.size) for marker in markers))
        bbox = mapview.get_bbox(margin)
        for marker in markers:
            if bbox.collide(marker.lat, marker.lon):
                set_marker_position(mapview, marker)
                if not marker.parent:
                    self.insert_marker(marker)
            else:
                super().remove_widget(marker)

    def set_marker_position(self, mapview, marker):
        x, y = mapview.get_window_xy_from(marker.lat, marker.lon, mapview.zoom)
        marker.x = int(x - marker.width * marker.anchor_x)
        marker.y = int(y - marker.height * marker.anchor_y)
        if hasattr(marker, "children"):
            if marker.children != None and len(marker.children) > 0:
                for c in marker.children:
                    c.x = marker.x
                    c.y = marker.y+dp(16)

    def unload(self):
        self.clear_widgets()
        del self.markers[:]


class MapViewScatter(Scatter):
    # internal
    def on_transform(self, *args):
        super().on_transform(*args)
        self.parent.on_transform(self.transform)

    def collide_point(self, x, y):
        return True


class MapView(Widget):
    """MapView is the widget that control the map displaying, navigation, and
    layers management.
    """

    lon = NumericProperty()
    """Longitude at the center of the widget
    """

    lat = NumericProperty()
    """Latitude at the center of the widget
    """

    zoom = NumericProperty(0)
    """Zoom of the widget. Must be between :meth:`MapSource.get_min_zoom` and
    :meth:`MapSource.get_max_zoom`. Default to 0.
    """

    map_source = ObjectProperty(MapSource())
    """Provider of the map, default to a empty :class:`MapSource`.
    """

    double_tap_zoom = BooleanProperty(False)
    """If True, this will activate the double-tap to zoom.
    """

    pause_on_action = BooleanProperty(True)
    """Pause any map loading / tiles loading when an action is done.
    This allow better performance on mobile, but can be safely deactivated on
    desktop.
    """

    snap_to_zoom = BooleanProperty(True)
    """When the user initiate a zoom, it will snap to the closest zoom for
    better graphics. The map can be blur if the map is scaled between 2 zoom.
    Default to True, even if it doesn't fully working yet.
    """

    animation_duration = NumericProperty(100)
    """Duration to animate Tiles alpha from 0 to 1 when it's ready to show.
    Default to 100 as 100ms. Use 0 to deactivate.
    """

    delta_x = NumericProperty(0)
    delta_y = NumericProperty(0)
    background_color = ListProperty([181 / 255.0, 208 / 255.0, 208 / 255.0, 1])
    cache_dir = StringProperty(CACHE_DIR)
    _zoom = NumericProperty(0)
    _pause = BooleanProperty(False)
    _scale = 1.0
    _allow_snap = False
    _disabled_count = 0
    high_res = True
    high_res_mode = 1

    __events__ = ["on_map_relocated"]

    # Public API

    @property
    def viewport_pos(self):
        vx, vy = self._scatter.to_local(self.x, self.y)
        return vx - self.delta_x, vy - self.delta_y

    @property
    def scale(self):
        if self._invalid_scale:
            self._invalid_scale = False
            self._scale = round(self._scatter.scale, 2)
        return self._scale

    def get_bbox(self, margin=0):
        """Returns the bounding box from the bottom/left (lat1, lon1) to
        top/right (lat2, lon2).
        """
        x1, y1 = self.to_local(0 - margin, 0 - margin)
        x2, y2 = self.to_local((self.width + margin), (self.height + margin))
        c1 = self.get_latlon_at(x1, y1)
        c2 = self.get_latlon_at(x2, y2)
        return Bbox((c1.lat, c1.lon, c2.lat, c2.lon))

    bbox = AliasProperty(get_bbox, None, bind=["lat", "lon", "_zoom"])

    def unload(self):
        """Unload the view and all the layers.
        It also cancel all the remaining downloads.
        """
        self.remove_all_tiles()

    def get_window_xy_from(self, lat, lon, zoom):
        """Returns the x/y position in the widget absolute coordinates
        from a lat/lon"""
        scale = self.scale
        vx, vy = self.viewport_pos
        ms = self.map_source
        x = ms.get_x(zoom, lon) - vx
        y = ms.get_y(zoom, lat) - vy
        x *= scale
        y *= scale
        x = x + self.pos[0]
        y = y + self.pos[1]
        return x, y

    def center_on(self, *args):
        """Center the map on the coordinate :class:`Coordinate`, or a (lat, lon)
        """
        map_source = self.map_source
        zoom = self._zoom

        if len(args) == 1 and isinstance(args[0], Coordinate):
            coord = args[0]
            lat = coord.lat
            lon = coord.lon
        elif len(args) == 2:
            lat, lon = args
        else:
            raise Exception("Invalid argument for center_on")
        lon = clamp(lon, MIN_LONGITUDE, MAX_LONGITUDE)
        lat = clamp(lat, MIN_LATITUDE, MAX_LATITUDE)
        scale = self._scatter.scale
        x = map_source.get_x(zoom, lon) - self.center_x / scale
        y = map_source.get_y(zoom, lat) - self.center_y / scale
        self.delta_x = -x
        self.delta_y = -y
        self.lon = lon
        self.lat = lat
        self._scatter.pos = 0, 0
        self.trigger_update(True)

    def set_zoom_at(self, zoom, x, y, scale=None):
        """Sets the zoom level, leaving the (x, y) at the exact same point
        in the view.
        """
        zoom = clamp(
            zoom, self.map_source.get_min_zoom(), self.map_source.get_max_zoom()
        )
        if int(zoom) == int(self._zoom):
            if scale is None:
                return
            elif scale == self.scale:
                return
        scale = scale or 1.0

        # first, rescale the scatter
        scatter = self._scatter
        scale = clamp(scale, scatter.scale_min, scatter.scale_max)
        rescale = scale * 1.0 / scatter.scale
        scatter.apply_transform(
            Matrix().scale(rescale, rescale, rescale),
            post_multiply=True,
            anchor=scatter.to_local(x, y),
        )

        # adjust position if the zoom changed
        c1 = self.map_source.get_col_count(self._zoom)
        c2 = self.map_source.get_col_count(zoom)
        if c1 != c2:
            f = float(c2) / float(c1)
            self.delta_x = scatter.x + self.delta_x * f
            self.delta_y = scatter.y + self.delta_y * f
            # back to 0 every time
            scatter.apply_transform(
                Matrix().translate(-scatter.x, -scatter.y, 0), post_multiply=True
            )

        # avoid triggering zoom changes.
        self._zoom = zoom
        self.zoom = self._zoom

    def on_zoom(self, instance, zoom):
        if zoom == self._zoom:
            return
        x = self.map_source.get_x(zoom, self.lon) - self.delta_x
        y = self.map_source.get_y(zoom, self.lat) - self.delta_y
        self.set_zoom_at(zoom, x, y)
        self.center_on(self.lat, self.lon)

    def get_latlon_at(self, x, y, zoom=None):
        """Return the current :class:`Coordinate` within the (x, y) widget
        coordinate.
        """
        if zoom is None:
            zoom = self._zoom
        vx, vy = self.viewport_pos
        scale = self._scale
        return Coordinate(
            lat=self.map_source.get_lat(zoom, y / scale + vy),
            lon=self.map_source.get_lon(zoom, x / scale + vx),
        )

    def add_marker(self, marker, layer=None):
        """Add a marker into the layer. If layer is None, it will be added in
        the default marker layer. If there is no default marker layer, a new
        one will be automatically created
        """
        if layer is None:
            if not self._default_marker_layer:
                layer = MarkerMapLayer()
                self.add_layer(layer)
            else:
                layer = self._default_marker_layer
        layer.add_widget(marker)
        layer.set_marker_position(self, marker)

    def remove_marker(self, marker):
        """Remove a marker from its layer
        """
        marker.detach()

    def add_layer(self, layer, mode="window"):
        """Add a new layer to update at the same time the base tile layer.
        mode can be either "scatter" or "window". If "scatter", it means the
        layer will be within the scatter transformation. It's perfect if you
        want to display path / shape, but not for text.
        If "window", it will have no transformation. You need to position the
        widget yourself: think as Z-sprite / billboard.
        Defaults to "window".
        """
        assert mode in ("scatter", "window")
        if self._default_marker_layer is None and isinstance(layer, MarkerMapLayer):
            self._default_marker_layer = layer
        self._layers.append(layer)
        c = self.canvas
        if mode == "scatter":
            self.canvas = self.canvas_layers
        else:
            self.canvas = self.canvas_layers_out
        layer.canvas_parent = self.canvas
        super().add_widget(layer)
        self.canvas = c

    def remove_layer(self, layer):
        """Remove the layer
        """
        c = self.canvas
        self._layers.remove(layer)
        self.canvas = layer.canvas_parent
        super().remove_widget(layer)
        self.canvas = c

    def sync_to(self, other):
        """Reflect the lat/lon/zoom of the other MapView to the current one.
        """
        if self._zoom != other._zoom:
            self.set_zoom_at(other._zoom, *self.center)
        self.center_on(other.get_latlon_at(*self.center))

    # Private API

    def __init__(self, **kwargs):
        from kivy.base import EventLoop

        EventLoop.ensure_window()
        self._invalid_scale = True
        self._tiles = []
        self._tiles_bg = []
        self._tilemap = {}
        self._layers = []
        self._default_marker_layer = None
        self._need_redraw_all = False
        self._transform_lock = False
        self.trigger_update(True)
        self.canvas = Canvas()
        self._scatter = MapViewScatter()
        self.add_widget(self._scatter)
        with self._scatter.canvas:
            self.canvas_map = Canvas()
            self.canvas_layers = Canvas()
        with self.canvas:
            self.canvas_layers_out = Canvas()
        self._scale_target_anim = False
        self._scale_target = 1.0
        self._touch_count = 0
        self.map_source.cache_dir = self.cache_dir
        Clock.schedule_interval(self._animate_color, 1 / 60.0)
        self.lat = kwargs.get("lat", self.lat)
        self.lon = kwargs.get("lon", self.lon)
        super().__init__(**kwargs)

    def _animate_color(self, dt):
        # fast path
        d = self.animation_duration
        if d == 0:
            for tile in self._tiles:
                if tile.state == "need-animation":
                    tile.g_color.a = 1.0
                    tile.state = "animated"
            for tile in self._tiles_bg:
                if tile.state == "need-animation":
                    tile.g_color.a = 1.0
                    tile.state = "animated"
        else:
            d = d / 1000.0
            for tile in self._tiles:
                if tile.state != "need-animation":
                    continue
                tile.g_color.a += dt / d
                if tile.g_color.a >= 1:
                    tile.state = "animated"
            for tile in self._tiles_bg:
                if tile.state != "need-animation":
                    continue
                tile.g_color.a += dt / d
                if tile.g_color.a >= 1:
                    tile.state = "animated"

    def add_widget(self, widget):
        if isinstance(widget, MapMarker):
            self.add_marker(widget)
        elif isinstance(widget, MapLayer):
            self.add_layer(widget)
        else:
            super().add_widget(widget)

    def remove_widget(self, widget):
        if isinstance(widget, MapMarker):
            self.remove_marker(widget)
        elif isinstance(widget, MapLayer):
            self.remove_layer(widget)
        else:
            super().remove_widget(widget)

    def on_map_relocated(self, zoom, coord):
        pass

    def animated_diff_scale_at(self, d, x, y):
        self._scale_target_pos = x, y
        if self._scale_target_anim is False:
            self._scale_target_anim = True
            self._scale_target = d
        else:
            self._scale_target += d

        # print(f"Scale = {self._scale}   Target begin = {self._scale_target}")
        Clock.unschedule(self._animate_scale)
        Clock.schedule_interval(self._animate_scale, 1 / 60.0)

    def _animate_scale(self, dt):
        diff = self._scale_target / 3.0
        if abs(diff) < 0.01:
            diff = self._scale_target
            self._scale_target = 0
        else:
            self._scale_target -= diff

        final = self._scale_target == 0
        self.diff_scale_at(diff, *self._scale_target_pos, final = final)
        # print(f"Scale = {self._scale}   Target now = {self._scale_target}   Diff = {diff}")
        ret = self._scale_target != 0
        if not ret:
            self._pause = False
        return ret

    def diff_scale_at(self, d, x, y, final = False):
        scatter = self._scatter
        scale = scatter.scale * (2 ** d)
        self.scale_at(scale, x, y, final = final)

    def scale_at(self, scale, x, y, final = False):
        snap_digits = 1
        scatter = self._scatter
        scale = clamp(scale, scatter.scale_min, scatter.scale_max)
        rescale = scale * 1.0 / scatter.scale
        scatter.apply_transform(
            Matrix().scale(rescale, rescale, rescale),
            post_multiply=True,
            anchor=scatter.to_local(x, y),
        )
        # Create a final transform to always land on well-
        # defined scaling factors
        if final and self._allow_snap:
            int_diff = abs(self._scale-1.0)
            diff = self._scale-1.0
            if int_diff < 0.08:
                target = scatter.scale-diff
                factor = target/scatter.scale
                
                scatter.apply_transform(
                    Matrix().scale(factor, factor, factor),
                    post_multiply=True,
                    anchor=scatter.to_local(x, y),
                )
                # print(f"Snapped scale. Self = {self._scale}   Scale = {scale}")
        else:
            pass
            # print(f"Self = {self._scale}   Scale = {scale}   Rescale = {rescale}   Zoom = {self.zoom}")

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        if self.pause_on_action:
            self._pause = True
        # if "button" in touch.profile:
        #     print(f"Scale = {self._scale}   Scatter = {self._scatter.scale}")

        if "button" in touch.profile and touch.button in ("scrolldown", "scrollup"):
            self._allow_snap = False
            if self.snap_to_zoom:
                d = 1 if touch.button == "scrolldown" else -1
            else:
                d = 0.1 if touch.button == "scrolldown" else -0.1
            
            self.animated_diff_scale_at(d, *touch.pos)
            return True
        elif touch.is_double_tap and self.double_tap_zoom:
            self._allow_snap = True
            if self._scale < 1.0:
                dz = (1/self._scale)-1
            else:
                next_scale = 2.0
                dz = (next_scale/self._scale)-1.0

            # print(f"Diff zoom {self._scale} factor = {dz}")
            self.animated_diff_scale_at(dz, *touch.pos)
            return True
        touch.grab(self)
        self._touch_count += 1
        if self._touch_count == 1:
            self._touch_zoom = (self.zoom, self._scale)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            touch.ungrab(self)
            self._touch_count -= 1
            if self._touch_count == 0:
                # animate to the closest zoom
                # zoom, scale = self._touch_zoom
                # cur_zoom = self.zoom
                # cur_scale = self._scale
                # if cur_zoom < zoom or round(cur_scale, 2) < scale:
                #     self.animated_diff_scale_at(1.0 - cur_scale, *touch.pos)
                # elif cur_zoom > zoom or round(cur_scale, 2) > scale:
                #     self.animated_diff_scale_at(2.0 - cur_scale, *touch.pos)
                self._pause = False
            return True
        return super(MapView, self).on_touch_up(touch)

    def on_transform(self, *args):
        self._invalid_scale = True
        if self._transform_lock:
            return
        self._transform_lock = True
        # recalculate viewport
        map_source = self.map_source
        zoom = self._zoom
        scatter = self._scatter
        scale = scatter.scale
        
        if self.high_res:
            if self.high_res_mode == 2:
                # Double resolution mode
                if round(scale, 2) >= 1.0:
                    zoom += 1
                    scale /= 2.0
                elif round(scale, 2) < 0.5:
                    zoom -= 1
                    scale *= 2.0
            elif self.high_res_mode == 1:
                # Improved resolution mode
                if round(scale, 2) >= 1.2:
                    zoom += 1
                    scale /= 2.0
                elif round(scale, 2) < 0.6:
                    zoom -= 1
                    scale *= 2.0
        else:
            # if round(scale, 2) >= 2.0:
            #     zoom += 1
            #     scale /= 2.0
            # elif round(scale, 2) < 1.0:
            #     zoom -= 1
            #     scale *= 2.0
            if round(scale, 2) >= 1.75:
                zoom += 1
                scale /= 2.0
            elif round(scale, 2) < 0.875:
                zoom -= 1
                scale *= 2.0


        zoom = clamp(zoom, map_source.min_zoom, map_source.max_zoom)
        if zoom != self._zoom:
            self.set_zoom_at(zoom, scatter.x, scatter.y, scale=scale)
            self.trigger_update(True)
        else:
            if zoom == map_source.min_zoom and round(scatter.scale, 2) < 1.0:
                scatter.scale = 1.0
                self.trigger_update(True)
            else:
                self.trigger_update(False)

        if map_source.bounds:
            self._apply_bounds()
        self._transform_lock = False
        self._scale = self._scatter.scale

    def _apply_bounds(self):
        # if the map_source have any constraints, apply them here.
        map_source = self.map_source
        zoom = self._zoom
        min_lon, min_lat, max_lon, max_lat = map_source.bounds
        xmin = map_source.get_x(zoom, min_lon)
        xmax = map_source.get_x(zoom, max_lon)
        ymin = map_source.get_y(zoom, min_lat)
        ymax = map_source.get_y(zoom, max_lat)

        dx = self.delta_x
        dy = self.delta_y
        oxmin, oymin = self._scatter.to_local(self.x, self.y)
        oxmax, oymax = self._scatter.to_local(self.right, self.top)
        s = self._scale
        cxmin = oxmin - dx
        if cxmin < xmin:
            self._scatter.x += (cxmin - xmin) * s
        cymin = oymin - dy
        if cymin < ymin:
            self._scatter.y += (cymin - ymin) * s
        cxmax = oxmax - dx
        if cxmax > xmax:
            self._scatter.x -= (xmax - cxmax) * s
        cymax = oymax - dy
        if cymax > ymax:
            self._scatter.y -= (ymax - cymax) * s

    def on__pause(self, instance, value):
        if not value:
            self.trigger_update(True)

    def trigger_update(self, full):
        self._need_redraw_full = full or self._need_redraw_full
        Clock.unschedule(self.do_update)
        Clock.schedule_once(self.do_update, -1)

    def do_update(self, dt):
        zoom = self._zoom
        scale = self._scale
        self.lon = self.map_source.get_lon(
            zoom, (self.center_x - self._scatter.x) / scale - self.delta_x
        )
        self.lat = self.map_source.get_lat(
            zoom, (self.center_y - self._scatter.y) / scale - self.delta_y
        )
        self.dispatch("on_map_relocated", zoom, Coordinate(self.lon, self.lat))
        for layer in self._layers:
            layer.reposition()

        if self._need_redraw_full:
            self._need_redraw_full = False
            self.move_tiles_to_background()
            self.load_visible_tiles()
        else:
            self.load_visible_tiles()

    def bbox_for_zoom(self, vx, vy, w, h, zoom):
        # return a tile-bbox for the zoom
        map_source = self.map_source
        size = map_source.dp_tile_size
        scale = self._scale

        max_x_end = map_source.get_col_count(zoom)
        max_y_end = map_source.get_row_count(zoom)

        x_count = int(ceil(w / scale / float(size))) + 1
        y_count = int(ceil(h / scale / float(size))) + 1

        tile_x_first = int(clamp(vx / float(size), 0, max_x_end))
        tile_y_first = int(clamp(vy / float(size), 0, max_y_end))
        tile_x_last = tile_x_first + x_count
        tile_y_last = tile_y_first + y_count
        tile_x_last = int(clamp(tile_x_last, tile_x_first, max_x_end))
        tile_y_last = int(clamp(tile_y_last, tile_y_first, max_y_end))

        x_count = tile_x_last - tile_x_first
        y_count = tile_y_last - tile_y_first
        return (tile_x_first, tile_y_first, tile_x_last, tile_y_last, x_count, y_count)

    def load_visible_tiles(self):
        map_source = self.map_source
        vx, vy = self.viewport_pos
        zoom = self._zoom
        dirs = [0, 1, 0, -1, 0]
        bbox_for_zoom = self.bbox_for_zoom
        size = map_source.dp_tile_size

        (
            tile_x_first,
            tile_y_first,
            tile_x_last,
            tile_y_last,
            x_count,
            y_count,
        ) = bbox_for_zoom(vx, vy, self.width, self.height, zoom)

        # Adjust tiles behind us
        for tile in self._tiles_bg[:]:
            tile_x = tile.tile_x
            tile_y = tile.tile_y

            f = 2 ** (zoom - tile.zoom)
            w = self.width / f
            h = self.height / f
            (
                btile_x_first,
                btile_y_first,
                btile_x_last,
                btile_y_last,
                _,
                _,
            ) = bbox_for_zoom(vx / f, vy / f, w, h, tile.zoom)

            if (
                tile_x < btile_x_first
                or tile_x >= btile_x_last
                or tile_y < btile_y_first
                or tile_y >= btile_y_last
            ):
                tile.state = "done"
                self._tiles_bg.remove(tile)
                self.canvas_map.before.remove(tile.g_color)
                self.canvas_map.before.remove(tile)
                continue

            tsize = size * f
            tile.size = tsize, tsize
            tile.pos = (tile_x * tsize + self.delta_x, tile_y * tsize + self.delta_y)

        # Get rid of old tiles first
        for tile in self._tiles[:]:
            tile_x = tile.tile_x
            tile_y = tile.tile_y

            if (
                tile_x < tile_x_first
                or tile_x >= tile_x_last
                or tile_y < tile_y_first
                or tile_y >= tile_y_last
            ):
                tile.state = "done"
                self.tile_map_set(tile_x, tile_y, False)
                self._tiles.remove(tile)
                self.canvas_map.remove(tile)
                self.canvas_map.remove(tile.g_color)
            else:
                tile.size = (size, size)
                tile.pos = (tile_x * size + self.delta_x, tile_y * size + self.delta_y)

        # Load new tiles if needed
        x = tile_x_first + x_count // 2 - 1
        y = tile_y_first + y_count // 2 - 1
        arm_max = max(x_count, y_count) + 2
        arm_size = 1
        turn = 0
        while arm_size < arm_max:
            for i in range(arm_size):
                if (
                    not self.tile_in_tile_map(x, y)
                    and y >= tile_y_first
                    and y < tile_y_last
                    and x >= tile_x_first
                    and x < tile_x_last
                ):
                    self.load_tile(x, y, size, zoom)

                x += dirs[turn % 4 + 1]
                y += dirs[turn % 4]

            if turn % 2 == 1:
                arm_size += 1

            turn += 1

    def load_tile(self, x, y, size, zoom):
        if self.tile_in_tile_map(x, y) or zoom != self._zoom:
            return
        self.load_tile_for_source(self.map_source, 1.0, size, x, y, zoom)
        # XXX do overlay support
        self.tile_map_set(x, y, True)

    def load_tile_for_source(self, map_source, opacity, size, x, y, zoom):
        tile = Tile(size=(size, size), cache_dir=self.cache_dir)
        tile.g_color = Color(1, 1, 1, 0)
        tile.tile_x = x
        tile.tile_y = y
        tile.zoom = zoom
        tile.pos = (x * size + self.delta_x, y * size + self.delta_y)
        tile.map_source = map_source
        tile.state = "loading"
        if not self._pause:
            map_source.fill_tile(tile)
        self.canvas_map.add(tile.g_color)
        self.canvas_map.add(tile)
        self._tiles.append(tile)

    def move_tiles_to_background(self):
        # remove all the tiles of the main map to the background map
        # retain only the one who are on the current zoom level
        # for all the tile in the background, stop the download if not yet started.
        zoom = self._zoom
        tiles = self._tiles
        btiles = self._tiles_bg
        canvas_map = self.canvas_map
        tile_size = self.map_source.tile_size

        # move all tiles to background
        while tiles:
            tile = tiles.pop()
            if tile.state == "loading":
                tile.state = "done"
                continue
            btiles.append(tile)

        # clear the canvas
        canvas_map.clear()
        canvas_map.before.clear()
        self._tilemap = {}

        # unsure if it's really needed, i personnally didn't get issues right now
        # btiles.sort(key=lambda z: -z.zoom)

        # add all the btiles into the back canvas.
        # except for the tiles that are owned by the current zoom level
        for tile in btiles[:]:
            if tile.zoom == zoom:
                btiles.remove(tile)
                tiles.append(tile)
                tile.size = tile_size, tile_size
                canvas_map.add(tile.g_color)
                canvas_map.add(tile)
                self.tile_map_set(tile.tile_x, tile.tile_y, True)
                continue
            canvas_map.before.add(tile.g_color)
            canvas_map.before.add(tile)

    def remove_all_tiles(self):
        # clear the map of all tiles.
        self.canvas_map.clear()
        self.canvas_map.before.clear()
        for tile in self._tiles:
            tile.state = "done"
        del self._tiles[:]
        del self._tiles_bg[:]
        self._tilemap = {}

    def tile_map_set(self, tile_x, tile_y, value):
        key = tile_y * self.map_source.get_col_count(self._zoom) + tile_x
        if value:
            self._tilemap[key] = value
        else:
            self._tilemap.pop(key, None)

    def tile_in_tile_map(self, tile_x, tile_y):
        key = tile_y * self.map_source.get_col_count(self._zoom) + tile_x
        return key in self._tilemap

    def on_size(self, instance, size):
        for layer in self._layers:
            layer.size = size
        self.center_on(self.lat, self.lon)
        self.trigger_update(True)

    def on_pos(self, instance, pos):
        self.center_on(self.lat, self.lon)
        self.trigger_update(True)

    def on_map_source(self, instance, source):
        if isinstance(source, string_types):
            self.map_source = MapSource.from_provider(source)
        elif isinstance(source, (tuple, list)):
            cache_key, min_zoom, max_zoom, url, attribution, options = source
            self.map_source = MapSource(
                url=url,
                cache_key=cache_key,
                min_zoom=min_zoom,
                max_zoom=max_zoom,
                attribution=attribution,
                cache_dir=self.cache_dir,
                **options
            )
        elif isinstance(source, MapSource):
            self.map_source = source
        else:
            raise Exception("Invalid map source provider")
        self.zoom = clamp(self.zoom, self.map_source.min_zoom, self.map_source.max_zoom)
        self.remove_all_tiles()
        self.trigger_update(True)
