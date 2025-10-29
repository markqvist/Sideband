"""BLE advertise operations."""
from abc import abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional, Union

from jnius import JavaException, autoclass
from kivy.event import EventDispatcher

from able.android.dispatcher import BluetoothDispatcher
from able.android.jni import PythonBluetoothAdvertiser
from able.utils import force_convertible_to_java_array


AdvertiseDataBuilder = autoclass('android.bluetooth.le.AdvertiseData$Builder')
AdvertisingSet = autoclass('android.bluetooth.le.AdvertisingSet')
AdvertisingSetParametersBuilder = autoclass('android.bluetooth.le.AdvertisingSetParameters$Builder')
AndroidAdvertiseData = autoclass('android.bluetooth.le.AdvertiseData')
BluetoothLeAdvertiser = autoclass('android.bluetooth.le.BluetoothLeAdvertiser')
ParcelUuid = autoclass('android.os.ParcelUuid')

BLEAdvertiser = autoclass('org.able.BLEAdvertiser')


class Interval(IntEnum):
    """Advertising interval constants.
    https://developer.android.com/reference/android/bluetooth/le/AdvertisingSetParameters#INTERVAL_HIGH
    """
    MIN = 160  #: Minimum value for advertising interval, around every 100ms
    MEDIUM = 400  #: Advertise on medium frequency, around every 250ms
    HIGH = 1600  #: Advertise on low frequency, around every 1000ms
    MAX = 16777215  #: Maximum value for advertising interval


class TXPower(IntEnum):
    """Advertising transmission (TX) power level constants.
    https://developer.android.com/reference/android/bluetooth/le/AdvertisingSetParameters#TX_POWER_HIGH
    """
    MIN = -127  #: Minimum value for TX power
    ULTRA_LOW = -21  #: Advertise using the lowest TX power level
    LOW = -15  #: Advertise using the low TX power level
    MEDIUM = -7  #: Advertise using the medium TX power level
    MAX = 1  #: Maximum value for TX power


class Status:
    """Advertising operation status constants.
    https://developer.android.com/reference/android/bluetooth/le/AdvertisingSetCallback#constants
    """
    SUCCESS = 0
    DATA_TOO_LARGE = 1
    TOO_MANY_ADVERTISERS = 2
    ALREADY_STARTED = 3
    INTERNAL_ERROR = 4
    FEATURE_UNSUPPORTED = 5


@dataclass
class ADStructure:

    @abstractmethod
    def add_payload(self, builder: AdvertiseDataBuilder):
        pass


class DeviceName(ADStructure):
    """Include device name (complete local name) in advertise packet."""

    def add_payload(self, builder):
        builder.setIncludeDeviceName(True)


class TXPowerLevel(ADStructure):
    """Include transmission power level in the advertise packet."""

    def add_payload(self, builder):
        builder.setIncludeTxPowerLevel(True)


@dataclass
class ServiceUUID(ADStructure):
    """Service UUID to advertise.

    :param uid: UUID to be advertised
    """
    uid: str

    def add_payload(self, builder):
        builder.addServiceUuid(
            ParcelUuid.fromString(self.uid)
        )


@dataclass
class ServiceData(ADStructure):
    """Service data to advertise.

    :param uid: UUID of the service the data is associated with
    :param data: Service data
    """

    uid: str
    data: Union[list, tuple, bytes, bytearray]

    def add_payload(self, builder):
        builder.addServiceData(
            ParcelUuid.fromString(self.uid),
                force_convertible_to_java_array(self.data)
        )


@dataclass
class ManufacturerData(ADStructure):
    """Manufacturer specific data to advertise.

    :param id: Manufacturer ID
    :param data: Manufacturer specific data
    """
    id: int
    data: Union[list, tuple, bytes, bytearray]

    def add_payload(self, builder):
        builder.addManufacturerData(
            self.id,
            force_convertible_to_java_array(self.data)
        )


class AdvertiseData:
    """Builder for data payload to be advertised.

    :param payload: List of AD structures to include in advertisement

    >>> AdvertiseData(DeviceName(), ManufacturerData(10, b'specific data'))
    [DeviceName(), ManufacturerData(id=10, data=b'specific data')]
    """

    def __init__(self, *payload: List[ADStructure]):
        self.payload = payload
        self.data = self.build()

    def __repr__(self):
        sections = ", ".join(repr(ad) for ad in self.payload)
        return f"[{sections}]"

    def build(self) -> AndroidAdvertiseData:
        builder = AdvertiseDataBuilder()
        for ad in self.payload:
            ad.add_payload(builder)
        return builder.build()


