import time

class sidebandservice():

    def __init__(self):
        print("Sideband Service created")
        self.run()

    def run(self):
        while True:
            print("Service ping")
            time.sleep(3)

sbs = sidebandservice()