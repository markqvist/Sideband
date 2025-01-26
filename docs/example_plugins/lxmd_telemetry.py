# This is an LXMd telemetry plugin that
# queries a running LXMF Propagation Node
# for status and statistics.

import RNS

class LXMdTelemetryPlugin(SidebandTelemetryPlugin):
    plugin_name = "lxmd_telemetry"

    def start(self):
        # Do any initialisation work here
        RNS.log("LXMd telemetry plugin starting...")

        # And finally call start on superclass
        super().start()

    def stop(self):
        # Do any teardown work here
        pass

        # And finally call stop on superclass
        super().stop()

    def update_telemetry(self, telemeter):
        if telemeter != None:
            if not "lxmf_propagation" in telemeter.sensors:
                # Create lxmd status sensor if it is not already
                # enabled in the running telemeter instance
                telemeter.enable("lxmf_propagation")

                # Set the identity file used to communicate with
                # the running LXMd instance.
                telemeter.sensors["lxmf_propagation"].set_identity("~/.lxmd/identity")

                # You can also get LXMF Propagation Node stats
                # from an LXMd instance running inside nomadnet
                # telemeter.sensors["lxmf_propagation"].set_identity("~/.nomadnetwork/storage/identity")

# Finally, tell Sideband what class in this
# file is the actual plugin class.
plugin_class = LXMdTelemetryPlugin
