"""Start advertising service."""
from able import BluetoothDispatcher, Permission, require_bluetooth_enabled
from jnius import autoclass
from kivy.app import App
from kivy.lang import Builder


kv = """
BoxLayout:
   Button:
      text: 'Start service'
      on_press: app.ble_dispatcher.start_service()
   Button:
      text: 'Stop service'
      on_press: app.ble_dispatcher.stop_service()
"""


class Dispatcher(BluetoothDispatcher):
    @property
    def service(self):
        return autoclass("test.able.advservice.ServiceAble")

    @property
    def activity(self):
        return autoclass("org.kivy.android.PythonActivity").mActivity

    # Need to turn on the adapter, before service is started
    @require_bluetooth_enabled
    def start_service(self):
        self.service.start(
            self.activity,
            # Pass UUID to advertise
            "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        )
        App.get_running_app().stop()  # Can close the app, service will continue running

    def stop_service(self):
        self.service.stop(self.activity)


class ServiceApp(App):
    def build(self):
        self.ble_dispatcher = Dispatcher(
            # This app does not use device scanning,
            # so the list of required permissions can be reduced
            runtime_permissions=[
                Permission.BLUETOOTH_CONNECT,
                Permission.BLUETOOTH_ADVERTISE,
            ]
        )
        return Builder.load_string(kv)


if __name__ == "__main__":
    ServiceApp().run()
