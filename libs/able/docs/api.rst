API
---

.. automodule:: able

Client
^^^^^^

BluetoothDispatcher
"""""""""""""""""""

.. autoclass:: BluetoothDispatcher
   :members: adapter,
             gatt,
             bonded_devices,
             name,
             set_queue_timeout,
             start_scan,
             stop_scan,
             connect_by_device_address,
             connect_gatt,
             close_gatt,
             discover_services,
             enable_notifications,
             write_descriptor,
             write_characteristic,
             read_characteristic,
             update_rssi,
             request_mtu,
             on_error,
             on_gatt_release,
             on_scan_started,
             on_scan_completed,
             on_device,
             on_bluetooth_adapter_state_changeable,
             on_connection_state_change,
             on_services,
             on_characteristic_changed,
             on_characteristic_read,
             on_characteristic_write,
             on_descriptor_read,
             on_descriptor_write,
             on_rssi_updated,
             on_mtu_changed,

Decorators
""""""""""

.. autofunction:: require_bluetooth_enabled


Advertisement
"""""""""""""

.. autoclass:: Advertisement

   .. autoclass:: able::Advertisement.ad_types

Services
""""""""

.. autoclass:: Services
   :members:

Constants
"""""""""

.. autodata:: GATT_SUCCESS
.. autodata:: STATE_CONNECTED
.. autodata:: STATE_DISCONNECTED
.. autoclass:: AdapterState
   :members:
   :member-order: bysource
.. autoclass:: WriteType
   :members:

Permissions
^^^^^^^^^^^

.. automodule:: able.permissions
.. automodule:: able
.. autoclass:: Permission
   :members:
   :undoc-members:
   :member-order: bysource


Scan settings
^^^^^^^^^^^^^

.. automodule:: able.scan_settings
.. autoclass:: ScanSettingsBuilder
.. autoclass:: ScanSettings


>>> settings = ScanSettingsBuilder() \
...  .setMatchMode(ScanSettings.MATCH_MODE_AGGRESSIVE) \
...  .setCallbackType(
...     ScanSettings.CALLBACK_TYPE_FIRST_MATCH |
...     ScanSettings.CALLBACK_TYPE_MATCH_LOST
...   )


Scan filters
^^^^^^^^^^^^

.. automodule:: able.filters
   :members:
   :member-order: bysource
   :show-inheritance:


Advertising
^^^^^^^^^^^

.. automodule:: able.advertising

Advertiser
""""""""""
.. autoclass:: Advertiser
   :members:
   :member-order: bysource


Payload
"""""""
.. autoclass:: AdvertiseData

.. autoclass:: DeviceName
   :show-inheritance:
.. autoclass:: TXPowerLevel
   :show-inheritance:
.. autoclass:: ServiceUUID
   :show-inheritance:
.. autoclass:: ServiceData
   :show-inheritance:
.. autoclass:: ManufacturerData
   :show-inheritance:

Constants
"""""""""

.. autoclass:: Interval
   :members:
   :member-order: bysource

.. autoclass:: TXPower
   :members:
   :member-order: bysource

.. autoclass:: Status
   :members:
   :undoc-members:
   :member-order: bysource
