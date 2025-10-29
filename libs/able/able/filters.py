"""BLE scanning filters,
wrappers for Java class `android.bluetooth.le.ScanFilter.Builder`
https://developer.android.com/reference/android/bluetooth/le/ScanFilter.Builder
"""
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Union
import uuid

from jnius import autoclass

ParcelUuid = autoclass('android.os.ParcelUuid')
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
ScanFilter = autoclass('android.bluetooth.le.ScanFilter')
ScanFilterBuilder = autoclass('android.bluetooth.le.ScanFilter$Builder')


@dataclass
class Filter:
    """Base class for BLE scanning fiters.

    >>> # Filters of different kinds could be ANDed to set multiple conditions.
    >>> # Both device name and address required:
    >>> combined_filter = DeviceNameFilter("Example") & DeviceAddressFilter("01:02:03:AB:CD:EF")

    >>> DeviceNameFilter("Example1") & DeviceNameFilter("Example2")
    Traceback (most recent call last):
    ValueError: cannot combine filters of the same type
    """

    def __post_init__(self):
        self.filters = [self]

    def __and__(self, other):
        if type(self) in (type(f) for f in other.filters):
            raise ValueError('cannot combine filters of the same type')
        self.filters.extend(other.filters)
        return self

    def build(self):
        builder = ScanFilterBuilder()
        for scan_filter in self.filters:
            scan_filter.filter(builder)
        return builder.build()

    @abstractmethod
    def filter(self, builder):
        pass


class EmptyFilter(Filter):
    """Filter with no restrictions."""

    def filter(self, builder):
        pass


@dataclass
class DeviceAddressFilter(Filter):
    """Set filter on device address.
    Uses Java method `ScanFilter.Builder.setDeviceAddress`.

    :param address: Address in the format of "01:02:03:AB:CD:EF"

    >>> DeviceAddressFilter("01:02:03:AB:CD:EF")
    DeviceAddressFilter(address='01:02:03:AB:CD:EF')
    """
    address: str

    def __post_init__(self):
        super().__post_init__()
        if not BluetoothAdapter.checkBluetoothAddress(str(self.address)):
            raise ValueError(f"{self.address} is not a valid Bluetooth address")

    def filter(self, builder):
        builder.setDeviceAddress(str(self.address))


@dataclass
class DeviceNameFilter(Filter):
    """Set filter on device name.
    Uses Java method `ScanFilter.Builder.setDeviceName`.

    :param name: Device name
    """
    name: str

    def filter(self, builder):
        builder.setDeviceName(str(self.name))


@dataclass
class ManufacturerDataFilter(Filter):
    """Set filter on manufacture data.
    Uses Java method `ScanFilter.Builder.setManufacturerData`.

    :param id: Manufacturer ID
    :param data: Manufacturer specific data
    :param mask: bit mask for partial filtration of the `data`. For any bit in the mask,
                 set it to 1 if it needs to match the one in manufacturer data,
                 otherwise set it to 0 to ignore that bit.


    >>> # Filter by just ID, ignoring the data:
    >>> ManufacturerDataFilter(0x0AD0, [])
    ManufacturerDataFilter(id=2768, data=[], mask=None)

    >>> ManufacturerDataFilter(0x0AD0, [0x2, 0x15, 0x8d])
    ManufacturerDataFilter(id=2768, data=[2, 21, 141], mask=None)

    >>> # With mask set to ignore the second data byte:
    >>> ManufacturerDataFilter(0x0AD0, [0x2, 0, 0x8d], [0xff, 0, 0xff])
    ManufacturerDataFilter(id=2768, data=[2, 0, 141], mask=[255, 0, 255])

    >>> ManufacturerDataFilter(0x0AD0, [0x2, 21, 0x8d], [0xff])
    Traceback (most recent call last):
    ValueError: mask is shorter than the data
    """
    id: int
    data: Union[list, tuple, bytes, bytearray]
    mask: List[int] = field(default_factory=lambda: None)

    def __post_init__(self):
        super().__post_init__()
        if self.mask and len(self.mask) < len(self.data):
            raise ValueError('mask is shorter than the data')

    def filter(self, builder):
        if self.mask:
            builder.setManufacturerData(self.id, self.data, self.mask)
        else:
            builder.setManufacturerData(self.id, self.data)


