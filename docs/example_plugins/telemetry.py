# This is a basic telemetry plugin
# example that you can build upon to
# implement your own telemetry plugins.

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
            # Create power consumption sensors
            telemeter.synthesize("power_consumption")
            telemeter.sensors["power_consumption"].update_consumer(2163.15, type_label="Heater consumption")
            telemeter.sensors["power_consumption"].update_consumer(12.7/1e6, type_label="Receiver consumption")
            telemeter.sensors["power_consumption"].update_consumer(0.055, type_label="LED consumption", custom_icon="led-on")
            telemeter.sensors["power_consumption"].update_consumer(982.22*1e9, type_label="Smelter consumption")

            # Create power production sensor
            telemeter.synthesize("power_production")
            telemeter.sensors["power_production"].update_producer(5732.15, type_label="Solar production", custom_icon="solar-power-variant")

            # Create storage sensor
            telemeter.synthesize("nvm")
            telemeter.sensors["nvm"].update_entry(capacity=256e9, used=38.48e9, type_label="SSD")

            # Create RAM sensors
            telemeter.synthesize("ram")
            telemeter.sensors["ram"].update_entry(capacity=8e9, used=3.48e9, type_label="RAM")
            telemeter.sensors["ram"].update_entry(capacity=16e9, used=0.72e9, type_label="Swap")

            # Create CPU sensor
            telemeter.synthesize("processor")
            telemeter.sensors["processor"].update_entry(current_load=0.42, clock=2.45e9, load_avgs=[0.27, 0.43, 0.49], type_label="CPU")

            # Create custom sensor
            telemeter.synthesize("custom")
            telemeter.sensors["custom"].update_entry("311 seconds", type_label="Specific impulse is", custom_icon="rocket-launch")
            telemeter.sensors["custom"].update_entry("a lie", type_label="The cake is", custom_icon="cake-variant")

            # Create tank sensors
            telemeter.synthesize("tank")
            telemeter.sensors["tank"].update_entry(capacity=1500, level=728, type_label="Fresh water", custom_icon="cup-water")
            telemeter.sensors["tank"].update_entry(capacity=2000, level=122, unit="L", type_label="Waste tank")

            # Create fuel sensor
            telemeter.synthesize("fuel")
            telemeter.sensors["fuel"].update_entry(capacity=75, level=61)

# Finally, tell Sideband what class in this
# file is the actual plugin class.
plugin_class = BasicTelemetryPlugin
