from dataclasses import dataclass, field
from functools import partial, wraps
from typing import Optional

from android import activity
from android.permissions import (
    check_permission,
    request_permissions,
)
from jnius import autoclass
from kivy.logger import Logger


Activity = autoclass("android.app.Activity")


def require_bluetooth_enabled(method):
    """Decorator to call `BluetoothDispatcher` method
    when runtime permissions are granted
    and Bluetooth adapter becomes ready.

    Decorator launches system activities that allows the user
    to grant runtime permissions and turn on Bluetooth,
    if Bluetooth is not enabled.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        manager = AdapterManager.get_attached_manager(self)
        if manager:
            return manager.execute(partial(method, self, *args, **kwargs))
        return None

    return wrapper


def set_adapter_failure_rollback(handler):
    """Decorator to launch handler
    if permissions are not granted or adapter is not enabled."""

    def inner(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            manager = AdapterManager.get_attached_manager(self)
            if manager:
                manager.rollback_handlers.append(partial(handler, self))
                return func(self, *args, **kwargs)
            return None

        return wrapper

    return inner


@dataclass
class AdapterManager:
    """
    Class for managing the execution of operations
    that require the BLE adapter.
    Operations are deferred until runtime permissions are granted
    and the BLE adapter is enabled.
    """

    ble: "org.able.BLE"
    enable_ble_code: str
    runtime_permissions: list
    operations: list = field(default_factory=list)
    rollback_handlers: list = field(default_factory=list)
    is_permissions_granted: bool = False
    is_permissions_requested: bool = False
    is_adapter_requested: bool = False

    @property
    def adapter(self) -> Optional["android.bluetooth.BluetoothAdapter"]:
        if self.has_permissions:
            adapter = self.ble.mBluetoothAdapter
            if adapter and adapter.isEnabled():
                return adapter
        return None

    @property
    def has_permissions(self):
        if not self.is_permissions_granted:
            self.is_permissions_granted = self.check_permissions()
        return self.is_permissions_granted

    @property
    def is_service_context(self):
        return not activity._activity

    def __post_init__(self):
        if self.is_service_context:
            self.is_permissions_granted = True
        else:
            activity.bind(on_activity_result=self.on_activity_result)

    @classmethod
    def get_attached_manager(cls, instance):
        manager = getattr(instance, "_adapter_manager", None)
        if not manager:
            Logger.error("BLE adapter manager is not installed")
        return manager

    def install(self, instance):
        setattr(instance, "_adapter_manager", self)

    def check_permissions(self):
        return all(
            [check_permission(permission) for permission in self.runtime_permissions]
        )

    def request_permissions(self):
        if self.is_permissions_requested:
            return
        self.is_permissions_requested = True
        if not self.is_service_context:
            Logger.debug("Request runtime permissions")
            request_permissions(
                self.runtime_permissions,
                self.on_runtime_permissions,
            )
        else:
            Logger.error("Required permissions are not granted for service")

    def request_adapter(self):
        if self.is_adapter_requested:
            return
        self.is_adapter_requested = True
        self.ble.getAdapter(self.enable_ble_code)

    def rollback(self):
        self._execute_operations(self.rollback_handlers)

    def execute(self, operation):
        if self.adapter:
            # execute immediately, if adapter is enabled
            return operation()
        self.operations.append(operation)
        self.execute_operations()

    def execute_operations(self):
        if self.has_permissions:
            if self.adapter:
                self._execute_operations(self.operations)
            else:
                self.request_adapter()
        else:
            self.request_permissions()

    def _execute_operations(self, operations):
        self.operations = []
        self.rollback_handlers = []
        for operation in operations:
            try:
                operation()
            except Exception as exc:
                Logger.exception(exc)

    def on_runtime_permissions(self, permissions, grant_results):
        granted = all(grant_results)
        self.is_permissions_granted = granted
        self.is_permissions_requested = False  # allow future invocations
        if granted:
            Logger.debug("Required permissions are granted")
            self.execute_operations()
        else:
            Logger.error("Required permissions are not granted")
            self.rollback()

    def on_activity_result(self, requestCode, resultCode, intent):
        if requestCode == self.enable_ble_code:
            enabled = resultCode == Activity.RESULT_OK
            self.is_adapter_requested = False  # allow future invocations
            if enabled:
                Logger.debug("BLE adapter is enabled")
                self.execute_operations()
            else:
                Logger.error("BLE adapter is not enabled")
                self.rollback()
