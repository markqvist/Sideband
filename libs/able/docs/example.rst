Usage Examples
==============

Alert
-----

.. literalinclude:: ./examples/alert.py
   :language: python

Full example code: `alert <https://github.com/b3b/able/blob/master/examples/alert/>`_


Change MTU
----------
.. literalinclude:: ./examples/mtu.py
   :language: python


Scan settings
-------------

.. code-block:: python

  from able import BluetoothDispatcher
  from able.scan_settings import ScanSettingsBuilder, ScanSettings

  # Use faster detection (more power usage) mode
  settings = ScanSettingsBuilder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
  BluetoothDispatcher().start_scan(settings=settings)


Scan filters
------------

.. code-block:: python

  from able import BluetoothDispatcher
  from able.filters import (
      DeviceAddressFilter,
      DeviceNameFilter,
      ManufacturerDataFilter,
      ServiceDataFilter,
      ServiceUUIDFilter
  )

  ble = BluetoothDispatcher()

  # Start scanning with the condition that device has one of names: "Device1" or "Device2"
  ble.start_scan(filters=[DeviceNameFilter("Device1"), DeviceNameFilter("Device2")])
  ble.stop_scan()

  # Start scanning with the condition that
  # device advertises "180f" service and one of names: "Device1" or "Device2"
  ble.start_scan(filters=[
      ServiceUUIDFilter('0000180f-0000-1000-8000-00805f9b34fb') & DeviceNameFilter("Device1"),
      ServiceUUIDFilter('0000180f-0000-1000-8000-00805f9b34fb') & DeviceNameFilter("Device2")
  ])


Adapter state
-------------

.. literalinclude:: ./examples/adapter_state_change.py
   :language: python


Advertising
-----------

Advertise with data and additional (scannable) data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

  from able import BluetoothDispatcher
  from able.advertising import (
      Advertiser,
      AdvertiseData,
      ManufacturerData,
      Interval,
      ServiceUUID,
      ServiceData,
      TXPower,
  )

  advertiser = Advertiser(
      ble=BluetoothDispatcher(),
      data=AdvertiseData(ServiceUUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")),
      scan_data=AdvertiseData(ManufacturerData(id=0xAABB, data=b"some data")),
      interval=Interval.MEDIUM,
      tx_power=TXPower.MEDIUM,
  )

  advertiser.start()


Set and advertise device name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  from able import BluetoothDispatcher
  from able.advertising import Advertiser, AdvertiseData, DeviceName

  ble = BluetoothDispatcher()
  ble.name = "New test device name"

  # There must be a wait and check, it takes time for new name to take effect
  print(f"New device name is set: {ble.name}")

  Advertiser(
      ble=ble,
      data=AdvertiseData(DeviceName())
  )


Battery service data
^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ./examples/advertising_battery.py
   :language: python


Use iBeacon advertising format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  import uuid
  from able import BluetoothDispatcher
  from able.advertising import Advertiser, AdvertiseData, ManufacturerData


  data = AdvertiseData(
      ManufacturerData(
          0x4C,  # Apple Manufacturer ID
          bytes([
              0x2, # SubType: Custom Manufacturer Data
              0x15 # Subtype lenth
          ]) +
          uuid.uuid4().bytes +  # UUID of beacon
          bytes([
              0, 15,  # Major value
              0, 1,  # Minor value
              10  # RSSI, dBm at 1m
          ]))
  )

  Advertiser(BluetoothDispatcher(), data).start()


Android Services
----------------

BLE devices scanning service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**main.py**

.. literalinclude:: ./examples/service_scan_main.py
   :language: python

**service.py**

.. literalinclude:: ./examples/service_scan_service.py
   :language: python

Full example code: `service_scan <https://github.com/b3b/able/blob/master/examples/service_scan/>`_


Advertising service
^^^^^^^^^^^^^^^^^^^

**main.py**

.. literalinclude:: ./examples/service_advertise_main.py
   :language: python

**service.py**

.. literalinclude:: ./examples/service_advertise_service.py
   :language: python

Full example code: `service_advertise <https://github.com/b3b/able/blob/master/examples/service_advertise/>`_


Connect to multiple devices
---------------------------

.. literalinclude:: ./examples/multi_devices/main.py
   :language: python

Full example code: `multi_devices <https://github.com/b3b/able/blob/master/examples/multi_devices/>`_
