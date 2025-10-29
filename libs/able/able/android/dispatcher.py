from jnius import JavaException, autoclass
from kivy.logger import Logger

from able.adapter import (
    AdapterManager,
    require_bluetooth_enabled,
    set_adapter_failure_rollback,
)
from able.android.jni import PythonBluetooth
from able.dispatcher import BluetoothDispatcherBase
from able.scan_settings import ScanSettingsBuilder

ArrayList = autoclass("java.util.ArrayList")

try:
    BLE = autoclass("org.able.BLE")
except:
    Logger.error(
        "able_recipe: Failed to load Java class org.able.BLE. Possible build error."
    )
    raise
else:
    Logger.info("able_recipe: org.able.BLE Java class loaded")

BluetoothAdapter = autoclass("android.bluetooth.BluetoothAdapter")
BluetoothDevice = autoclass("android.bluetooth.BluetoothDevice")
BluetoothGattDescriptor = autoclass("android.bluetooth.BluetoothGattDescriptor")

ENABLE_NOTIFICATION_VALUE = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
ENABLE_INDICATION_VALUE = BluetoothGattDescriptor.ENABLE_INDICATION_VALUE
DISABLE_NOTIFICATION_VALUE = BluetoothGattDescriptor.DISABLE_NOTIFICATION_VALUE


class BluetoothDispatcher(BluetoothDispatcherBase):
    @property
    @require_bluetooth_enabled
    def adapter(self):
        return AdapterManager.get_attached_manager(self).adapter

    @property
    def bonded_devices(self):
        ble_types = (BluetoothDevice.DEVICE_TYPE_LE, BluetoothDevice.DEVICE_TYPE_DUAL)
        adapter = self.adapter
        devices = adapter.getBondedDevices().toArray() if adapter else []
        return [dev for dev in devices if dev.getType() in ble_types]

    def _set_ble_interface(self):
        self._events_interface = PythonBluetooth(self)
        self._ble = BLE(self._events_interface)

    @set_adapter_failure_rollback(
        lambda self: self.dispatch("on_scan_started", success=False)
    )
    @require_bluetooth_enabled
    def start_scan(self, filters=None, settings=None):
        filters_array = ArrayList()
        for f in filters or []:
            filters_array.add(f.build())
        if not settings:
            settings = ScanSettingsBuilder()
        try:
            settings = settings.build()
        except AttributeError:
            pass
        self._ble.startScan(self.enable_ble_code, filters_array, settings)

    def stop_scan(self):
        self._ble.stopScan()

    @require_bluetooth_enabled
    def connect_by_device_address(self, address: str, autoconnect: bool = False):
        address = address.upper()
        if not BluetoothAdapter.checkBluetoothAddress(address):
            raise ValueError(f"{address} is not a valid Bluetooth address")
        adapter = self.adapter
        if adapter:
            self.connect_gatt(adapter.getRemoteDevice(address), autoconnect)

    @require_bluetooth_enabled
    def enable_notifications(self, characteristic, enable=True, indication=False):
        if not self.gatt.setCharacteristicNotification(characteristic, enable):
            return False

        if not enable:
            # DISABLE_NOTIFICAITON_VALUE is for disabling
            # both notifications and indications
            descriptor_value = DISABLE_NOTIFICATION_VALUE
        elif indication:
            descriptor_value = ENABLE_INDICATION_VALUE
        else:
            descriptor_value = ENABLE_NOTIFICATION_VALUE

        for descriptor in characteristic.getDescriptors().toArray():
            self.write_descriptor(descriptor, descriptor_value)
        return True

    @require_bluetooth_enabled
    def _start_advertising(self, advertiser):
        advertiser._start()

    @require_bluetooth_enabled
    def _set_name(self, value):
        adapter = self.adapter
        if adapter:
            self.adapter.setName(value)
