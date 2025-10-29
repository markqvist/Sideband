import pytest

import able.filters as filters


@pytest.fixture
def java_builder(mocker):
    instance = mocker.Mock()
    mocker.patch("able.filters.ScanFilterBuilder", return_value=instance)
    return instance


def test_filter_builded(java_builder):
    filters.Filter().build()
    assert java_builder.build.call_count == 1


def test_builder_method_called(java_builder):
    f = filters.DeviceNameFilter("test")

    f.build()

    assert java_builder.method_calls == [
        ("setDeviceName", ("test",)),
        ("build", )
    ]


def test_filters_combined(java_builder):
    f = filters.DeviceNameFilter("test") & (
        filters.DeviceAddressFilter("AA:AA:AA:AA:AA:AA") &
        filters.ManufacturerDataFilter("test-id", [1, 2, 3])
    )

    f.build()

    assert java_builder.method_calls == [
        ("setDeviceName", ("test",)),
        ("setDeviceAddress", ("AA:AA:AA:AA:AA:AA",)),
        ("setManufacturerData", ("test-id", [1, 2, 3])),
        ("build", )
    ]


def test_combine_same_type_exception(java_builder):
    with pytest.raises(ValueError, match="cannot combine filters of the same type"):
        f = filters.DeviceNameFilter("test") & (
            filters.DeviceAddressFilter("AA:AA:AA:AA:AA:AA") &
            filters.DeviceNameFilter("test2")
        )
