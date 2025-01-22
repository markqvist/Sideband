# This plugin lets you remotely query and view a
# number of different image sources in Sideband,
# including remote or local webcams, video sources
# or images stored in a filesystem.
#
# This plugin requires the "pillow" pip package.
#
# For HTTP and local file sources, no extras are
# required, but for fetching images from connected
# video sources, you need "opencv-python" from pip.

import io
import os
import RNS
import time
import queue
import requests
import threading
import importlib
from PIL import Image as PilImage

if importlib.util.find_spec("cv2") != None:
    import cv2

# Add view sources to the plugin
def register_view_sources():
    ViewCommandPlugin.add_source("xkcd", HttpSource("https://imgs.xkcd.com/comics/tsp_vs_tbsp.png"))
    ViewCommandPlugin.add_source("camera", CameraSource(camera_index=0))
    ViewCommandPlugin.add_source("rocks", FileSource("~/Downloads/rocks.jpg"))
    ViewCommandPlugin.add_source("osaka", StreamSource("http://honjin1.miemasu.net/nphMotionJpeg?Resolution=640x480&Quality=Standard"))
    ViewCommandPlugin.add_source("factory", StreamSource("http://takemotopiano.aa1.netvolante.jp:8190/nphMotionJpeg?Resolution=640x480&Quality=Standard&Framerate=1"))

quality_presets = {
    "lora": {"max": 160, "quality": 18},
    "low": {"max": 256, "quality": 25},
    "default": {"max": 320, "quality": 33},
    "medium": {"max": 480, "quality": 50},
    "high": {"max": 960, "quality": 65},
    "hd": {"max": 1920, "quality": 75},
    "4k": {"max": 3840, "quality": 65},
}

if not "default" in quality_presets:
    raise ValueError("No default quality preset defined, please define one and reload the plugin")

class ViewSource():
    DEFAULT_STALE_TIME = 3.14159

    def __init__(self):
        self.source_data = None
        self.last_update = 0
        self.stale_time = ViewSource.DEFAULT_STALE_TIME

    def is_stale(self):
        return time.time() > self.last_update + self.stale_time

    def update(self):
        raise NotImplementedError()

    def scaled_image(self, max_dimension, quality):
        with PilImage.open(io.BytesIO(self.source_data)) as im:
            im.thumbnail((max_dimension, max_dimension))
            buf = io.BytesIO()
            im.save(buf, format="webp", quality=quality)
            return buf.getvalue()

    def get_image_field(self, preset="default"):
        if not preset in quality_presets:
            preset = "default"

        try:
            if self.is_stale():
                self.update()
            
            if self.source_data != None:
                max_dimension = quality_presets[preset]["max"]
                quality = quality_presets[preset]["quality"]
                return ["webp", self.scaled_image(max_dimension, quality)]

        except Exception as e:
            RNS.log(f"Could not create image field for {self}. The contained exception was: {e}", RNS.LOG_ERROR)
            RNS.trace_exception(e)

        return None

class HttpSource(ViewSource):
    def __init__(self, url):
        self.url = url
        super().__init__()

    def update(self):
        image_request = requests.get(self.url, stream=True)
        if image_request.status_code == 200:
            self.source_data = image_request.content
            self.last_update = time.time()
        else:
            self.source_data = None

class CameraSource(ViewSource):
    def __init__(self, camera_index=0, camera_width=1280, camera_height=720):
        self.camera_index  = camera_index
        self.camera_width  = camera_width
        self.camera_height = camera_height
        self.camera_ready  = False
        self.frame_queue   = queue.Queue()
        super().__init__()

        self.start_reading()

    def start_reading(self):
        self.camera = cv2.VideoCapture(self.camera_index)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        threading.Thread(target=self.read_frames, daemon=True).start()

    def read_frames(self):
        try:
            while True:
                ret, frame = self.camera.read()
                self.camera_ready = True
                if not ret:
                    self.camera_ready = False
                    break
                
                if not self.frame_queue.empty():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                
                self.frame_queue.put(frame)

        except Exception as e:
            RNS.log("An error occurred while reading frames from the camera: "+str(e), RNS.LOG_ERROR)

        self.release_camera()

    def update(self):
        if not self.camera:
            self.start_reading()
            while not self.camera_ready:
              time.sleep(0.2)
        
        retval, frame = self.camera.read()
      
        if not retval:
            self.source_data = None
        else:
            retval, buffer = cv2.imencode(".png", frame)
            self.source_data = io.BytesIO(buffer).getvalue()
            self.last_update = time.time()

    def release_camera(self):
        try:
            self.camera.release()
        except:
            pass  
        
        self.camera = None
        self.camera_ready = False

