from typing import List, Optional

from kivy.event import EventDispatcher
from kivy.logger import Logger

from able import WriteType
from able.adapter import AdapterManager
from able.filters import Filter
from able.permissions import DEFAULT_RUNTIME_PERMISSIONS
from able.queue import BLEQueue, ble_task, ble_task_done
from able.scan_settings import ScanSettingsBuilder
from able.utils import force_convertible_to_java_array


class BLEError:
    """Raise Exception on attribute access"""

    def __init__(self, msg):
        self.msg = msg

    def __getattr__(self, name):
        raise Exception(self.msg)


class BluetoothDispatcherBase(EventDispatcher):
    __events__ = (
        "on_device",
        "on_scan_started",
        "on_scan_completed",
        "on_services",
        "on_connection_state_change",
        "on_bluetooth_adapter_state_change",
        "on_characteristic_changed",
        "on_characteristic_read",
        "on_characteristic_write",
        "on_descriptor_read",
        "on_descriptor_write",
        "on_gatt_release",
        "on_error",
        "on_rssi_updated",
        "on_mtu_changed",
    )
    queue_class = BLEQueue

    def __init__(
        self,
        queue_timeout: float = 0.5,
        enable_ble_code: int = 0xAB1E,
        runtime_permissions: Optional[list[str]] = None,  # DEFAULT_RUNTIME_PERMISSIONS
    ):
        super(BluetoothDispatcherBase, self).__init__()
        self.queue_timeout = queue_timeout
        self.enable_ble_code = enable_ble_code
        self.runtime_permissions = [
            str(permission)
            for permission in (
                runtime_permissions
                if runtime_permissions is not None
                else DEFAULT_RUNTIME_PERMISSIONS
            )
        ]
        self._remote_device_address = None
        self._set_ble_interface()
        self._set_queue()
        self._set_adapter_manager()

    def _set_ble_interface(self):
        self._ble = BLEError("BLE is not implemented for platform")

    def _set_queue(self):
        self.queue = self.queue_class(timeout=self.queue_timeout)

    def _set_adapter_manager(self):
        AdapterManager(
            ble=self._ble,
            enable_ble_code=self.enable_ble_code,
            runtime_permissions=self.runtime_permissions,
        ).install(self)

    def _check_runtime_permissions(self):
        return True

    def _request_runtime_permissions(self):
        pass

    @property
    def adapter(self) -> Optional["android.bluetooth.BluetoothAdapter"]:
        """Local device Bluetooth adapter.
        Could be `None` if adapter is not enabled or access to the adapter is not granted yet.

        :type: `BluetoothAdapter <https://developer.android.com/reference/android/bluetooth/BluetoothAdapter>`_
               `Java object <https://pyjnius.readthedocs.io/en/stable/api.html#jnius.JavaClass>`_
        """

    @property
    def gatt(self):
        """GATT profile of the connected device

        :type: BluetoothGatt Java object
        """
        return self._ble.getGatt()

    @property
    def bonded_devices(self):
        """List of Java `android.bluetooth.BluetoothDevice` objects of paired BLE devices.

        :type: List[BluetoothDevice]
        """
        return []

    @property
    def name(self):
        """Name of the Bluetooth adapter.

        :setter: Set name of the Bluetooth adapter
        :type: Optional[str]
        """
        adapter = self.adapter
        return adapter and adapter.getName()

    @name.setter
    def name(self, value):
        self._set_name(value)

    def _set_name(self, value):
        pass

    def set_queue_timeout(self, timeout):
        """Change the BLE operations queue timeout"""
        self.queue_timeout = timeout
        self.queue.set_timeout(timeout)

    def start_scan(
        self,
        filters: Optional[List[Filter]] = None,
        settings: Optional[ScanSettingsBuilder] = None,
    ):
        """Start a scan for devices.
        The status of the scan start are reported with
        :func:`scan_started <on_scan_started>` event.

        :param filters: list of filters to restrict scan results.
                        Advertising record is considered matching the filters
                        if it matches any of the :class:`able.filters.Filter` in the list.
        :param settings: scan settings
        """
        pass

    def stop_scan(self):
        """Stop the ongoing scan for devices."""
        pass

    def connect_by_device_address(self, address: str, autoconnect: bool = False):
        """Connect to GATT Server of the device with a given Bluetooth hardware address, without scanning.

        :param address: Bluetooth hardware address string in "XX:XX:XX:XX:XX:XX" format
        :param autoconnect: If True, automatically reconnects when available.
                            False = direct connect (default).
        :raises:
            ValueError: if `address` is not a valid Bluetooth address
        """
        pass

    def connect_gatt(self, device, autoconnect: bool = False):
        """Connect to GATT Server hosted by device

        :param device: BluetoothDevice Java object
        :param autoconnect: If True, automatically reconnects when available.
                            False = direct connect (default).
        """
        self._ble.connectGatt(device, autoconnect)

    def close_gatt(self):
        """Close current GATT client"""
        self._ble.closeGatt()

    def discover_services(self):
        """Discovers services offered by a remote device.
        The status of the discovery reported with
        :func:`services <on_services>` event.

        :return: true, if the remote services discovery has been started
        """
        return self.gatt.discoverServices()

    def enable_notifications(self, characteristic, enable=True, indication=False):
        """Enable/disable notifications or indications for a given characteristic

        :param characteristic: BluetoothGattCharacteristic Java object
        :param enable: enable notifications if True, else disable notifications
        :param indication: handle indications instead of notifications
        :return: True, if the operation was initiated successfully
        """
        return True

    @ble_task
    def write_descriptor(self, descriptor, value):
        """Set and write the value of a given descriptor to the associated
        remote device

        :param descriptor: BluetoothGattDescriptor Java object
        :param value: value to write
        """
        if not descriptor.setValue(force_convertible_to_java_array(value)):
            Logger.error("Error on set descriptor value")
            return
        if not self.gatt.writeDescriptor(descriptor):
            Logger.error("Error on descriptor write")

    @ble_task
    def write_characteristic(
        self, characteristic, value, write_type: Optional[WriteType] = None
    ):
        """Write a given characteristic value to the associated remote device

        :param characteristic: BluetoothGattCharacteristic Java object
        :param value: value to write
        :param write_type: specific write type to set for the characteristic
        """
        self._ble.writeCharacteristic(
            characteristic, force_convertible_to_java_array(value), int(write_type or 0)
        )

    @ble_task
    def read_characteristic(self, characteristic):
        """Read a given characteristic from the associated remote device

        :param characteristic: BluetoothGattCharacteristic Java object
        """
        self._ble.readCharacteristic(characteristic)

    @ble_task
    def update_rssi(self):
        """Triggers an update for the RSSI from the associated remote device"""
        self._ble.readRemoteRssi()

    @ble_task
    def request_mtu(self, mtu: int):
        """Request to change the ATT Maximum Transmission Unit value

        :param value: new MTU size
        """
        self.gatt.requestMtu(mtu)

    def on_error(self, msg):
        """Error handler

        :param msg: error message
        """
        self._ble = BLEError(msg)  # Exception for calls from another threads
        raise Exception(msg)

    @ble_task_done
    def on_gatt_release(self):
        """`gatt_release` event handler.
        Event is dispatched at every read/write completed operation
        """
        pass

    def on_scan_started(self, success):
        """`scan_started` event handler

        :param success: true, if scan was started successfully
        """
        pass

    def on_scan_completed(self):
        """`scan_completed` event handler"""
        pass

    def on_device(self, device, rssi, advertisement):
        """`device` event handler.
        Event is dispatched when device is found during a scan.

        :param device: BluetoothDevice Java object
        :param rssi: the RSSI value for the remote device
        :param advertisement: :class:`Advertisement` data record
        """
        pass

    def on_connection_state_change(self, status, state):
        """`connection_state_change` event handler

        :param status: status of the operation,
                       `GATT_SUCCESS` if the operation succeeds
        :param state: STATE_CONNECTED or STATE_DISCONNECTED
        """
        pass

    def on_bluetooth_adapter_state_change(self, state):
        """`bluetooth_adapter_state_change` event handler
            Allows the user to detect when bluetooth adapter is turned on/off.

        :param state: STATE_OFF, STATE_TURNING_OFF, STATE_ON, STATE_TURNING_ON
        """

    def on_services(self, services, status):
        """`services` event handler

        :param services: :class:`Services` dict filled with discovered
                         characteristics
                         (BluetoothGattCharacteristic Java objects)
        :param status: status of the operation,
                       `GATT_SUCCESS` if the operation succeeds
        """
        pass

    def on_characteristic_changed(self, characteristic):
        """`characteristic_changed` event handler

        :param characteristic: BluetoothGattCharacteristic Java object
        """
        pass

    def on_characteristic_read(self, characteristic, status):
        """`characteristic_read` event handler

        :param characteristic: BluetoothGattCharacteristic Java object
        :param status: status of the operation,
                       `GATT_SUCCESS` if the operation succeeds
        """
        pass

    def on_characteristic_write(self, characteristic, status):
        """`characteristic_write` event handler

        :param characteristic: BluetoothGattCharacteristic Java object
        :param status: status of the operation,
                       `GATT_SUCCESS` if the operation succeeds
        """
        pass

    def on_descriptor_read(self, descriptor, status):
        """`descriptor_read` event handler

        :param descriptor: BluetoothGattDescriptor Java object
        :param status: status of the operation,
                       `GATT_SUCCESS` if the operation succeeds
        """
        pass

    def on_descriptor_write(self, descriptor, status):
        """`descriptor_write` event handler

        :param descriptor: BluetoothGattDescriptor Java object
        :param status: status of the operation,
                       `GATT_SUCCESS` if the operation succeeds
        """
        pass

    def on_rssi_updated(self, rssi, status):
        """`onReadRemoteRssi` event handler.
        Event is dispatched at every RSSI update completed operation,
        reporting a RSSI value for a remote device connection.

        :param rssi: integer containing RSSI value in dBm
        :param status: status of the operation,
                       `GATT_SUCCESS` if the operation succeeds
        """
        pass

    def on_mtu_changed(self, mtu, status):
        """`onMtuChanged` event handler
        Event is dispatched when MTU for a remote device has changed,
        reporting a new MTU size.

        :param mtu: integer containing the new MTU size
        :param status: status of the operation,
                       `GATT_SUCCESS` if the MTU has been changed successfully
        """
        pass
