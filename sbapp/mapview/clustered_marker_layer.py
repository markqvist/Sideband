# coding=utf-8
"""
Layer that support point clustering
===================================
"""

from math import atan, exp, floor, log, pi, sin, sqrt
from os.path import dirname, join

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)

from mapview.view import MapLayer, MapMarker

Builder.load_string(
    """
<ClusterMapMarker>:
    size_hint: None, None
    source: root.source
    size: list(map(dp, self.texture_size))
    allow_stretch: True

    Label:
        color: root.text_color
        pos: root.pos
        size: root.size
        text: "{}".format(root.num_points)
        font_size: dp(18)
"""
)


# longitude/latitude to spherical mercator in [0..1] range
def lngX(lng):
    return lng / 360.0 + 0.5


def latY(lat):
    if lat == 90:
        return 0
    if lat == -90:
        return 1
    s = sin(lat * pi / 180.0)
    y = 0.5 - 0.25 * log((1 + s) / (1 - s)) / pi
    return min(1, max(0, y))


# spherical mercator to longitude/latitude
def xLng(x):
    return (x - 0.5) * 360


def yLat(y):
    y2 = (180 - y * 360) * pi / 180
    return 360 * atan(exp(y2)) / pi - 90


class KDBush:
    """
    kdbush implementation from:
    https://github.com/mourner/kdbush/blob/master/src/kdbush.js
    """

    def __init__(self, points, node_size=64):
        self.points = points
        self.node_size = node_size

        self.ids = ids = [0] * len(points)
        self.coords = coords = [0] * len(points) * 2
        for i, point in enumerate(points):
            ids[i] = i
            coords[2 * i] = point.x
            coords[2 * i + 1] = point.y

        self._sort(ids, coords, node_size, 0, len(ids) - 1, 0)

    def range(self, min_x, min_y, max_x, max_y):
        return self._range(
            self.ids, self.coords, min_x, min_y, max_x, max_y, self.node_size
        )

    def within(self, x, y, r):
        return self._within(self.ids, self.coords, x, y, r, self.node_size)

    def _sort(self, ids, coords, node_size, left, right, depth):
        if right - left <= node_size:
            return
        m = int(floor((left + right) / 2.0))
        self._select(ids, coords, m, left, right, depth % 2)
        self._sort(ids, coords, node_size, left, m - 1, depth + 1)
        self._sort(ids, coords, node_size, m + 1, right, depth + 1)

    def _select(self, ids, coords, k, left, right, inc):
        swap_item = self._swap_item
        while right > left:
            if (right - left) > 600:
                n = float(right - left + 1)
                m = k - left + 1
                z = log(n)
                s = 0.5 + exp(2 * z / 3.0)
                sd = 0.5 * sqrt(z * s * (n - s) / n) * (-1 if (m - n / 2.0) < 0 else 1)
                new_left = max(left, int(floor(k - m * s / n + sd)))
                new_right = min(right, int(floor(k + (n - m) * s / n + sd)))
                self._select(ids, coords, k, new_left, new_right, inc)

            t = coords[2 * k + inc]
            i = left
            j = right

            swap_item(ids, coords, left, k)
            if coords[2 * right + inc] > t:
                swap_item(ids, coords, left, right)

            while i < j:
                swap_item(ids, coords, i, j)
                i += 1
                j -= 1
                while coords[2 * i + inc] < t:
                    i += 1
                while coords[2 * j + inc] > t:
                    j -= 1

            if coords[2 * left + inc] == t:
                swap_item(ids, coords, left, j)
            else:
                j += 1
                swap_item(ids, coords, j, right)

            if j <= k:
                left = j + 1
            if k <= j:
                right = j - 1

    def _swap_item(self, ids, coords, i, j):
        swap = self._swap
        swap(ids, i, j)
        swap(coords, 2 * i, 2 * j)
        swap(coords, 2 * i + 1, 2 * j + 1)

    def _swap(self, arr, i, j):
        tmp = arr[i]
        arr[i] = arr[j]
        arr[j] = tmp

    def _range(self, ids, coords, min_x, min_y, max_x, max_y, node_size):
        stack = [0, len(ids) - 1, 0]
        result = []
        x = y = 0

        while stack:
            axis = stack.pop()
            right = stack.pop()
            left = stack.pop()

            if right - left <= node_size:
                for i in range(left, right + 1):
                    x = coords[2 * i]
                    y = coords[2 * i + 1]
                    if x >= min_x and x <= max_x and y >= min_y and y <= max_y:
                        result.append(ids[i])
                continue

            m = int(floor((left + right) / 2.0))

            x = coords[2 * m]
            y = coords[2 * m + 1]

            if x >= min_x and x <= max_x and y >= min_y and y <= max_y:
                result.append(ids[m])

            nextAxis = (axis + 1) % 2

            if min_x <= x if axis == 0 else min_y <= y:
                stack.append(left)
                stack.append(m - 1)
                stack.append(nextAxis)
            if max_x >= x if axis == 0 else max_y >= y:
                stack.append(m + 1)
                stack.append(right)
                stack.append(nextAxis)

        return result

    def _within(self, ids, coords, qx, qy, r, node_size):
        sq_dist = self._sq_dist
        stack = [0, len(ids) - 1, 0]
        result = []
        r2 = r * r

        while stack:
            axis = stack.pop()
            right = stack.pop()
            left = stack.pop()

            if right - left <= node_size:
                for i in range(left, right + 1):
                    if sq_dist(coords[2 * i], coords[2 * i + 1], qx, qy) <= r2:
                        result.append(ids[i])
                continue

            m = int(floor((left + right) / 2.0))

            x = coords[2 * m]
            y = coords[2 * m + 1]

            if sq_dist(x, y, qx, qy) <= r2:
                result.append(ids[m])

            nextAxis = (axis + 1) % 2

            if (qx - r <= x) if axis == 0 else (qy - r <= y):
                stack.append(left)
                stack.append(m - 1)
                stack.append(nextAxis)
            if (qx + r >= x) if axis == 0 else (qy + r >= y):
                stack.append(m + 1)
                stack.append(right)
                stack.append(nextAxis)

        return result

    def _sq_dist(self, ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy


class Cluster:
    def __init__(self, x, y, num_points, id, props):
        self.x = x
        self.y = y
        self.num_points = num_points
        self.zoom = float("inf")
        self.id = id
        self.props = props
        self.parent_id = None
        self.widget = None

        # preprocess lon/lat
        self.lon = xLng(x)
        self.lat = yLat(y)


class Marker:
    def __init__(self, lon, lat, cls=MapMarker, options=None):
        self.lon = lon
        self.lat = lat
        self.cls = cls
        self.options = options

        # preprocess x/y from lon/lat
        self.x = lngX(lon)
        self.y = latY(lat)

        # cluster information
        self.id = None
        self.zoom = float("inf")
        self.parent_id = None
        self.widget = None

    def __repr__(self):
        return "<Marker lon={} lat={} source={}>".format(
            self.lon, self.lat, self.source
        )


class SuperCluster:
    """Port of supercluster from mapbox in pure python
    """

    def __init__(self, min_zoom=0, max_zoom=16, radius=40, extent=512, node_size=64):
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.radius = radius
        self.extent = extent
        self.node_size = node_size

    def load(self, points):
        """Load an array of markers.
        Once loaded, the index is immutable.
        """
        from time import time

        self.trees = {}
        self.points = points

        for index, point in enumerate(points):
            point.id = index

        clusters = points
        for z in range(self.max_zoom, self.min_zoom - 1, -1):
            start = time()
            print("build tree", z)
            self.trees[z + 1] = KDBush(clusters, self.node_size)
            print("kdbush", (time() - start) * 1000)
            start = time()
            clusters = self._cluster(clusters, z)
            print(len(clusters))
            print("clustering", (time() - start) * 1000)
        self.trees[self.min_zoom] = KDBush(clusters, self.node_size)

    def get_clusters(self, bbox, zoom):
        """For the given bbox [westLng, southLat, eastLng, northLat], and
        integer zoom, returns an array of clusters and markers
        """
        tree = self.trees[self._limit_zoom(zoom)]
        ids = tree.range(lngX(bbox[0]), latY(bbox[3]), lngX(bbox[2]), latY(bbox[1]))
        clusters = []
        for i in range(len(ids)):
            c = tree.points[ids[i]]
            if isinstance(c, Cluster):
                clusters.append(c)
            else:
                clusters.append(self.points[c.id])
        return clusters

    def _limit_zoom(self, z):
        return max(self.min_zoom, min(self.max_zoom + 1, z))

    def _cluster(self, points, zoom):
        clusters = []
        c_append = clusters.append
        trees = self.trees
        r = self.radius / float(self.extent * pow(2, zoom))

        # loop through each point
        for i in range(len(points)):
            p = points[i]
            # if we've already visited the point at this zoom level, skip it
            if p.zoom <= zoom:
                continue
            p.zoom = zoom

            # find all nearby points
            tree = trees[zoom + 1]
            neighbor_ids = tree.within(p.x, p.y, r)

            num_points = 1
            if isinstance(p, Cluster):
                num_points = p.num_points
            wx = p.x * num_points
            wy = p.y * num_points

            props = None

            for j in range(len(neighbor_ids)):
                b = tree.points[neighbor_ids[j]]
                # filter out neighbors that are too far or already processed
                if zoom < b.zoom:
                    num_points2 = 1
                    if isinstance(b, Cluster):
                        num_points2 = b.num_points
                    # save the zoom (so it doesn't get processed twice)
                    b.zoom = zoom
                    #  accumulate coordinates for calculating weighted center
                    wx += b.x * num_points2
                    wy += b.y * num_points2
                    num_points += num_points2
                    b.parent_id = i

            if num_points == 1:
                c_append(p)
            else:
                p.parent_id = i
                c_append(
                    Cluster(wx / num_points, wy / num_points, num_points, i, props)
                )
        return clusters


class ClusterMapMarker(MapMarker):
    source = StringProperty(join(dirname(__file__), "icons", "cluster.png"))
    cluster = ObjectProperty()
    num_points = NumericProperty()
    text_color = ListProperty([0.1, 0.1, 0.1, 1])

    def on_cluster(self, instance, cluster):
        self.num_points = cluster.num_points

    def on_touch_down(self, touch):
        return False


class ClusteredMarkerLayer(MapLayer):
    cluster_cls = ObjectProperty(ClusterMapMarker)
    cluster_min_zoom = NumericProperty(0)
    cluster_max_zoom = NumericProperty(16)
    cluster_radius = NumericProperty("40dp")
    cluster_extent = NumericProperty(512)
    cluster_node_size = NumericProperty(64)

    def __init__(self, **kwargs):
        self.cluster = None
        self.cluster_markers = []
        super().__init__(**kwargs)

    def add_marker(self, lon, lat, cls=MapMarker, options=None):
        if options is None:
            options = {}
        marker = Marker(lon, lat, cls, options)
        self.cluster_markers.append(marker)
        return marker

    def remove_marker(self, marker):
        self.cluster_markers.remove(marker)

    def reposition(self):
        if self.cluster is None:
            self.build_cluster()
        margin = dp(48)
        mapview = self.parent
        set_marker_position = self.set_marker_position
        bbox = mapview.get_bbox(margin)
        bbox = (bbox[1], bbox[0], bbox[3], bbox[2])
        self.clear_widgets()
        for point in self.cluster.get_clusters(bbox, mapview.zoom):
            widget = point.widget
            if widget is None:
                widget = self.create_widget_for(point)
            set_marker_position(mapview, widget)
            self.add_widget(widget)

    def build_cluster(self):
        self.cluster = SuperCluster(
            min_zoom=self.cluster_min_zoom,
            max_zoom=self.cluster_max_zoom,
            radius=self.cluster_radius,
            extent=self.cluster_extent,
            node_size=self.cluster_node_size,
        )
        self.cluster.load(self.cluster_markers)

    def create_widget_for(self, point):
        if isinstance(point, Marker):
            point.widget = point.cls(lon=point.lon, lat=point.lat, **point.options)
        elif isinstance(point, Cluster):
            point.widget = self.cluster_cls(lon=point.lon, lat=point.lat, cluster=point)
        return point.widget

    def set_marker_position(self, mapview, marker):
        x, y = mapview.get_window_xy_from(marker.lat, marker.lon, mapview.zoom)
        marker.x = int(x - marker.width * marker.anchor_x)
        marker.y = int(y - marker.height * marker.anchor_y)
