import os
import RNS
import time
import struct
import threading

from RNS.vendor import umsgpack as umsgpack

class Telemeter():
  @staticmethod
  def from_packed(packed):
    try:
      p = umsgpack.unpackb(packed)
      t = Telemeter(from_packed=True)
      for sid in p:
        if sid in t.sids:
          name = None
          s = t.sids[sid]()
          for n in t.available:
            if t.sids[t.available[n]] == type(s):
              name = n

          if name != None:
            s.data = s.unpack(p[sid])
            s.active = True
            t.sensors[name] = s

      return t

    except Exception as e:
      RNS.log("An error occurred while unpacking telemetry. The contained exception was: "+str(e), RNS.LOG_ERROR)
      return None

  def __init__(self, from_packed=False):
    self.sids = {
      Sensor.SID_TIME: Time,
      Sensor.SID_BATTERY: Battery,
      Sensor.SID_PRESSURE: Pressure,
      Sensor.SID_LOCATION: Location,
      Sensor.SID_PHYSICAL_LINK: PhysicalLink,
      Sensor.SID_TEMPERATURE: Temperature,
      Sensor.SID_HUMIDITY: Humidity,
      Sensor.SID_MAGNETIC_FIELD: MagneticField,
      Sensor.SID_AMBIENT_LIGHT: AmbientLight,
      Sensor.SID_GRAVITY: Gravity,
      Sensor.SID_ANGULAR_VELOCITY: AngularVelocity,
      Sensor.SID_ACCELERATION: Acceleration,
      Sensor.SID_PROXIMITY: Proximity,
    }
    self.available = {
      "time": Sensor.SID_TIME,
      "battery": Sensor.SID_BATTERY,
      "pressure": Sensor.SID_PRESSURE,
      "location": Sensor.SID_LOCATION,
      "physical_link": Sensor.SID_PHYSICAL_LINK,
      "temperature": Sensor.SID_TEMPERATURE,
      "humidity": Sensor.SID_HUMIDITY,
      "magnetic_field": Sensor.SID_MAGNETIC_FIELD,
      "ambient_light": Sensor.SID_AMBIENT_LIGHT,
      "gravity": Sensor.SID_GRAVITY,
      "angular_velocity": Sensor.SID_ANGULAR_VELOCITY,
      "acceleration": Sensor.SID_ACCELERATION,
      "proximity": Sensor.SID_PROXIMITY,
    }
    self.from_packed = from_packed
    self.sensors = {}
    if not self.from_packed:
      self.enable("time")

  def synthesize(self, sensor):
      if sensor in self.available:
        if not sensor in self.sensors:
          self.sensors[sensor] = self.available[sensor]()
          self.sensors[sensor].active = True

  def enable(self, sensor):
    if not self.from_packed:
      if sensor in self.available:
        if not sensor in self.sensors:
          self.sensors[sensor] = self.sids[self.available[sensor]]()
        if not self.sensors[sensor].active:
          self.sensors[sensor].start()
  
  def disable(self, sensor):
    if not self.from_packed:
      if sensor in self.available:
        if sensor in self.sensors:
          if self.sensors[sensor].active:
            self.sensors[sensor].stop()

  def stop_all(self):
    if not self.from_packed:
      for sensor in self.sensors:
        self.sensors[sensor].stop()

  def read(self, sensor):
    if not self.from_packed:
      if sensor in self.available:
        if sensor in self.sensors:
          return self.sensors[sensor].data
      return None
    else:
      if sensor in self.available:
        if sensor in self.sensors:
          return self.sensors[sensor]._data

  def read_all(self):
    readings = {}
    for sensor in self.sensors:
      if self.sensors[sensor].active:
        if not self.from_packed:
          readings[sensor] = self.sensors[sensor].data
        else:
          readings[sensor] = self.sensors[sensor]._data

    return readings

  def packed(self):
    packed = {}
    packed[Sensor.SID_TIME] = int(time.time())
    for sensor in self.sensors:
      if self.sensors[sensor].active:
        packed[self.sensors[sensor].sid] = self.sensors[sensor].pack()
    return umsgpack.packb(packed)