class Advertiser(EventDispatcher):
    """Base class for BLE advertise operations.

    :param ble: BLE interface instance
    :param data: Advertisement data to be broadcasted
    :param scan_data: Scan response associated with the advertisement data
    :param interval: Advertising interval
                     `<https://developer.android.com/reference/android/bluetooth/le/AdvertisingSetParameters.Builder#setInterval(int)>`_
    :param tx_power: Transmission power level
                     `<https://developer.android.com/reference/android/bluetooth/le/AdvertisingSetParameters.Builder#setTxPowerLevel(int)>`_

    >>> Advertiser(
    ...            ble=BluetoothDispatcher(),
    ...            data=AdvertiseData(DeviceName()),
    ...            scan_data=AdvertiseData(TXPowerLevel()),
    ...            interval=Interval.MIN,
    ...            tx_power=TXPower.MAX
    ... ) #doctest: +ELLIPSIS
    <able.advertising.Advertiser object at 0x...>
    """

    __events__ = (
        'on_advertising_started',
        'on_advertising_stopped',
        'on_advertising_enabled',
        'on_advertising_data_set',
        'on_scan_response_data_set',
        'on_advertising_parameters_updated',
        'on_advertising_set_changed',
    )

    def __init__(
            self,
            ble: BluetoothDispatcher,
            data: AdvertiseData = None,
            scan_data: AdvertiseData = None,
            interval: int = Interval.HIGH,
            tx_power: int = TXPower.MEDIUM,
    ):
        self._ble = ble
        self._data = data
        self._scan_data = scan_data
        self._interval = interval
        self._tx_power = tx_power

        self._events_interface = PythonBluetoothAdvertiser(self)
        self._advertiser = BLEAdvertiser(self._events_interface)
        self._callback_set = self._advertiser.mCallbackSet
        self._advertising_set = None

    @property
    def data(self):
        """
        :setter: Update advertising data
        :type: Optional[AdvertiseData]
        """
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self._update_advertising_set()

    @property
    def scan_data(self):
        """
        :setter: Update the scan response
        :type: Optional[AdvertiseData]
        """
        return self._scan_data

    @scan_data.setter
    def scan_data(self, value):
        self._scan_data = value
        self._update_advertising_set()

    @property
    def interval(self):
        """
        :setter: Update the advertising interval
        :type: int
        """
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = value
        self._update_advertising_set()

    @property
    def tx_power(self):
        """
        :setter: Update the transmission power level
        :type: int
        """
        return self._tx_power

    @tx_power.setter
    def tx_power(self, value):
        self._tx_power = value
        self._update_advertising_set()

    @property
    def bluetooth_le_advertiser(self) -> Optional[BluetoothLeAdvertiser]:
        adapter = self._ble.adapter
        return adapter and adapter.getBluetoothLeAdvertiser()

    @property
    def parameters(self) -> AdvertisingSetParametersBuilder:
        builder = AdvertisingSetParametersBuilder()
        builder.setLegacyMode(True) \
               .setConnectable(False) \
               .setScannable(True) \
               .setInterval(self._interval) \
               .setTxPowerLevel(self._tx_power)
        return builder.build()

    def start(self):
        """Start advertising.

        Start a system activity that allows the user to turn on Bluetooth if Bluetooth is not enabled.
        """
        if not self._advertising_set:
            self._ble._start_advertising(self)

    def stop(self):
        """Stop advertising."""
        advertiser = self.bluetooth_le_advertiser
        if advertiser:
            advertiser.stopAdvertisingSet(self._callback_set)

    def on_advertising_started(self, advertising_set: AdvertisingSet, tx_power: int, status: Status):
        """Handler for advertising start operation (onAdvertisingSetStarted).
        """

    def on_advertising_stopped(self, advertising_set: AdvertisingSet):
        """Handler for advertising stop operation (onAdvertisingSetStopped)."""

    def on_advertising_enabled(self, advertising_set: AdvertisingSet, enable: bool, status: Status):
        """Handler for advertising enable/disable operation (onAdvertisingEnabled)."""

    def on_advertising_data_set(self, advertising_set: AdvertisingSet, status: Status):
        """Handler for data set operation (onAdvertisingDataSet)."""

    def on_scan_response_data_set(self, advertising_set: AdvertisingSet, status: Status):
        """Handler for scan response data set operation (onScanResponseDataSet)."""

    def on_advertising_parameters_updated(self, advertising_set: AdvertisingSet, tx_power: int, status: Status):
        """Handler for parameters set operation (onAdvertisingParametersUpdated)."""

    def on_advertising_set_changed(self, advertising_set):
        self._advertising_set = advertising_set

    def _start(self):
        advertiser = self.bluetooth_le_advertiser
        if advertiser:
            self._callback_set = self._advertiser.createCallback()
            try:
                advertiser.startAdvertisingSet(
                    self.parameters,
                    self._data and self._data.data,
                    self._scan_data and self._scan_data.data,
                    None,  # periodicParameters
                    None,  # periodicData
                    self._callback_set
                )
            except JavaException as exc:
                if exc.classname == 'java.lang.IllegalArgumentException' and \
                   exc.innermessage.endswith('data too big'):
                    self.dispatch('on_advertising_started', None, 0, Status.DATA_TOO_LARGE)
                raise

    def _update_advertising_set(self):
        advertising_set = self._advertising_set
        if advertising_set:
            advertising_set.setAdvertisingParameters(self.parameters)
            advertising_set.setScanResponseData(self._scan_data and self._scan_data.data)
            advertising_set.setAdvertisingData(self._data and self._data.data)