class StreamSource(ViewSource):
    DEFAULT_IDLE_TIMEOUT = 10

    def __init__(self, url=None):
        self.url          = url
        self.stream_ready = False
        self.frame_queue  = queue.Queue()
        self.stream       = None
        self.started      = 0
        self.idle_timeout = StreamSource.DEFAULT_IDLE_TIMEOUT
        super().__init__()

        self.start_reading()

    def start_reading(self):
        self.stream  = cv2.VideoCapture(self.url)
        self.started = time.time()
        threading.Thread(target=self.read_frames, daemon=True).start()

    def read_frames(self):
        try:
            while max(self.last_update, self.started)+self.idle_timeout > time.time():
                ret, frame = self.stream.read()
                if not ret:
                    self.stream_ready = False
                else:
                    self.stream_ready = True            
                    if not self.frame_queue.empty():
                        if self.frame_queue.qsize() > 1:
                            try:
                                self.frame_queue.get_nowait()
                            except queue.Empty:
                                pass
                    
                    self.frame_queue.put(frame)

            RNS.log(str(self)+" idled", RNS.LOG_DEBUG)

        except Exception as e:
            RNS.log("An error occurred while reading frames from the stream: "+str(e), RNS.LOG_ERROR)

        self.release_stream()

    def update(self):
        if not self.stream:
            self.start_reading()
            while not self.stream_ready:
              time.sleep(0.2)
              if self.stream == None:
                self.source_data = None
                return

        frame = self.frame_queue.get()
        retval, buffer = cv2.imencode(".png", frame)
        self.source_data = io.BytesIO(buffer).getvalue()
        self.last_update = time.time()

    def release_stream(self):
        try:
            self.stream.release()
        except:
            pass  
        
        self.stream = None
        self.stream_ready = False

class FileSource(ViewSource):
    def __init__(self, path):
        self.path = os.path.expanduser(path)
        super().__init__()

    def update(self):
        try:
            with open(self.path, "rb") as image_file:
                self.source_data = image_file.read()

        except Exception as e:
            RNS.log("Could not read image at \"{self.path}\": "+str(e), RNS.LOG_ERROR)
            self.source_data = None

class ViewCommandPlugin(SidebandCommandPlugin):
    command_name = "view"
    sources      = {}

    stamptimefmt = "%Y-%m-%d %H:%M:%S"

    def start(self):
        RNS.log("View command plugin starting...")
        super().start()

    def stop(self):
        super().stop()

    @staticmethod
    def add_source(name, source):
        ViewCommandPlugin.sources[name] = source

    def message_response(self, message, destination):
        self.get_sideband().send_message(
            message,
            destination,
            False,                # Don't use propagation by default, try direct first
            skip_fields = True,   # Don't include any additional fields automatically
            no_display = True,    # Don't display this message in the message stream
        )

    def image_response(self, message, image_field, destination):
        self.get_sideband().send_message(
            message,
            destination,
            False,                # Don't use propagation by default, try direct first
            skip_fields = True,   # Don't include any additional fields automatically
            no_display = True,    # Don't display this message in the message stream
            image = image_field,  # Add the scaled and compressed image
        )

    def timestamp_str(self, time_s):
        timestamp = time.localtime(time_s)
        return time.strftime(self.stamptimefmt, timestamp)

    def handle_command(self, arguments, lxm):
        requestor = lxm.source_hash

        if len(arguments) == 0:
            self.message_response("No view source was specified", requestor)
            return

        if arguments[0] == "--list" or arguments[0] == "-l":
            if len(self.sources) == 0:
                response = "No sources available on this system"
            else:
                response = "Available Sources:\n"
                for source in self.sources:
                    response += "\n - "+str(source)

            self.message_response(response, requestor)
            return

        try:
            source = arguments[0]
            if len(arguments) > 1:
                quality_preset = arguments[1]
            else:
                quality_preset = "default"

            if not source in self.sources:
                self.message_response("The specified view source does not exist on this system", requestor)
            
            else:
                image_field     = self.sources[source].get_image_field(quality_preset)
                image_timestamp = self.timestamp_str(self.sources[source].last_update)
                message         = "#!md\n" # Tell sideband to format this message
                message        += f"Source [b]{source}[/b] at [b]{image_timestamp}[/b]"

                if image_field != None:
                    self.image_response(message, image_field, requestor)
                else:
                    self.message_response("The image source could not be retrieved or prepared", requestor)

        except Exception as e:
            self.message_response(f"An error occurred:\n\n{e}", requestor)

register_view_sources()

# Finally, tell Sideband what class in this
# file is the actual plugin class.
plugin_class = ViewCommandPlugin