class Sensor():
  SID_NONE             = 0x00
  SID_TIME             = 0x01
  SID_LOCATION         = 0x02
  SID_PRESSURE         = 0x03
  SID_BATTERY          = 0x04
  SID_PHYSICAL_LINK    = 0x05
  SID_ACCELERATION     = 0x06
  SID_TEMPERATURE      = 0x07
  SID_HUMIDITY         = 0x08
  SID_MAGNETIC_FIELD   = 0x09
  SID_AMBIENT_LIGHT    = 0x0A
  SID_GRAVITY          = 0x0B
  SID_ANGULAR_VELOCITY = 0x0C
  SID_PROXIMITY        = 0x0E

  def __init__(self, sid = None, stale_time = None):
    self._sid = sid or Sensor.SID_NONE
    self._stale_time = stale_time
    self._data = None
    self.active = False
    self.last_update = 0
    self.last_read = 0

  @property
  def sid(self):
    return self._sid

  @property
  def data(self):
    if self._data == None or (self._stale_time != None and time.time() > self.last_update+self._stale_time):
      try:
        self.update_data()
      except:
        pass

    self.last_read = time.time()
    return self._data

  @data.setter
  def data(self, value):
    self.last_update = time.time()
    self._data = value

  def update_data(self):
    raise NotImplementedError()

  def setup_sensor(self):
    raise NotImplementedError()

  def teardown_sensor(self):
    raise NotImplementedError()

  def start(self):
    self.setup_sensor()
    self.active = True

  def stop(self):
    self.teardown_sensor()
    self.active = False

  def packb(self):
    return umsgpack.packb(self.pack())

  def unpackb(self, packed):
    return umsgpack.unpackb(self.unpack(packed))

  def pack(self):
    return self.data

  def unpack(self, packed):
    return packed

class Time(Sensor):
  SID = Sensor.SID_TIME
  STALE_TIME = 0.1

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

  def setup_sensor(self):
    self.update_data()

  def teardown_sensor(self):
    self.data = None

  def update_data(self):
    self.data = {"utc":int(time.time())}

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return d["utc"]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"utc": packed}
    except:
      return None

class Battery(Sensor):
  SID = Sensor.SID_BATTERY
  STALE_TIME = 10

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import battery
      self.battery = battery
    
    elif RNS.vendor.platformutils.is_linux():
      node_exists = False
      bn = 0
      node_name = None
      for bi in range(0,10):
          path = os.path.join('/sys', 'class', 'power_supply', 'BAT'+str(bi))
          if os.path.isdir(path):
              node_name = "BAT"+str(bi)
              break

      self.battery_node_name = node_name

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android() or RNS.vendor.platformutils.is_linux():
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android() or RNS.vendor.platformutils.is_linux():
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        self.battery.get_state()
        b = self.battery.status
        self.data = {"charge_percent": b["percentage"], "charging": b["isCharging"]}
      
      elif RNS.vendor.platformutils.is_linux():
        if self.battery_node_name:
          status = {"isCharging": None, "percentage": None}
          kernel_bat_path = os.path.join('/sys', 'class', 'power_supply', self.battery_node_name)
          uevent = os.path.join(kernel_bat_path, 'uevent')
          with open(uevent, "rb") as fle:
              lines = [
                  line.decode('utf-8').strip()
                  for line in fle.readlines()
              ]
          output = {
              line.split('=')[0]: line.split('=')[1]
              for line in lines
          }

          is_charging = output['POWER_SUPPLY_STATUS'] == 'Charging'
          charge_percent = float(output['POWER_SUPPLY_CAPACITY'])
          self.data = {"charge_percent": charge_percent, "charging": is_charging}
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return [d["charge_percent"], d["charging"]]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"charge_percent": packed[0], "charging": packed[1]}
    except:
      return None