@dataclass
class ServiceDataFilter(Filter):
    """Set filter on service data.
    Uses Java method `ScanFilter.Builder.setServiceData`.

    :param uid: UUID of the service in the format of
                "0000180f-0000-1000-8000-00805f9b34fb"
    :param data: service data
    :param mask: bit mask for partial filtration of the `data`. For any bit in the mask,
                 set it to 1 if it needs to match the one in service data,
                 otherwise set it to 0 to ignore that bit.

    >>> ServiceDataFilter("0000180f-0000-1000-8000-00805f9b34fb", [])
    ServiceDataFilter(uid='0000180f-0000-1000-8000-00805f9b34fb', data=[], mask=None)

    >>> # With mask set to ignore the first data byte:
    >>> ServiceDataFilter("0000180f-0000-1000-8000-00805f9b34fb", [0, 0x11], [0, 0xff])
    ServiceDataFilter(uid='0000180f-0000-1000-8000-00805f9b34fb', data=[0, 17], mask=[0, 255])

    >>> ServiceDataFilter("0000180f", [])
    Traceback (most recent call last):
    ValueError: badly formed hexadecimal UUID string

    >>> ServiceDataFilter("0000180f-0000-1000-8000-00805f9b34fb", [0x12, 0x34], [0xff])
    Traceback (most recent call last):
    ValueError: mask is shorter than the data
    """
    uid: str
    data: Union[list, tuple, bytes, bytearray]
    mask: List[int] = field(default_factory=lambda: None)

    def __post_init__(self):
        super().__post_init__()
        # validate UUID value
        uuid.UUID(self.uid)
        if self.mask and len(self.mask) < len(self.data):
            raise ValueError('mask is shorter than the data')

    def filter(self, builder):
        uid = ParcelUuid.fromString(self.uid)
        if self.mask:
            builder.setServiceData(uid, self.data, self.mask)
        else:
            builder.setServiceData(uid, self.data)


@dataclass
class ServiceSolicitationFilter(Filter):
    """Set filter on service solicitation uuid.
    Uses Java method `ScanFilter.Builder.setServiceSolicitation`.

    :param uid: UUID of the service in the format of
                "0000180f-0000-1000-8000-00805f9b34fb"
    """
    uid: str

    def filter(self, builder):
        uid = ParcelUuid.fromString(self.uid)
        builder.setServiceSolicitation(uid)


@dataclass
class ServiceUUIDFilter(Filter):
    """Set filter on service uuid.
    Uses Java method `ScanFilter.Builder.setServiceUuid`.

    :param uid: UUID of the service in the format of
                "0000180f-0000-1000-8000-00805f9b34fb"
    :mask: bit mask for partial filtration of the UUID, in the format of
           "ffffffff-0000-0000-0000-ffffffffffff". Set any bit in the mask
           to 1 to indicate a match is needed for the bit in `uid`,
           and 0 to ignore that bit.

    >>> ServiceUUIDFilter('16fe0d00-c111-11e3-b8c8-0002a5d5c51b')
    ServiceUUIDFilter(uid='16fe0d00-c111-11e3-b8c8-0002a5d5c51b', mask=None)

    >>> ServiceUUIDFilter(
    ... '16fe0d00-c111-11e3-b8c8-0002a5d5c51b',
    ... 'ffffffff-0000-0000-0000-000000000000'
    ... )  #doctest: +ELLIPSIS
    ServiceUUIDFilter(uid='16fe0d00-...', mask='ffffffff-...')

    >>> ServiceUUIDFilter('123')
    Traceback (most recent call last):
    ValueError: badly formed hexadecimal UUID string
    """
    uid: str
    mask: str = None

    def __post_init__(self):
        super().__post_init__()
        # validate UUID values
        uuid.UUID(self.uid)
        if self.mask:
            uuid.UUID(self.mask)

    def filter(self, builder):
        uid = ParcelUuid.fromString(self.uid)
        if self.mask:
            mask = ParcelUuid.fromString(self.mask)
            builder.setServiceUuid(uid, mask)
        else:
            builder.setServiceUuid(uid)
