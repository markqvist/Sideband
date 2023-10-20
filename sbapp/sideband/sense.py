import RNS
import time

from RNS.vendor import umsgpack as umsgpack

class Sensor():
  SID_NONE      = 0x00
  SID_BATTERY   = 0x01
  SID_BAROMETER = 0x02

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

class Battery(Sensor):
  SID = Sensor.SID_BATTERY
  STALE_TIME = 10

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android() or RNS.vendor.platformutils.is_linux():
      from plyer import battery
      self.battery = battery

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android() or RNS.vendor.platformutils.is_linux():
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android() or RNS.vendor.platformutils.is_linux():
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android() or RNS.vendor.platformutils.is_linux():
        self.battery.get_state()
        b = self.battery.status
        self.data = {"charge_percent": b["percentage"], "charging": b["isCharging"]}
    
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

class Barometer(Sensor):
  SID = Sensor.SID_BAROMETER
  STALE_TIME = 5

  def __init__(self):
    super().__init__(type(self).SID, type(self).STALE_TIME)

    if RNS.vendor.platformutils.is_android():
      from plyer import barometer
      self.android_barometer = barometer

  def setup_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_barometer.enable()
      self.update_data()

  def teardown_sensor(self):
    if RNS.vendor.platformutils.is_android():
      self.android_barometer.disable()
      self.data = None

  def update_data(self):
    try:
      if RNS.vendor.platformutils.is_android():
        self.data = {"mbar": self.android_barometer.pressure}
    
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

class Telemeter():
  def __init__(self):
    self.available = {"battery": Battery, "barometer": Barometer}
    self.sensors = {}

  def enable(self, sensor):
    if sensor in self.available:
      if not sensor in self.sensors:
        self.sensors[sensor] = self.available[sensor]()
      if not self.sensors[sensor].active:
        self.sensors[sensor].start()
  
  def disable(self, sensor):
    if sensor in self.available:
      if sensor in self.sensors:
        if self.sensors[sensor].active:
          self.sensors[sensor].stop()

  def read(self, sensor):
    if sensor in self.available:
      if sensor in self.sensors:
        return self.sensors[sensor].data
    return None

  def read_all(self):
    readings = {}
    for sensor in self.sensors:
      if self.sensors[sensor].active:
        readings[sensor] = self.sensors[sensor].data
    return readings

  def pack(self):
    packed = {}
    for sensor in self.sensors:
      if self.sensors[sensor].active:
        packed[self.sensors[sensor].sid] = self.sensors[sensor].pack()
    return umsgpack.packb(packed)