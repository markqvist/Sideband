import RNS
import os
import sys
import time

from LXST._version import __version__
from LXST.Primitives.Telephony import Telephone
from RNS.vendor.configobj import ConfigObj

class ReticulumTelephone():
    STATE_AVAILABLE  = 0x00
    STATE_CONNECTING = 0x01
    STATE_RINGING    = 0x02
    STATE_IN_CALL    = 0x03

    HW_SLEEP_TIMEOUT = 15
    HW_STATE_IDLE    = 0x00
    HW_STATE_DIAL    = 0x01
    HW_STATE_SLEEP   = 0xFF

    RING_TIME        = 30
    WAIT_TIME        = 60
    PATH_TIME        = 10

    def __init__(self, identity, owner = None, service = False, speaker=None, microphone=None, ringer=None):
        self.identity          = identity
        self.service           = service
        self.owner             = owner
        self.config            = None
        self.should_run        = False
        self.telephone         = None
        self.state             = self.STATE_AVAILABLE
        self.hw_state          = self.HW_STATE_IDLE
        self.hw_last_event     = time.time()
        self.hw_input          = ""
        self.direction         = None
        self.last_input        = None
        self.first_run         = False
        self.ringtone_path     = None
        self.speaker_device    = speaker
        self.microphone_device = microphone
        self.ringer_device     = ringer
        self.phonebook         = {}
        self.aliases           = {}
        self.names             = {}
        
        self.telephone  = Telephone(self.identity, ring_time=self.RING_TIME, wait_time=self.WAIT_TIME)
        self.telephone.set_ringing_callback(self.ringing)
        self.telephone.set_established_callback(self.call_established)
        self.telephone.set_ended_callback(self.call_ended)
        self.telephone.set_speaker(self.speaker_device)
        self.telephone.set_microphone(self.microphone_device)
        self.telephone.set_ringer(self.ringer_device)
        self.telephone.set_allowed(self.__is_allowed)
        RNS.log(f"{self} initialised", RNS.LOG_DEBUG)

    def set_ringtone(self, ringtone_path):
        if os.path.isfile(ringtone_path):
            self.ringtone_path = ringtone_path
            self.telephone.set_ringtone(self.ringtone_path)

    def set_speaker(self, device):
        self.speaker_device = device
        self.telephone.set_speaker(self.speaker_device)

    def set_microphone(self, device):
        self.microphone_device = device
        self.telephone.set_microphone(self.microphone_device)

    def set_ringer(self, device):
        self.ringer_device = device
        self.telephone.set_ringer(self.ringer_device)

    def announce(self, attached_interface=None):
        self.telephone.announce(attached_interface=attached_interface)

    @property
    def is_available(self):
        return self.state == self.STATE_AVAILABLE

    @property
    def is_in_call(self):
        return self.state == self.STATE_IN_CALL

    @property
    def is_ringing(self):
        return self.state == self.STATE_RINGING

    @property
    def call_is_connecting(self):
        return self.state == self.STATE_CONNECTING

    @property
    def hw_is_idle(self):
        return self.hw_state == self.HW_STATE_IDLE

    @property
    def hw_is_dialing(self):
        return self.hw_state == self.HW_STATE_DIAL

    def start(self):
        if not self.should_run:
            self.should_run = True
            self.run()

    def stop(self):
        self.should_run = False
        self.telephone.teardown()
        self.telephone = None

    def hangup(self): self.telephone.hangup()
    def answer(self): self.telephone.answer(self.caller)
    def set_busy(self, busy): self.telephone.set_busy(busy)

    def dial(self, identity_hash):
        self.last_dialled_identity_hash = identity_hash
        destination_hash = RNS.Destination.hash_from_name_and_identity("lxst.telephony", identity_hash)
        if RNS.Transport.has_path(destination_hash):
            call_hops = RNS.Transport.hops_to(destination_hash)
            cs = "" if call_hops == 1 else "s"
            RNS.log(f"Connecting call over {call_hops} hop{cs}...", RNS.LOG_DEBUG)
            identity = RNS.Identity.recall(destination_hash)
            self.call(identity)
        else:
            return "no_path"

    def redial(self, args=None):
        if self.last_dialled_identity_hash: self.dial(self.last_dialled_identity_hash)

    def call(self, remote_identity):
        RNS.log(f"Calling {RNS.prettyhexrep(remote_identity.hash)}...", RNS.LOG_DEBUG)
        self.state = self.STATE_CONNECTING
        self.caller = remote_identity
        self.direction = "to"
        self.telephone.call(self.caller)

    def ringing(self, remote_identity):
        if self.hw_state == self.HW_STATE_SLEEP: self.hw_state = self.HW_STATE_IDLE
        self.state = self.STATE_RINGING
        self.caller  = remote_identity
        self.direction = "from" if self.direction == None else "to"
        RNS.log(f"Incoming call from {RNS.prettyhexrep(self.caller.hash)}", RNS.LOG_DEBUG)
        if self.owner:
            self.owner.incoming_call(remote_identity)

    def call_ended(self, remote_identity):
        if self.is_in_call or self.is_ringing or self.call_is_connecting:
            if self.is_in_call:         RNS.log(f"Call with {RNS.prettyhexrep(self.caller.hash)} ended\n", RNS.LOG_DEBUG)
            if self.is_ringing:         RNS.log(f"Call {self.direction} {RNS.prettyhexrep(self.caller.hash)} was not answered\n", RNS.LOG_DEBUG)
            if self.call_is_connecting: RNS.log(f"Call to {RNS.prettyhexrep(self.caller.hash)} could not be connected\n", RNS.LOG_DEBUG)
            self.direction = None
            self.state = self.STATE_AVAILABLE

    def call_established(self, remote_identity):
        if self.call_is_connecting or self.is_ringing:
            self.state = self.STATE_IN_CALL
            RNS.log(f"Call established with {RNS.prettyhexrep(self.caller.hash)}", RNS.LOG_DEBUG)

    def __is_allowed(self, identity_hash):
        if self.owner.config["voice_trusted_only"]:
            return self.owner.voice_is_trusted(identity_hash)
        else: return True

    def __spin(self, until=None, msg=None, timeout=None):
        if msg: RNS.log(msg, RNS.LOG_DEBUG)
        if timeout != None: timeout = time.time()+timeout
        while (timeout == None or time.time()<timeout) and not until(): time.sleep(0.1)
        if timeout != None and time.time() > timeout:
            return False
        else:
            return True
