"""Detect and log Bluetooth adapter state change."""

from typing import Optional

from kivy.logger import Logger
from kivy.uix.widget import Widget

from able import AdapterState, BluetoothDispatcher


class Dispatcher(BluetoothDispatcher):
    def on_bluetooth_adapter_state_change(self, state: int):
        Logger.info(
            f"Bluetoth adapter state changed to {state} ('{AdapterState(state).name}')."
        )
        if state == AdapterState.OFF:
            Logger.info("Adapter state changed to OFF.")


class StateChangeApp(App):
    def build(self):
        Dispatcher()
        return Widget()


if __name__ == "__main__":
    StateChangeApp.run()
