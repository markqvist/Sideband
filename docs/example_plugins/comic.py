import io
import RNS
import requests
from PIL import Image as PilImage

class ComicCommandPlugin(SidebandCommandPlugin):
    command_name = "comic"

    def start(self):
        # Do any initialisation work here
        RNS.log("Comic command plugin example starting...")

        # And finally call start on superclass
        super().start()

    def stop(self):
        # Do any teardown work here
        pass

        # And finally call stop on superclass
        super().stop()

    def handle_command(self, arguments, lxm):
        comic_source = "https://imgs.xkcd.com/comics/tsp_vs_tbsp.png"
        response_content = f"The source for this comic is:\n{comic_source}"

        try:
            image_request = requests.get(comic_source, stream=True)
            if image_request.status_code == 200:
                max_size = 320, 320
                with PilImage.open(io.BytesIO(image_request.content)) as im:
                    im.thumbnail(max_size)
                    buf = io.BytesIO()
                    im.save(buf, format="webp", quality=22)
                    image_field = ["webp", buf.getvalue()]

                    # Send the fetched comic as a message
                    self.get_sideband().send_message(
                        response_content,
                        lxm.source_hash,
                        False,                # Don't use propagation by default, try direct first
                        skip_fields = True,   # Don't include any additional fields automatically
                        no_display = True,    # Don't display this message in the message stream
                        image = image_field,  # Add the scaled and compressed image
                    )

            else:
                # Send an error message
                self.get_sideband().send_message(
                    "The specified comic could not be downloaded",
                    lxm.source_hash,
                    False,                # Don't use propagation by default, try direct first
                    skip_fields = True,   # Don't include any additional fields automatically
                    no_display = True,    # Don't display this message in the message stream
                )

        except Exception as e:
            # Send an error message
            self.get_sideband().send_message(
                "An error occurred while trying to fetch the specified comic:\n\n"+str(e),
                lxm.source_hash,
                False,                # Don't use propagation by default, try direct first
                skip_fields = True,   # Don't include any additional fields automatically
                no_display = True,    # Don't display this message in the message stream
            )


# Finally, tell Sideband what class in this
# file is the actual plugin class.
plugin_class = ComicCommandPlugin