import pytest

from able.android.dispatcher import BluetoothDispatcher


@pytest.fixture
def ble(mocker):
    mocker.patch("able.android.dispatcher.PythonBluetooth")
    ble = BluetoothDispatcher()
    ble._ble = mocker.Mock()
    ble.on_scan_started = mocker.Mock()
    return ble


def test_adapter_returned(mocker, ble):
    manager = ble._adapter_manager
    manager.check_permissions = mocker.Mock(return_value=False)
    assert not ble.adapter
    assert not ble.adapter

    manager.check_permissions = mocker.Mock(return_value=True)
    assert ble.adapter


def test_start_scan_executed(ble):
    manager = ble._adapter_manager
    assert manager

    ble.start_scan()
    ble._ble.startScan.assert_called_once()


def test_start_scan_failed_as_expected(mocker, ble):
    manager = ble._adapter_manager
    manager.check_permissions = mocker.Mock(return_value=False)

    ble.start_scan()
    ble._ble.startScan.assert_not_called()

    assert len(manager.operations) == 1
    assert len(manager.rollback_handlers) == 1

    manager.on_runtime_permissions(permissions=[...], grant_results=[False])

    ble.on_scan_started.assert_called_once_with(success=False)
    assert len(manager.operations) == 0
    assert len(manager.rollback_handlers) == 0
