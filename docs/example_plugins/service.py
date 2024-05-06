# This is a bare-minimum service plugin
# example that you can build upon to
# implement your own service plugins.

import RNS
import time
import threading

class BasicServicePlugin(SidebandServicePlugin):
    service_name = "service_example"

    def service_jobs(self):
        while self.should_run:
            time.sleep(5)
            RNS.log("Service ping from "+str(self))

        RNS.log("Jobs stopped running for "+str(self))

    def start(self):
        # Do any initialisation work here
        RNS.log("Basic service plugin example starting...")
        self.should_run = True
        self.service_thread = threading.Thread(target=self.service_jobs, daemon=True)
        self.service_thread.start()

        # And finally call start on superclass
        super().start()

    def stop(self):
        # Do any teardown work here
        self.should_run = False

        # And finally call stop on superclass
        super().stop()

# Finally, tell Sideband what class in this
# file is the actual plugin class.
plugin_class = BasicServicePlugin