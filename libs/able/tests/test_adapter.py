import pytest

from able.adapter import (
    AdapterManager,
    require_bluetooth_enabled,
    set_adapter_failure_rollback,
)
from able.android.dispatcher import BluetoothDispatcher


@pytest.fixture
def manager(mocker):
    return AdapterManager(mocker.Mock(), ..., [])


def test_operation_executed(mocker, manager):
    operation = mocker.Mock()
    logger = mocker.patch("able.adapter.Logger")

    manager.execute(operation)

    operation.assert_called_once()
    logger.exception.assert_not_called()


def test_operation_failed_as_expected(mocker, manager):
    manager.check_permissions = mocker.Mock(return_value=False)
    expected = Exception("expected")
    operation = mocker.Mock(side_effect=expected)
    logger = mocker.patch("able.adapter.Logger")

    manager.execute(operation)
    operation.assert_not_called()

    manager.check_permissions = mocker.Mock(return_value=True)
    manager.execute_operations()

    operation.assert_called_once()
    logger.exception.assert_called_once_with(expected)


def test_operations_executed(mocker, manager):
    operations = [mocker.Mock(), mocker.Mock()]
    manager.operations = operations.copy()
    manager.check_permissions = mocker.Mock(return_value=False)

    manager.execute_operations()

    # permissions not granted = > suspended
    calls = [operation.call_count for operation in manager.operations]
    assert calls == [0, 0]
    assert manager.operations == operations

    # one more operation requested
    manager.execute(next_operation := mocker.Mock())

    assert [operation.call_count for operation in manager.operations] == [0, 0, 0]
    assert manager.operations == operations + [next_operation]

    manager.check_permissions = mocker.Mock(return_value=True)
    manager.execute_operations()
    assert not manager.operations
    assert [operation.call_count for operation in operations + [next_operation]] == [
        1,
        1,
        1,
    ]


def test_rollback_performed(mocker, manager):
    handlers = [mocker.Mock(), mocker.Mock()]
    operations = [mocker.Mock(), mocker.Mock()]

    manager.operations = operations.copy()
    manager.rollback_handlers = handlers.copy()
    manager.rollback()

    assert not manager.rollback_handlers
    assert not manager.operations
    assert [operation.call_count for operation in operations] == [0, 0]
    assert [operation.call_count for operation in handlers] == [1, 1]
