import RNS

class BasicTelemetryPlugin(SidebandTelemetryPlugin):
    plugin_name = "telemetry_example"

    def start(self):
        # Do any initialisation work here
        RNS.log("Basic telemetry plugin example starting...")

        # And finally call start on superclass
        super().start()

    def stop(self):
        # Do any teardown work here
        pass

        # And finally call stop on superclass
        super().stop()

    def update_telemetry(self, telemeter):
        if telemeter != None:
            RNS.log("Updating power sensors")
            telemeter.synthesize("power_consumption")
            telemeter.sensors["power_consumption"].update_consumer(2163.15, type_label="Heater consumption")
            telemeter.sensors["power_consumption"].update_consumer(12.7/1e6, type_label="Receiver consumption")
            telemeter.sensors["power_consumption"].update_consumer(0.055, type_label="LED consumption")
            telemeter.sensors["power_consumption"].update_consumer(982.22*1e9, type_label="Smelter consumption")

            telemeter.synthesize("power_production")
            telemeter.sensors["power_production"].update_producer(5732.15, type_label="Solar production")

# Finally, tell Sideband what class in this
# file is the actual plugin class.
plugin_class = BasicTelemetryPlugin