class Pressure(Sensor):
  SID = Sensor.SID_PRESSURE
  STALE_TIME = 5

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import barometer
      self.android_sensor = barometer

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.enable()
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.disable()
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        self.data = {"mbar": self.android_sensor.pressure}
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return d["mbar"]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"mbar": packed}
    except:
      return None

class Location(Sensor):
  SID = Sensor.SID_LOCATION
  
  STALE_TIME = 15
  MIN_DISTANCE = 4
  ACCURACY_TARGET = 250

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    self._raw = None
    self._min_distance = Location.MIN_DISTANCE
    self._accuracy_target = Location.ACCURACY_TARGET

    self.latitude = None
    self.longtitude = None
    self.altitude = None
    self.speed = None
    self.bearing = None
    self.accuracy = None

    if RNS.vendor.platformutils.is_android():
      from plyer import gps
      self.gps = gps

  def set_min_distance(self, distance):
    try:
      d = float(distance)
      if d >= 0:
        self._min_distance = d
        self.teardown_sensor()
        self.setup_sensor()
    except:
      pass

  def set_accuracy_target(self, target):
    try:
      t = float(target)
      if t >= 0:
        self._accuracy_target = t
    except:
      pass

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      from android.permissions import request_permissions, check_permission

      if check_permission("android.permission.ACCESS_COARSE_LOCATION") and check_permission("android.permission.ACCESS_FINE_LOCATION"):
        self.gps.configure(on_location=self.android_location_callback)
        self.gps.start(minTime=self._stale_time, minDistance=self._min_distance)
      
      self.update_data()
    
  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.gps.stop()
      self.data = None

  def android_location_callback(self, **kwargs):
    self._raw = kwargs
    self._last_update = time.time()

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        if "lat" in self._raw:
          self.latitude   = self._raw["lat"]
        if "lon" in self._raw:
          self.longtitude = self._raw["lon"]
        if "altitude" in self._raw:
          self.altitude   = self._raw["altitude"]
        if "speed" in self._raw:
          self.speed      = self._raw["speed"]
          if self.speed < 0:
            self.speed = 0
        if "bearing" in self._raw:
          self.bearing    = self._raw["bearing"]
        if "accuracy" in self._raw:
          self.accuracy   = self._raw["accuracy"]
          if self.accuracy < 0:
            self.accuracy = 0

        if self.accuracy != None and self.accuracy <= self._accuracy_target:        
          self.data = {
            "latitude": round(self.latitude, 6),
            "longtitude": round(self.longtitude, 6),
            "altitude": round(self.altitude, 2),
            "speed": round(self.speed, 2),
            "bearing": round(self.bearing, 2),
            "accuracy": round(self.accuracy, 2),
            "last_update": int(self._last_update),
            }
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      try:
        return [
          struct.pack("!i", int(round(d["latitude"], 6)*1e6)),
          struct.pack("!i", int(round(d["longtitude"], 6)*1e6)),
          struct.pack("!I", int(round(d["altitude"], 2)*1e2)),
          struct.pack("!I", int(round(d["speed"], 2)*1e2)),
          struct.pack("!I", int(round(d["bearing"], 2)*1e2)),
          struct.pack("!H", int(round(d["accuracy"], 2)*1e2)),
          d["last_update"],
        ]
      except Exception as e:
        RNS.log("An error occurred while packing location sensor data. The contained exception was: "+str(e), RNS.LOG_ERROR)
        return None

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {
          "latitude": struct.unpack("!i", packed[0])[0]/1e6,
          "longtitude": struct.unpack("!i", packed[1])[0]/1e6,
          "altitude": struct.unpack("!I", packed[2])[0]/1e2,
          "speed": struct.unpack("!I", packed[3])[0]/1e2,
          "bearing": struct.unpack("!I", packed[4])[0]/1e2,
          "accuracy": struct.unpack("!H", packed[5])[0]/1e2,
          "last_update": packed[6],
        }
    except:
      return None

