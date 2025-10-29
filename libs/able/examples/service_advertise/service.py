"""Service to advertise data, while not stopped."""
import time
from os import environ

from able import BluetoothDispatcher
from able.advertising import (
    Advertiser,
    AdvertiseData,
    ServiceUUID,
)


def main():
    uuid = environ.get(
        "PYTHON_SERVICE_ARGUMENT",
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    )
    advertiser = Advertiser(
        ble=BluetoothDispatcher(),
        data=AdvertiseData(ServiceUUID(uuid)),
    )
    advertiser.start()
    while True:
        time.sleep(0xDEAD)


if __name__ == "__main__":
    main()
