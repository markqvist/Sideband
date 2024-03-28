class SidebandPlugin():
    pass

class SidebandCommandPlugin(SidebandPlugin):
    def __init__(self, sideband_core):
        self.__sideband = sideband_core
        self.__started = False
        self.command_name = type(self).command_name

    def start(self):
        self.__started = True

    def stop(self):
        self.__started = False

    def is_running(self):
        return self.__started == True

    def get_sideband(self):
        return self.__sideband

    def handle_command(self, arguments):
        raise NotImplementedError

class SidebandServicePlugin(SidebandPlugin):
    def __init__(self, sideband_core):
        self.__sideband = sideband_core
        self.__started = False
        self.service_name = type(self).service_name

    def start(self):
        self.__started = True

    def stop(self):
        self.__started = False

    def is_running(self):
        return self.__started == True

    def get_sideband(self):
        return self.__sideband

class SidebandTelemetryPlugin(SidebandPlugin):
    def __init__(self, sideband_core):
        self.__sideband = sideband_core
        self.__started = False
        self.plugin_name = type(self).plugin_name

    def start(self):
        self.__started = True

    def stop(self):
        self.__started = False

    def is_running(self):
        return self.__started == True

    def get_sideband(self):
        return self.__sideband

    def update_telemetry(self, telemeter):
        raise NotImplementedError