class PhysicalLink(Sensor):
  SID = Sensor.SID_PHYSICAL_LINK
  STALE_TIME = 5

  def __init__(self):
    self.rssi = None
    self.snr = None
    self.q = None
    super().__init__(type(self).SID, type(self).STALE_TIME)

  def setup_sensor(self):
      self.update_data()

  def teardown_sensor(self):
      self.data = None

  def update_data(self):
    try:
      self.data = {"rssi": self.rssi, "snr": self.snr, "q": self.q}

    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return [d["rssi"], d["snr"], d["q"]]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"rssi": packed[0], "snr": packed[1], "q": packed[2]}
    except:
      return None

class Temperature(Sensor):
  SID = Sensor.SID_TEMPERATURE
  STALE_TIME = 5

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import temperature
      self.android_sensor = temperature

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.enable()
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.disable()
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        self.data = {"c": round(self.android_sensor.temperature, 2)}
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return d["percent_relative"]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"percent_relative": packed}
    except:
      return None

class Humidity(Sensor):
  SID = Sensor.SID_HUMIDITY
  STALE_TIME = 5

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import humidity
      self.android_sensor = humidity

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.enable()
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.disable()
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        self.data = {"percent_relative": round(self.android_sensor.tell, 2)}
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return d["percent_relative"]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"percent_relative": packed}
    except:
      return None

class MagneticField(Sensor):
  SID = Sensor.SID_MAGNETIC_FIELD
  STALE_TIME = 1

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import compass
      self.android_sensor = compass

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.enable()
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.disable()
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        vectors = self.android_sensor.field
        self.data = {"x": round(vectors[0], 6), "y": round(vectors[1], 6), "z": round(vectors[2], 6)}
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return [d["x"], d["y"], d["z"]]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"x": packed[0], "y": packed[1], "z": packed[2]}
    except:
      return None

class AmbientLight(Sensor):
  SID = Sensor.SID_AMBIENT_LIGHT
  STALE_TIME = 1

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import light
      self.android_sensor = light

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.enable()
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.disable()
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        self.data = {"lux": round(self.android_sensor.illumination, 2)}
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return d["lux"]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"lux": packed}
    except:
      return None

class Gravity(Sensor):
  SID = Sensor.SID_GRAVITY
  STALE_TIME = 1

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import gravity
      self.android_sensor = gravity

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.enable()
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.disable()
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        vectors = self.android_sensor.gravity
        self.data = {"x": round(vectors[0], 6), "y": round(vectors[1], 6), "z": round(vectors[2], 6)}
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return [d["x"], d["y"], d["z"]]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"x": packed[0], "y": packed[1], "z": packed[2]}
    except:
      return None

class AngularVelocity(Sensor):
  SID = Sensor.SID_ANGULAR_VELOCITY
  STALE_TIME = 1

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import gyroscope
      self.android_sensor = gyroscope

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.enable()
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.disable()
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        vectors = self.android_sensor.rotation
        self.data = {"x": round(vectors[0], 6), "y": round(vectors[1], 6), "z": round(vectors[2], 6)}
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return [d["x"], d["y"], d["z"]]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"x": packed[0], "y": packed[1], "z": packed[2]}
    except:
      return None

class Acceleration(Sensor):
  SID = Sensor.SID_ACCELERATION
  STALE_TIME = 1

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import accelerometer
      self.android_sensor = accelerometer

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.enable()
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.disable()
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        vectors = self.android_sensor.acceleration
        self.data = {"x": round(vectors[0], 6), "y": round(vectors[1], 6), "z": round(vectors[2], 6)}
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return [d["x"], d["y"], d["z"]]

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return {"x": packed[0], "y": packed[1], "z": packed[2]}
    except:
      return None

class Proximity(Sensor):
  SID = Sensor.SID_PROXIMITY
  STALE_TIME = 1

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import proximity
      self.android_sensor = proximity

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.enable()
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_sensor.disable()
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        self.data = self.android_sensor.proximity
    
    except:
      self.data = None

  def pack(self):
    d = self.data
    if d == None:
      return None
    else:
      return d

  def unpack(self, packed):
    try:
      if packed == None:
        return None
      else:
        return packed
    except:
      return None