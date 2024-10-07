# This is a bare-minimum command plugin
# example that you can build upon to
# implement your own command plugins.

import RNS

class BasicCommandPlugin(SidebandCommandPlugin):
    command_name = "basic_example"

    def start(self):
        # Do any initialisation work here
        RNS.log("Basic command plugin example starting...")

        # And finally call start on superclass
        super().start()

    def stop(self):
        # Do any teardown work here
        pass

        # And finally call stop on superclass
        super().stop()

    def handle_command(self, arguments, lxm):
        response_content = f"Hello {RNS.prettyhexrep(lxm.source_hash)}. "
        response_content += "This is a response from the basic command example. It doesn't do much, but here is a list of the arguments you included:\n"

        for argument in arguments:
            response_content += f"\n{argument)}"

        # Let the Sideband core send a reply.
        self.get_sideband().send_message(
            response_content,
            lxm.source_hash,
            False,              # Don't use propagation by default, try direct first
            skip_fields = True, # Don't include any additional fields automatically
            no_display = True,  # Don't display this message in the message stream
            attachment = None,  # Don't add any attachment field to this message
            image = None,       # Don't add any image field to this message
            audio = None,       # Don't add any audio field to this message
        )

# Finally, tell Sideband what class in this
# file is the actual plugin class.
plugin_class = BasicCommandPlugin