# This plugin provides temperature, humidity
# and pressure data via a BME280 sensor
# connected over I2C. The plugin requires
# the "smbus2" and "RPi.bme280" modules to
# be available on your system. These can be
# installed with:
#
# pip install smbus2 RPi.bme280

import os
import RNS
from importlib.util import find_spec

class BME280Plugin(SidebandTelemetryPlugin):
    plugin_name = "telemetry_bme280"

    I2C_ADDRESS = 0x76
    I2C_BUS     = 1

    # If your BME280 has an offset from the true
    # temperature, you can compensate for this
    # by modifying this parameter.
    TEMPERATURE_CORRECTION = 0.0

    def start(self):
        RNS.log("BME280 telemetry plugin starting...")

        if find_spec("smbus2"): import smbus2
        else: raise OSError(f"No smbus2 module available, cannot start BME280 telemetry plugin")
        
        if find_spec("bme280"): import bme280
        else: raise OSError(f"No bme280 module available, cannot start BME280 telemetry plugin")

        self.sensor_connected = False

        try:
            self.bme280 = bme280
            self.address = self.I2C_ADDRESS
            self.bus = smbus2.SMBus(self.I2C_BUS)
            self.calibration = self.bme280.load_calibration_params(self.bus, self.address)
            self.sensor_connected = True
            self.tc = self.TEMPERATURE_CORRECTION
        
        except Exception as e:
            RNS.log(f"Could not connect to I2C device while starting BME280 telemetry plugin", RNS.LOG_ERROR)
            RNS.log(f"The contained exception was: {e}", RNS.LOG_ERROR)

        super().start()

    def stop(self):
        self.bus.close()
        super().stop()

    def update_telemetry(self, telemeter):
        if telemeter != None:
            if self.sensor_connected:
                try:
                    sample = self.bme280.sample(self.bus, self.address, self.calibration); ts = telemeter.sensors
                    telemeter.synthesize("temperature"); ts["temperature"].data = {"c": round(sample.temperature+self.tc,1)}
                    telemeter.synthesize("humidity");    ts["humidity"].data    = {"percent_relative": round(sample.humidity,1)}
                    telemeter.synthesize("pressure");    ts["pressure"].data    = {"mbar": round(sample.pressure,1)}

                except Exception as e:
                    RNS.log("An error occurred while updating BME280 sensor data", RNS.LOG_ERROR)
                    RNS.log(f"The contained exception was: {e}", RNS.LOG_ERROR)

plugin_class = BME280Plugin