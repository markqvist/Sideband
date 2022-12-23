import RNS
import LXMF
import threading
import plyer
import os.path
import time
import sqlite3
import random

import RNS.vendor.umsgpack as msgpack
import RNS.Interfaces.Interface as Interface

from .res import sideband_fb_data

if RNS.vendor.platformutils.get_platform() == "android":
    from jnius import autoclass, cast

class PropagationNodeDetector():
    EMITTED_DELTA_GRACE = 300
    EMITTED_DELTA_IGNORE = 10

    aspect_filter = "lxmf.propagation"

    def received_announce(self, destination_hash, announced_identity, app_data):
        try:
            if app_data != None and len(app_data) > 0:
                unpacked = msgpack.unpackb(app_data)
                node_active = unpacked[0]
                emitted = unpacked[1]
                hops = RNS.Transport.hops_to(destination_hash)

                age = time.time() - emitted
                if age < 0:
                    RNS.log("Warning, propagation node announce emitted in the future, possible timing inconsistency or tampering attempt.")
                    if age < -1*PropagationNodeDetector.EMITTED_DELTA_GRACE:
                        raise ValueError("Announce timestamp too far in the future, discarding it")

                if age > -1*PropagationNodeDetector.EMITTED_DELTA_IGNORE:
                    # age = 0
                    pass

                RNS.log("Detected active propagation node "+RNS.prettyhexrep(destination_hash)+" emission "+str(age)+" seconds ago, "+str(hops)+" hops away")
                self.owner.log_announce(destination_hash, RNS.prettyhexrep(destination_hash).encode("utf-8"), dest_type=PropagationNodeDetector.aspect_filter)

                if self.owner.config["lxmf_propagation_node"] == None:
                    if self.owner.active_propagation_node == None:
                        self.owner.set_active_propagation_node(destination_hash)
                    else:
                        prev_hops = RNS.Transport.hops_to(self.owner.active_propagation_node)
                        if hops <= prev_hops:
                            self.owner.set_active_propagation_node(destination_hash)
                        else:
                            pass
                else:
                    pass

        except Exception as e:
            RNS.log("Error while processing received propagation node announce: "+str(e))

    def __init__(self, owner):
        self.owner = owner
        self.owner_app = owner.owner_app

class SidebandCore():
    CONV_P2P       = 0x01
    CONV_GROUP     = 0x02
    CONV_BROADCAST = 0x03

    MAX_ANNOUNCES  = 24

    SERVICE_JOB_INTERVAL   = 1
    PERIODIC_JOBS_INTERVAL = 60
    PERIODIC_SYNC_RETRY = 360

    IF_CHANGE_ANNOUNCE_MIN_INTERVAL = 6    # In seconds
    AUTO_ANNOUNCE_RANDOM_MIN        = 90   # In minutes
    AUTO_ANNOUNCE_RANDOM_MAX        = 480  # In minutes

    aspect_filter = "lxmf.delivery"
    def received_announce(self, destination_hash, announced_identity, app_data):
        # Add the announce to the directory announce
        # stream logger
        self.log_announce(destination_hash, app_data, dest_type=SidebandCore.aspect_filter)

    def __init__(self, owner_app, is_service=False, is_client=False, android_app_dir=None, verbose=False):
        self.is_service = is_service
        self.is_client = is_client
        self.db = None

        if not self.is_service and not self.is_client:
            self.is_standalone = True
        else:
            self.is_standalone = False

        self.log_verbose = verbose
        self.owner_app = owner_app
        self.reticulum = None

        self.app_dir       = plyer.storagepath.get_home_dir()+"/.config/sideband"
        if self.app_dir.startswith("file://"):
            self.app_dir   = self.app_dir.replace("file://", "")
        
        self.rns_configdir = None
        if RNS.vendor.platformutils.is_android():
            self.app_dir = android_app_dir+"/io.unsigned.sideband/files/"
            self.rns_configdir = self.app_dir+"/app_storage/reticulum"
            self.asset_dir     = self.app_dir+"/app/assets"
        elif RNS.vendor.platformutils.is_darwin():
            core_path          = os.path.abspath(__file__)
            self.asset_dir     = core_path.replace("/sideband/core.py", "/assets")
        elif RNS.vendor.platformutils.get_platform() == "linux":
            core_path          = os.path.abspath(__file__)
            self.asset_dir     = core_path.replace("/sideband/core.py", "/assets")
        else:
            self.asset_dir     = plyer.storagepath.get_application_dir()+"/sbapp/assets"

        self.icon              = self.asset_dir+"/icon.png"
        self.icon_48           = self.asset_dir+"/icon_48.png"
        self.icon_32           = self.asset_dir+"/icon_32.png"
        self.icon_macos        = self.asset_dir+"/icon_macos.png"
        self.notification_icon = self.asset_dir+"/notification_icon.png"

        if not os.path.isdir(self.app_dir+"/app_storage"):
            os.makedirs(self.app_dir+"/app_storage")

        self.config_path   = self.app_dir+"/app_storage/sideband_config"
        self.identity_path = self.app_dir+"/app_storage/primary_identity"
        self.db_path       = self.app_dir+"/app_storage/sideband.db"
        self.lxmf_storage  = self.app_dir+"/app_storage/"
        self.log_dir       = self.app_dir+"/app_storage/"
        self.tmp_dir       = self.app_dir+"/app_storage/tmp"
        self.exports_dir   = self.app_dir+"/exports"
        
        self.first_run     = True
        self.saving_configuration = False
        self.last_lxmf_announce = 0
        self.last_if_change_announce = 0
        self.next_auto_announce = time.time() + 60*(random.random()*(SidebandCore.AUTO_ANNOUNCE_RANDOM_MAX-SidebandCore.AUTO_ANNOUNCE_RANDOM_MIN))

        self.getstate_cache = {}

        try:
            if not os.path.isfile(self.config_path):
                self.__init_config()
            else:
                self.__load_config()
                self.first_run = False

            if self.config["debug"]:
                self.log_verbose = True

            if not os.path.isdir(self.tmp_dir):
                os.makedirs(self.tmp_dir)
            else:
                self.clear_tmp_dir()

            if os.path.isdir(self.exports_dir):
                self.clear_exports_dir()
                
        except Exception as e:
            RNS.log("Error while configuring Sideband: "+str(e), RNS.LOG_ERROR)

        # Initialise Reticulum configuration
        if RNS.vendor.platformutils.get_platform() == "android":
            try:
                self.rns_configdir = self.app_dir+"/app_storage/reticulum"
                if not os.path.isdir(self.rns_configdir):
                    os.makedirs(self.rns_configdir)

                RNS.log("Configuring Reticulum instance...")
                if self.config["connect_transport"]:
                    RNS.log("Enabling Reticulum Transport")
                    generated_config = rns_config.replace("TRANSPORT_IS_ENABLED", "Yes")
                else:
                    RNS.log("Not enabling Reticulum Transport")
                    generated_config = rns_config.replace("TRANSPORT_IS_ENABLED", "No")


                config_file = open(self.rns_configdir+"/config", "wb")
                config_file.write(generated_config.encode("utf-8"))
                config_file.close()

            except Exception as e:
                RNS.log("Error while configuring Reticulum instance: "+str(e), RNS.LOG_ERROR)
        
        else:
            pass

        self.active_propagation_node = None
        self.propagation_detector = PropagationNodeDetector(self)

        RNS.Transport.register_announce_handler(self)
        RNS.Transport.register_announce_handler(self.propagation_detector)

    def clear_tmp_dir(self):
        if os.path.isdir(self.tmp_dir):
            for file in os.listdir(self.tmp_dir):
                fpath = self.tmp_dir+"/"+file
                os.unlink(fpath)

    def clear_exports_dir(self):
        if os.path.isdir(self.exports_dir):
            for file in os.listdir(self.exports_dir):
                fpath = self.exports_dir+"/"+file
                RNS.log("Clearing "+str(fpath))
                os.unlink(fpath)

    def __init_config(self):
        RNS.log("Creating new Sideband configuration...")
        if os.path.isfile(self.identity_path):
            self.identity = RNS.Identity.from_file(self.identity_path)
        else:
            self.identity = RNS.Identity()
            self.identity.to_file(self.identity_path)

        self.config = {}
        # Settings
        self.config["debug"] = False
        self.config["display_name"] = "Anonymous Peer"
        self.config["notifications_on"] = True
        self.config["dark_ui"] = False
        self.config["start_announce"] = True
        self.config["propagation_by_default"] = False
        self.config["home_node_as_broadcast_repeater"] = False
        self.config["send_telemetry_to_home_node"] = False
        self.config["lxmf_propagation_node"] = None
        self.config["lxmf_sync_limit"] = None
        self.config["lxmf_sync_max"] = 3
        self.config["lxmf_periodic_sync"] = False
        self.config["lxmf_sync_interval"] = 43200
        self.config["last_lxmf_propagation_node"] = None
        self.config["nn_home_node"] = None
        self.config["print_command"] = "lp"

        # Connectivity
        self.config["connect_transport"] = False
        self.config["connect_local"] = True
        self.config["connect_local_groupid"] = ""
        self.config["connect_local_ifac_netname"] = ""
        self.config["connect_local_ifac_passphrase"] = ""
        self.config["connect_tcp"] = False
        self.config["connect_tcp_host"] = "sideband.connect.reticulum.network"
        self.config["connect_tcp_port"] = "7822"
        self.config["connect_tcp_ifac_netname"] = ""
        self.config["connect_tcp_ifac_passphrase"] = ""
        self.config["connect_i2p"] = False
        self.config["connect_i2p_b32"] = "pmlm3l5rpympihoy2o5ago43kluei2jjjzsalcuiuylbve3mwi2a.b32.i2p"
        self.config["connect_i2p_ifac_netname"] = ""
        self.config["connect_i2p_ifac_passphrase"] = ""
        self.config["connect_rnode"] = False
        self.config["connect_rnode_ifac_netname"] = ""
        self.config["connect_rnode_ifac_passphrase"] = ""
        self.config["connect_serial"] = False
        self.config["connect_serial_ifac_netname"] = ""
        self.config["connect_serial_ifac_passphrase"] = ""
        self.config["connect_modem"] = False
        self.config["connect_modem_ifac_netname"] = ""
        self.config["connect_modem_ifac_passphrase"] = ""
        self.config["connect_ifmode_local"] = "full"
        self.config["connect_ifmode_tcp"] = "full"
        self.config["connect_ifmode_i2p"] = "full"
        self.config["connect_ifmode_rnode"] = "full"
        self.config["connect_ifmode_modem"] = "full"
        self.config["connect_ifmode_serial"] = "full"
        self.config["connect_ifmode_bluetooth"] = "full"
        # Hardware
        self.config["hw_rnode_frequency"] = None
        self.config["hw_rnode_modulation"] = "LoRa"
        self.config["hw_rnode_bandwidth"] = 62500
        self.config["hw_rnode_spreading_factor"] = 8
        self.config["hw_rnode_coding_rate"] = 6
        self.config["hw_rnode_tx_power"] = 0
        self.config["hw_rnode_beaconinterval"] = None
        self.config["hw_rnode_beacondata"] = None
        self.config["hw_rnode_bt_device"] = None
        self.config["hw_rnode_bluetooth"] = False
        self.config["hw_modem_baudrate"] = 57600
        self.config["hw_modem_databits"] = 8
        self.config["hw_modem_stopbits"] = 1
        self.config["hw_modem_parity"] = "none"
        self.config["hw_modem_preamble"] = 150
        self.config["hw_modem_tail"] = 20
        self.config["hw_modem_persistence"] = 220
        self.config["hw_modem_slottime"] = 20
        self.config["hw_modem_beaconinterval"] = None
        self.config["hw_modem_beacondata"] = None
        self.config["hw_serial_baudrate"] = 57600
        self.config["hw_serial_databits"] = 8
        self.config["hw_serial_stopbits"] = 1
        self.config["hw_serial_parity"] = "none"

        if not os.path.isfile(self.db_path):
            self.__db_init()
        else:
            self._db_initstate()
            self._db_initpersistent()

        self.__save_config()

    def should_persist_data(self):
        if self.reticulum != None:
            self.reticulum._should_persist_data()

        self.save_configuration()

    def __load_config(self):
        RNS.log("Loading Sideband identity...", RNS.LOG_DEBUG)
        self.identity = RNS.Identity.from_file(self.identity_path)

        RNS.log("Loading Sideband configuration... "+str(self.config_path), RNS.LOG_DEBUG)
        config_file = open(self.config_path, "rb")
        self.config = msgpack.unpackb(config_file.read())
        config_file.close()

        # Migration actions from earlier config formats
        if not "debug" in self.config:
            self.config["debug"] = False
        if not "dark_ui" in self.config:
            self.config["dark_ui"] = True
        if not "lxmf_periodic_sync" in self.config:
            self.config["lxmf_periodic_sync"] = False
        if not "lxmf_sync_interval" in self.config:
            self.config["lxmf_sync_interval"] = 43200
        if not "notifications_on" in self.config:
            self.config["notifications_on"] = True
        if not "print_command" in self.config:
            self.config["print_command"] = "lp"

        if not "connect_transport" in self.config:
            self.config["connect_transport"] = False
        if not "connect_rnode" in self.config:
            self.config["connect_rnode"] = False
        if not "connect_rnode_ifac_netname" in self.config:
            self.config["connect_rnode_ifac_netname"] = ""
        if not "connect_rnode_ifac_passphrase" in self.config:
            self.config["connect_rnode_ifac_passphrase"] = ""
        if not "connect_serial" in self.config:
            self.config["connect_serial"] = False
        if not "connect_serial_ifac_netname" in self.config:
            self.config["connect_serial_ifac_netname"] = ""
        if not "connect_serial_ifac_passphrase" in self.config:
            self.config["connect_serial_ifac_passphrase"] = ""
        if not "connect_modem" in self.config:
            self.config["connect_modem"] = False
        if not "connect_modem_ifac_netname" in self.config:
            self.config["connect_modem_ifac_netname"] = ""
        if not "connect_modem_ifac_passphrase" in self.config:
            self.config["connect_modem_ifac_passphrase"] = ""

        if not "connect_ifmode_local" in self.config:
            self.config["connect_ifmode_local"] = "full"
        if not "connect_ifmode_tcp" in self.config:
            self.config["connect_ifmode_tcp"] = "full"
        if not "connect_ifmode_i2p" in self.config:
            self.config["connect_ifmode_i2p"] = "full"
        if not "connect_ifmode_rnode" in self.config:
            self.config["connect_ifmode_rnode"] = "full"
        if not "connect_ifmode_modem" in self.config:
            self.config["connect_ifmode_modem"] = "full"
        if not "connect_ifmode_serial" in self.config:
            self.config["connect_ifmode_serial"] = "full"
        if not "connect_ifmode_bluetooth" in self.config:
            self.config["connect_ifmode_bluetooth"] = "full"

        if not "hw_rnode_frequency" in self.config:
            self.config["hw_rnode_frequency"] = None
        if not "hw_rnode_modulation" in self.config:
            self.config["hw_rnode_modulation"] = "LoRa"
        if not "hw_rnode_bandwidth" in self.config:
            self.config["hw_rnode_bandwidth"] = 62500
        if not "hw_rnode_spreading_factor" in self.config:
            self.config["hw_rnode_spreading_factor"] = 8
        if not "hw_rnode_coding_rate" in self.config:
            self.config["hw_rnode_coding_rate"] = 6
        if not "hw_rnode_tx_power" in self.config:
            self.config["hw_rnode_tx_power"] = 0
        if not "hw_rnode_beaconinterval" in self.config:
            self.config["hw_rnode_beaconinterval"] = None
        if not "hw_rnode_beacondata" in self.config:
            self.config["hw_rnode_beacondata"] = None
        if not "hw_rnode_bluetooth" in self.config:
            self.config["hw_rnode_bluetooth"] = False
        if not "hw_rnode_bt_device" in self.config:
            self.config["hw_rnode_bt_device"] = None

        if not "hw_modem_baudrate" in self.config:
            self.config["hw_modem_baudrate"] = 115200
        if not "hw_modem_databits" in self.config:
            self.config["hw_modem_databits"] = 8
        if not "hw_modem_stopbits" in self.config:
            self.config["hw_modem_stopbits"] = 1
        if not "hw_modem_parity" in self.config:
            self.config["hw_modem_parity"] = "none"
        if not "hw_modem_preamble" in self.config:
            self.config["hw_modem_preamble"] = 150
        if not "hw_modem_tail" in self.config:
            self.config["hw_modem_tail"] = 20
        if not "hw_modem_persistence" in self.config:
            self.config["hw_modem_persistence"] = 220
        if not "hw_modem_slottime" in self.config:
            self.config["hw_modem_slottime"] = 20
        if not "hw_modem_beaconinterval" in self.config:
            self.config["hw_modem_beaconinterval"] = None
        if not "hw_modem_beacondata" in self.config:
            self.config["hw_modem_beacondata"] = None
        
        if not "hw_serial_baudrate" in self.config:
            self.config["hw_serial_baudrate"] = 57600
        if not "hw_serial_databits" in self.config:
            self.config["hw_serial_databits"] = 8
        if not "hw_serial_stopbits" in self.config:
            self.config["hw_serial_stopbits"] = 1
        if not "hw_serial_parity" in self.config:
            self.config["hw_serial_parity"] = "none"

        # Make sure we have a database
        if not os.path.isfile(self.db_path):
            self.__db_init()
        else:
            self._db_initstate()
            self._db_initpersistent()
            self.__db_indices()

    def __reload_config(self):
        RNS.log("Reloading Sideband configuration... "+str(self.config_path), RNS.LOG_DEBUG)
        config_file = open(self.config_path, "rb")
        self.config = msgpack.unpackb(config_file.read())
        config_file.close()

        self.update_active_lxmf_propagation_node()

    def __save_config(self):
        RNS.log("Saving Sideband configuration...", RNS.LOG_DEBUG)
        def save_function():
            while self.saving_configuration:
                time.sleep(0.15)
            try:
                self.saving_configuration = True
                config_file = open(self.config_path, "wb")
                config_file.write(msgpack.packb(self.config))
                config_file.close()
                self.saving_configuration = False
            except Exception as e:
                self.saving_configuration = False
                RNS.log("Error while saving Sideband configuration: "+str(e), RNS.LOG_ERROR)

        threading.Thread(target=save_function, daemon=True).start()

        if self.is_client:
            self.setstate("wants.settings_reload", True)

    def reload_configuration(self):
        self.__reload_config()

    def save_configuration(self):
        self.__save_config()

    def set_active_propagation_node(self, dest):
        if dest == None:
            RNS.log("No active propagation node configured")
        else:
            try:
                self.active_propagation_node = dest
                self.config["last_lxmf_propagation_node"] = dest
                self.message_router.set_outbound_propagation_node(dest)
                
                RNS.log("Active propagation node set to: "+RNS.prettyhexrep(dest))
                self.__save_config()
            except Exception as e:
                RNS.log("Error while setting LXMF propagation node: "+str(e), RNS.LOG_ERROR)

    def notify(self, title, content, group=None, context_id=None):
        if self.config["notifications_on"]:
            if RNS.vendor.platformutils.get_platform() == "android":
                if self.getpersistent("permissions.notifications"):
                    notifications_permitted = True
                else:
                    notifications_permitted = False
            else:
                notifications_permitted = True

            if notifications_permitted:
                if RNS.vendor.platformutils.get_platform() == "android":
                    if self.is_service:
                        self.owner_service.android_notification(title, content, group=group, context_id=context_id)
                    else:
                        plyer.notification.notify(title, content, notification_icon=self.notification_icon, context_override=None)
                else:
                    plyer.notification.notify(title, content, app_icon=self.icon_32)

    def log_announce(self, dest, app_data, dest_type):
        try:
            RNS.log("Received "+str(dest_type)+" announce for "+RNS.prettyhexrep(dest)+" with data: "+app_data.decode("utf-8"))
            self._db_save_announce(dest, app_data, dest_type)
            self.setstate("app.flags.new_announces", True)

        except Exception as e:
            RNS.log("Exception while decoding LXMF destination announce data:"+str(e))

    def list_conversations(self):
        result = self._db_conversations()
        if result != None:
            return result
        else:
            return []

    def list_announces(self):
        result = self._db_announces()
        if result != None:
            return result
        else:
            return []

    def has_conversation(self, context_dest):
        existing_conv = self._db_conversation(context_dest)
        if existing_conv != None:
            return True
        else:
            return False

    def is_trusted(self, context_dest):
        try:
            existing_conv = self._db_conversation(context_dest)
            if existing_conv != None:
                if existing_conv["trust"] == 1:
                    return True
                else:
                    return False
            else:
                return False

        except Exception as e:
            RNS.log("Error while checking trust for "+RNS.prettyhexrep(context_dest)+": "+str(e), RNS.LOG_ERROR)
            return False

    def raw_display_name(self, context_dest):
        try:
            existing_conv = self._db_conversation(context_dest)
            if existing_conv != None:
                if existing_conv["name"] != None and existing_conv["name"] != "":
                    return existing_conv["name"]
                else:
                    return ""
            else:
                return ""

        except Exception as e:
            RNS.log("Error while getting peer name: "+str(e), RNS.LOG_ERROR)
            return ""

    def peer_display_name(self, context_dest):
        try:
            existing_conv = self._db_conversation(context_dest)
            if existing_conv != None:
                if existing_conv["name"] != None and existing_conv["name"] != "":
                    if existing_conv["trust"] == 1:
                        return existing_conv["name"]
                    else:
                        return existing_conv["name"]+" "+RNS.prettyhexrep(context_dest)

                else:
                    app_data = RNS.Identity.recall_app_data(context_dest)
                    if app_data != None:
                        if existing_conv["trust"] == 1:
                            return app_data.decode("utf-8")
                        else:
                            return app_data.decode("utf-8")+" "+RNS.prettyhexrep(context_dest)
                    else:
                        return RNS.prettyhexrep(context_dest)
            else:
                app_data = RNS.Identity.recall_app_data(context_dest)
                if app_data != None:
                    return app_data.decode("utf-8")+" "+RNS.prettyhexrep(context_dest)
                else:
                    return RNS.prettyhexrep(context_dest)


        except Exception as e:
            RNS.log("Could not decode a valid peer name from data: "+str(e), RNS.LOG_DEBUG)
            return RNS.prettyhexrep(context_dest)

    def clear_conversation(self, context_dest):
        self._db_clear_conversation(context_dest)

    def delete_announce(self, context_dest):
        self._db_delete_announce(context_dest)

    def delete_conversation(self, context_dest):
        self._db_clear_conversation(context_dest)
        self._db_delete_conversation(context_dest)

    def delete_message(self, message_hash):
        self._db_delete_message(message_hash)

    def read_conversation(self, context_dest):
        self._db_conversation_set_unread(context_dest, False)

    def unread_conversation(self, context_dest):
        self._db_conversation_set_unread(context_dest, True)

    def trusted_conversation(self, context_dest):
        self._db_conversation_set_trusted(context_dest, True)

    def untrusted_conversation(self, context_dest):
        self._db_conversation_set_trusted(context_dest, False)

    def named_conversation(self, name, context_dest):
        self._db_conversation_set_name(context_dest, name)

    def count_messages(self, context_dest):
        result = self._db_message_count(context_dest)
        if result != None:
            return result
        else:
            return None

    def list_messages(self, context_dest, after = None, before = None, limit = None):
        result = self._db_messages(context_dest, after, before, limit)
        if result != None:
            return result
        else:
            return []

    def service_available(self):
        service_heartbeat = self.getstate("service.heartbeat")
        if not service_heartbeat:
            return False
        else:
            try:
                if time.time() - service_heartbeat > 2.5:
                    return False
                else:
                    return True
            except:
                return False

    def gui_foreground(self):
        return self._db_getstate("app.foreground")

    def gui_display(self):
        return self._db_getstate("app.displaying")

    def gui_conversation(self):
        return self._db_getstate("app.active_conversation")

    def setstate(self, prop, val):
        self.getstate_cache[prop] = val
        self._db_setstate(prop, val)
        # def cb():
        #     self._db_setstate(prop, val)
        # threading.Thread(target=cb, daemon=True).start()

    def getstate(self, prop, allow_cache=False):
        if not RNS.vendor.platformutils.is_android():
            return self._db_getstate(prop)

        else:
            db_timeout = 0.060
            cached_value = None
            has_cached_value = False
            if prop in self.getstate_cache:
                cached_value = self.getstate_cache[prop]
                has_cached_value = True
            
            if not allow_cache or not has_cached_value:
                self.getstate_cache[prop] = self._db_getstate(prop)
                return self.getstate_cache[prop]
            
            else:
                get_thread_running = True
                def get_job():
                    self.getstate_cache[prop] = self._db_getstate(prop)
                    get_thread_running = False

                get_thread = threading.Thread(target=get_job, daemon=True)
                get_thread.timeout = time.time()+db_timeout
                get_thread.start()

                while get_thread.is_alive() and time.time() < get_thread.timeout:
                    time.sleep(0.01)

                if get_thread.is_alive():
                    return self.getstate_cache[prop]
                else:
                    return self.getstate_cache[prop]




    def setpersistent(self, prop, val):
        self._db_setpersistent(prop, val)
        # def cb():
        #     self._db_setpersistent(prop, val)
        # threading.Thread(target=cb, daemon=True).start()

    def getpersistent(self, prop):
        return self._db_getpersistent(prop)

    def __event_conversations_changed(self):
        pass

    def __event_conversation_changed(self, context_dest):
        pass

    def __db_connect(self):
        if self.db == None:
            self.db = sqlite3.connect(self.db_path, check_same_thread=False)

        return self.db

    def __db_init(self):
        db = self.__db_connect()
        dbc = db.cursor()

        dbc.execute("DROP TABLE IF EXISTS lxm")
        dbc.execute("CREATE TABLE lxm (lxm_hash BLOB PRIMARY KEY, dest BLOB, source BLOB, title BLOB, tx_ts INTEGER, rx_ts INTEGER, state INTEGER, method INTEGER, t_encrypted INTEGER, t_encryption INTEGER, data BLOB)")

        dbc.execute("DROP TABLE IF EXISTS conv")
        dbc.execute("CREATE TABLE conv (dest_context BLOB PRIMARY KEY, last_tx INTEGER, last_rx INTEGER, unread INTEGER, type INTEGER, trust INTEGER, name BLOB, data BLOB)")

        dbc.execute("DROP TABLE IF EXISTS announce")
        dbc.execute("CREATE TABLE announce (id PRIMARY KEY, received INTEGER, source BLOB, data BLOB, dest_type BLOB)")

        dbc.execute("DROP TABLE IF EXISTS state")
        dbc.execute("CREATE TABLE state (property BLOB PRIMARY KEY, value BLOB)")

        dbc.execute("DROP TABLE IF EXISTS persistent")
        dbc.execute("CREATE TABLE persistent (property BLOB PRIMARY KEY, value BLOB)")

        db.commit()

    def __db_indices(self):
        db = self.__db_connect()
        dbc = db.cursor()
        dbc.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_persistent_property ON persistent(property)")
        dbc.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_state_property ON state(property)")
        dbc.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_conv_dest_context ON conv(dest_context)")
        db.commit()

    def _db_initstate(self):
        db = self.__db_connect()
        dbc = db.cursor()

        dbc.execute("DROP TABLE IF EXISTS state")
        dbc.execute("CREATE TABLE state (property BLOB PRIMARY KEY, value BLOB)")
        db.commit()
        self._db_setstate("database_ready", True)

    def _db_getstate(self, prop):
        try:
            db = self.__db_connect()
            dbc = db.cursor()

            query = "select * from state where property=:uprop"
            dbc.execute(query, {"uprop": prop.encode("utf-8")})
            
            result = dbc.fetchall()

            if len(result) < 1:
                return None
            else:
                try:
                    entry = result[0]
                    val = msgpack.unpackb(entry[1])
                    
                    return val
                except Exception as e:
                    RNS.log("Could not unpack state value from database for property \""+str(prop)+"\". The contained exception was: "+str(e), RNS.LOG_ERROR)
                    return None

        except Exception as e:
            RNS.log("An error occurred during getstate database operation: "+str(e), RNS.LOG_ERROR)
            self.db = None

    def _db_setstate(self, prop, val):
        try:
            uprop = prop.encode("utf-8")
            bval = msgpack.packb(val)

            if self._db_getstate(prop) == None:
                try:
                    db = self.__db_connect()
                    dbc = db.cursor()
                    query = "INSERT INTO state (property, value) values (?, ?)"
                    data = (uprop, bval)
                    dbc.execute(query, data)
                    db.commit()

                except Exception as e:
                    RNS.log("Error while setting state property "+str(prop)+" in DB: "+str(e), RNS.LOG_ERROR)
                    RNS.log("Retrying as update query...", RNS.LOG_ERROR)
                    db = self.__db_connect()
                    dbc = db.cursor()
                    query = "UPDATE state set value=:bval where property=:uprop;"
                    dbc.execute(query, {"bval": bval, "uprop": uprop})
                    db.commit()

            else:
                db = self.__db_connect()
                dbc = db.cursor()
                query = "UPDATE state set value=:bval where property=:uprop;"
                dbc.execute(query, {"bval": bval, "uprop": uprop})
                db.commit()


        except Exception as e:
            RNS.log("An error occurred during setstate database operation: "+str(e), RNS.LOG_ERROR)
            self.db = None

    def _db_initpersistent(self):
        db = self.__db_connect()
        dbc = db.cursor()

        dbc.execute("CREATE TABLE IF NOT EXISTS persistent (property BLOB PRIMARY KEY, value BLOB)")
        db.commit()

    def _db_getpersistent(self, prop):
        try:
            db = self.__db_connect()
            dbc = db.cursor()
            
            query = "select * from persistent where property=:uprop"
            dbc.execute(query, {"uprop": prop.encode("utf-8")})
            result = dbc.fetchall()

            if len(result) < 1:
                return None
            else:
                try:
                    entry = result[0]
                    val = msgpack.unpackb(entry[1])
                    if val == None:
                        query = "delete from persistent where (property=:uprop);"
                        dbc.execute(query, {"uprop": prop.encode("utf-8")})
                        db.commit()

                    return val
                except Exception as e:
                    RNS.log("Could not unpack persistent value from database for property \""+str(prop)+"\". The contained exception was: "+str(e), RNS.LOG_ERROR)
                    return None
        
        except Exception as e:
            RNS.log("An error occurred during persistent getstate database operation: "+str(e), RNS.LOG_ERROR)
            self.db = None

    def _db_setpersistent(self, prop, val):
        try:
            db = self.__db_connect()
            dbc = db.cursor()
            uprop = prop.encode("utf-8")
            bval = msgpack.packb(val)

            if self._db_getpersistent(prop) == None:
                try:
                    query = "INSERT INTO persistent (property, value) values (?, ?)"
                    data = (uprop, bval)
                    dbc.execute(query, data)
                    db.commit()
        
                except Exception as e:
                    RNS.log("Error while setting persistent state property "+str(prop)+" in DB: "+str(e), RNS.LOG_ERROR)
                    RNS.log("Retrying as update query...")
                    query = "UPDATE state set value=:bval where property=:uprop;"
                    dbc.execute(query, {"bval": bval, "uprop": uprop})
                    db.commit()

            else:
                query = "UPDATE persistent set value=:bval where property=:uprop;"
                dbc.execute(query, {"bval": bval, "uprop": uprop})
                db.commit()
        
        except Exception as e:
            RNS.log("An error occurred during persistent setstate database operation: "+str(e), RNS.LOG_ERROR)
            self.db = None

    def _db_conversation_set_unread(self, context_dest, unread):
        db = self.__db_connect()
        dbc = db.cursor()
        
        query = "UPDATE conv set unread = ? where dest_context = ?"
        data = (unread, context_dest)
        dbc.execute(query, data)
        result = dbc.fetchall()
        db.commit()

    def _db_conversation_set_trusted(self, context_dest, trusted):
        db = self.__db_connect()
        dbc = db.cursor()
        
        query = "UPDATE conv set trust = ? where dest_context = ?"
        data = (trusted, context_dest)
        dbc.execute(query, data)
        result = dbc.fetchall()
        db.commit()

    def _db_conversation_set_name(self, context_dest, name):
        db = self.__db_connect()
        dbc = db.cursor()
        
        query = "UPDATE conv set name=:name_data where dest_context=:ctx;"
        dbc.execute(query, {"ctx": context_dest, "name_data": name.encode("utf-8")})
        result = dbc.fetchall()
        db.commit()

    def _db_conversations(self):
        db = self.__db_connect()
        dbc = db.cursor()
        
        dbc.execute("select * from conv")
        result = dbc.fetchall()

        if len(result) < 1:
            return None
        else:
            convs = []
            for entry in result:
                conv = {
                    "dest": entry[0],
                    "unread": entry[3],
                }
                convs.append(conv)

            return convs

    def _db_announces(self):
        db = self.__db_connect()
        dbc = db.cursor()
        
        dbc.execute("select * from announce order by received desc")
        result = dbc.fetchall()

        if len(result) < 1:
            return None
        else:
            announces = []
            added_dests = []
            for entry in result:
                try:
                    if not entry[2] in added_dests:
                        announce = {
                            "dest": entry[2],
                            "data": entry[3].decode("utf-8"),
                            "time": entry[1],
                            "type": entry[4]
                        }
                        added_dests.append(entry[2])
                        announces.append(announce)
                except Exception as e:
                    RNS.log("Exception while fetching announce from DB: "+str(e), RNS.LOG_ERROR)

            announces.reverse()
            return announces

    def _db_conversation(self, context_dest):
        db = self.__db_connect()
        dbc = db.cursor()
        
        query = "select * from conv where dest_context=:ctx"
        dbc.execute(query, {"ctx": context_dest})
        result = dbc.fetchall()

        if len(result) < 1:
            return None
        else:
            c = result[0]
            conv = {}
            conv["dest"] = c[0]
            conv["last_tx"] = c[1]
            conv["last_rx"] = c[2]
            conv["unread"] = c[3]
            conv["type"] = c[4]
            conv["trust"] = c[5]
            conv["name"] = c[6].decode("utf-8")
            conv["data"] = msgpack.unpackb(c[7])
            return conv

    def _db_clear_conversation(self, context_dest):
        RNS.log("Clearing conversation with "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
        db = self.__db_connect()
        dbc = db.cursor()

        query = "delete from lxm where (dest=:ctx_dst or source=:ctx_dst);"
        dbc.execute(query, {"ctx_dst": context_dest})
        db.commit()

    def _db_delete_conversation(self, context_dest):
        RNS.log("Deleting conversation with "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
        db = self.__db_connect()
        dbc = db.cursor()

        query = "delete from conv where (dest_context=:ctx_dst);"
        dbc.execute(query, {"ctx_dst": context_dest})
        db.commit()


    def _db_delete_announce(self, context_dest):
        RNS.log("Deleting announce with "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
        db = self.__db_connect()
        dbc = db.cursor()

        query = "delete from announce where (source=:ctx_dst);"
        dbc.execute(query, {"ctx_dst": context_dest})
        db.commit()

    def _db_create_conversation(self, context_dest, name = None, trust = False):
        RNS.log("Creating conversation for "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
        db = self.__db_connect()
        dbc = db.cursor()

        def_name = "".encode("utf-8")
        query = "INSERT INTO conv (dest_context, last_tx, last_rx, unread, type, trust, name, data) values (?, ?, ?, ?, ?, ?, ?, ?)"
        data = (context_dest, 0, 0, 0, SidebandCore.CONV_P2P, 0, def_name, msgpack.packb(None))

        dbc.execute(query, data)
        db.commit()

        if trust:
            self._db_conversation_set_trusted(context_dest, True)

        if name != None and name != "":
            self._db_conversation_set_name(context_dest, name)

        self.__event_conversations_changed()

    def _db_delete_message(self, msg_hash):
        RNS.log("Deleting message "+RNS.prettyhexrep(msg_hash))
        db = self.__db_connect()
        dbc = db.cursor()

        query = "delete from lxm where (lxm_hash=:mhash);"
        dbc.execute(query, {"mhash": msg_hash})
        db.commit()

    def _db_clean_messages(self):
        RNS.log("Purging stale messages... "+str(self.db_path))
        db = self.__db_connect()
        dbc = db.cursor()

        query = "delete from lxm where (state=:outbound_state or state=:sending_state);"
        dbc.execute(query, {"outbound_state": LXMF.LXMessage.OUTBOUND, "sending_state": LXMF.LXMessage.SENDING})
        db.commit()

    def _db_message_set_state(self, lxm_hash, state):
        db = self.__db_connect()
        dbc = db.cursor()
        
        query = "UPDATE lxm set state = ? where lxm_hash = ?"
        data = (state, lxm_hash)
        dbc.execute(query, data)
        db.commit()
        result = dbc.fetchall()

    def _db_message_set_method(self, lxm_hash, method):
        db = self.__db_connect()
        dbc = db.cursor()
        
        query = "UPDATE lxm set method = ? where lxm_hash = ?"
        data = (method, lxm_hash)
        dbc.execute(query, data)
        db.commit()
        result = dbc.fetchall()

    def message(self, msg_hash):
        return self._db_message(msg_hash)

    def _db_message(self, msg_hash):
        db = self.__db_connect()
        dbc = db.cursor()
        
        query = "select * from lxm where lxm_hash=:mhash"
        dbc.execute(query, {"mhash": msg_hash})
        result = dbc.fetchall()

        if len(result) < 1:
            return None
        else:
            entry = result[0]

            lxm_method = entry[7]
            if lxm_method == LXMF.LXMessage.PAPER:
                lxm_data = msgpack.unpackb(entry[10])
                packed_lxm = lxm_data[0]
                paper_packed_lxm = lxm_data[1]
            else:
                packed_lxm = entry[10]

            lxm = LXMF.LXMessage.unpack_from_bytes(packed_lxm, original_method = lxm_method)

            if lxm.desired_method == LXMF.LXMessage.PAPER:
                lxm.paper_packed = paper_packed_lxm

            message = {
                "hash": lxm.hash,
                "dest": lxm.destination_hash,
                "source": lxm.source_hash,
                "title": lxm.title,
                "content": lxm.content,
                "received": entry[5],
                "sent": lxm.timestamp,
                "state": entry[6],
                "method": entry[7],
                "lxm": lxm
            }
            return message

    def _db_message_count(self, context_dest):
        db = self.__db_connect()
        dbc = db.cursor()
        
        query = "select count(*) from lxm where dest=:context_dest or source=:context_dest"
        dbc.execute(query, {"context_dest": context_dest})

        result = dbc.fetchall()

        if len(result) < 1:
            return None
        else:
            return result[0][0]

    def _db_messages(self, context_dest, after = None, before = None, limit = None):
        db = self.__db_connect()
        dbc = db.cursor()
        
        if after != None and before == None:
            query = "select * from lxm where (dest=:context_dest or source=:context_dest) and rx_ts>:after_ts"
            dbc.execute(query, {"context_dest": context_dest, "after_ts": after})
        elif after == None and before != None:
            query = "select * from lxm where (dest=:context_dest or source=:context_dest) and rx_ts<:before_ts"
            dbc.execute(query, {"context_dest": context_dest, "before_ts": before})
        elif after != None and before != None:
            query = "select * from lxm where (dest=:context_dest or source=:context_dest) and rx_ts<:before_ts and rx_ts>:after_ts"
            dbc.execute(query, {"context_dest": context_dest, "before_ts": before, "after_ts": after})
        else:
            query = "select * from lxm where dest=:context_dest or source=:context_dest"
            dbc.execute(query, {"context_dest": context_dest})

        result = dbc.fetchall()

        if len(result) < 1:
            return None
        else:
            messages = []
            for entry in result:
                lxm_method = entry[7]
                if lxm_method == LXMF.LXMessage.PAPER:
                    lxm_data = msgpack.unpackb(entry[10])
                    packed_lxm = lxm_data[0]
                    paper_packed_lxm = lxm_data[1]
                else:
                    packed_lxm = entry[10]

                lxm = LXMF.LXMessage.unpack_from_bytes(packed_lxm, original_method = lxm_method)
                
                if lxm.desired_method == LXMF.LXMessage.PAPER:
                    lxm.paper_packed = paper_packed_lxm
                
                message = {
                    "hash": lxm.hash,
                    "dest": lxm.destination_hash,
                    "source": lxm.source_hash,
                    "title": lxm.title,
                    "content": lxm.content,
                    "received": entry[5],
                    "sent": lxm.timestamp,
                    "state": entry[6],
                    "method": entry[7],
                    "lxm": lxm
                }

                messages.append(message)
            if len(messages) > limit:
                messages = messages[-limit:]
            return messages

    def _db_save_lxm(self, lxm, context_dest):    
        state = lxm.state

        db = self.__db_connect()
        dbc = db.cursor()

        if not lxm.packed:
            lxm.pack()

        if lxm.method == LXMF.LXMessage.PAPER:
            packed_lxm = msgpack.packb([lxm.packed, lxm.paper_packed])
        else:
            packed_lxm = lxm.packed

        query = "INSERT INTO lxm (lxm_hash, dest, source, title, tx_ts, rx_ts, state, method, t_encrypted, t_encryption, data) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        data = (
            lxm.hash,
            lxm.destination_hash,
            lxm.source_hash,
            lxm.title,
            lxm.timestamp,
            time.time(),
            state,
            lxm.method,
            lxm.transport_encrypted,
            lxm.transport_encryption,
            packed_lxm,
        )

        dbc.execute(query, data)

        db.commit()

        self.__event_conversation_changed(context_dest)

    def _db_save_announce(self, destination_hash, app_data, dest_type="lxmf.delivery"):
        db = self.__db_connect()
        dbc = db.cursor()

        query = "delete from announce where id is NULL or id not in (select id from announce order by received desc limit "+str(self.MAX_ANNOUNCES)+")"
        dbc.execute(query)

        query = "delete from announce where (source=:source);"
        dbc.execute(query, {"source": destination_hash})

        now = time.time()
        hash_material = str(time).encode("utf-8")+destination_hash+app_data+dest_type.encode("utf-8")
        announce_hash = RNS.Identity.full_hash(hash_material)

        query = "INSERT INTO announce (id, received, source, data, dest_type) values (?, ?, ?, ?, ?)"
        data = (
            announce_hash,
            now,
            destination_hash,
            app_data,
            dest_type,
        )

        dbc.execute(query, data)
        db.commit()

    def lxmf_announce(self, attached_interface=None):
        if self.is_standalone or self.is_service:
            self.lxmf_destination.announce(attached_interface=attached_interface)
            self.last_lxmf_announce = time.time()
            self.next_auto_announce = time.time() + 60*(random.random()*(SidebandCore.AUTO_ANNOUNCE_RANDOM_MAX-SidebandCore.AUTO_ANNOUNCE_RANDOM_MIN))
            RNS.log("Next auto announce in "+RNS.prettytime(self.next_auto_announce-time.time()), RNS.LOG_DEBUG)
            self.setstate("wants.announce", False)
        else:
            self.setstate("wants.announce", True)

    def is_known(self, dest_hash):
        try:
            source_identity = RNS.Identity.recall(dest_hash)

            if source_identity:
                return True
            else:
                return False

        except Exception as e:
            return False

    def request_key(self, dest_hash):
        try:
            RNS.Transport.request_path(dest_hash)
            return True

        except Exception as e:
            RNS.log("Error while querying for key: "+str(e), RNS.LOG_ERROR)
            return False

    def _service_jobs(self):
        if self.is_service:
            last_usb_discovery = time.time()
            while True:
                time.sleep(SidebandCore.SERVICE_JOB_INTERVAL)
                now = time.time()

                announce_wanted = self.getstate("wants.announce")
                announce_attached_interface = None
                announce_delay = 0
                # TODO: The "start_announce" config entry should be
                # renamed to "auto_announce", which is its current
                # meaning.
                if self.config["start_announce"] == True:
                    needs_if_change_announce = False

                    if hasattr(self, "interface_local") and self.interface_local != None:
                        have_peers = len(self.interface_local.peers) > 0
                        if self.interface_local.carrier_changed:
                            RNS.log("AutoInterface carrier change detected, retaking wake locks", RNS.LOG_DEBUG)
                            self.owner_service.take_locks(force_multicast=True)
                            self.interface_local.carrier_changed = False

                        if hasattr(self.interface_local, "had_peers"):
                            if not self.interface_local.had_peers and have_peers:
                                RNS.log("Peers became reachable on the interface "+str(self.interface_local), RNS.LOG_DEBUG)
                                needs_if_change_announce = True
                                announce_attached_interface = self.interface_local
                                announce_delay = 10

                            if self.interface_local.had_peers and not have_peers:
                                RNS.log("No peers reachable on the interface "+str(self.interface_local), RNS.LOG_DEBUG)
                                needs_if_change_announce = True

                        self.interface_local.had_peers = have_peers

                    for interface in RNS.Transport.interfaces:
                        if not hasattr(self, "interface_local") or interface != self.interface_local:
                            if hasattr(interface, "was_online"):
                                if not interface.was_online and interface.online:
                                    RNS.log("The interface "+str(interface)+" became available", RNS.LOG_DEBUG)
                                    needs_if_change_announce = True

                                if interface.was_online and not interface.online:
                                    RNS.log("The interface "+str(interface)+" became unavailable", RNS.LOG_DEBUG)
                                    needs_if_change_announce = True

                            interface.was_online = interface.online

                    if needs_if_change_announce and time.time() > self.last_if_change_announce+SidebandCore.IF_CHANGE_ANNOUNCE_MIN_INTERVAL:
                        announce_wanted = True
                        self.last_if_change_announce = time.time()

                    if time.time() > self.next_auto_announce:
                        announce_wanted = True

                if hasattr(self, "interface_rnode") and self.interface_rnode != None:
                    if self.config["hw_rnode_bluetooth"]:
                        self.interface_rnode.allow_bluetooth = True
                    else:
                        self.interface_rnode.allow_bluetooth = False

                if announce_wanted:
                    def gen_announce_job(delay, attached_interface):
                        def x():
                            aif = announce_attached_interface
                            time.sleep(delay)
                            self.lxmf_announce(attached_interface=aif)
                        return x

                    threading.Thread(target=gen_announce_job(announce_delay, announce_attached_interface), daemon=True).start()

                if self.getstate("wants.bt_on"):
                    self.setstate("wants.bt_on", False)
                    self.owner_app.discover_usb_devices()
                    self.setstate("executing.bt_on", True)
                    if self.interface_rnode != None:
                        self.interface_rnode.enable_bluetooth()
                    else:
                        if hasattr(self.owner_app, "usb_devices") and self.owner_app.usb_devices != None:
                            if len(self.owner_app.usb_devices) > 0:
                                target_port = self.owner_app.usb_devices[0]["port"]
                                RNS.Interfaces.Android.RNodeInterface.RNodeInterface.bluetooth_control(port=target_port, enable_bluetooth = True)
                            else:
                                RNS.log("Could not execute RNode Bluetooth control command, no USB devices available", RNS.LOG_ERROR)
                    self.setstate("executing.bt_on", False)
                
                if self.getstate("wants.bt_off"):
                    self.setstate("wants.bt_off", False)
                    self.owner_app.discover_usb_devices()
                    self.setstate("executing.bt_off", True)
                    if self.interface_rnode != None:
                        self.interface_rnode.disable_bluetooth()
                    else:
                        if hasattr(self.owner_app, "usb_devices") and self.owner_app.usb_devices != None:
                            if len(self.owner_app.usb_devices) > 0:
                                target_port = self.owner_app.usb_devices[0]["port"]
                                RNS.Interfaces.Android.RNodeInterface.RNodeInterface.bluetooth_control(port=target_port, disable_bluetooth = True)
                            else:
                                RNS.log("Could not execute RNode Bluetooth control command, no USB devices available", RNS.LOG_ERROR)
                    self.setstate("executing.bt_off", False)
                
                if self.getstate("wants.bt_pair"):
                    self.setstate("wants.bt_pair", False)
                    self.owner_app.discover_usb_devices()
                    self.setstate("executing.bt_pair", True)
                    if self.interface_rnode != None:
                        self.interface_rnode.bluetooth_pair()
                    else:
                        if hasattr(self.owner_app, "usb_devices") and self.owner_app.usb_devices != None:
                            if len(self.owner_app.usb_devices) > 0:
                                try:
                                    target_port = self.owner_app.usb_devices[0]["port"]
                                    RNS.Interfaces.Android.RNodeInterface.RNodeInterface.bluetooth_control(port=target_port, pairing_mode = True)
                                except Exception as e:
                                    self.setstate("hardware_operation.error", "An error ocurred while trying to communicate with the device. Please make sure that Sideband has been granted permissions to access the device.\n\nThe reported error was:\n\n[i]"+str(e)+"[/i]")                
                            else:
                                RNS.log("Could not execute RNode Bluetooth control command, no USB devices available", RNS.LOG_ERROR)
                    self.setstate("executing.bt_pair", False)

                if (now - last_usb_discovery > 5):
                    if self.interface_rnode != None and not self.interface_rnode.online:
                        self.owner_app.discover_usb_devices()
                        last_usb_discovery = time.time()

                        if hasattr(self.owner_app, "usb_devices") and self.owner_app.usb_devices != None:
                            if len(self.owner_app.usb_devices) > 0:
                                target_device = self.owner_app.usb_devices[0]
                                if self.interface_rnode.port != target_device["port"]:
                                    RNS.log("Updating RNode device to "+str(target_device))
                                    self.interface_rnode.port = target_device["port"]

                    if self.interface_serial != None and not self.interface_serial.online:
                        self.owner_app.discover_usb_devices()
                        last_usb_discovery = time.time()

                        if hasattr(self.owner_app, "usb_devices") and self.owner_app.usb_devices != None:
                            if len(self.owner_app.usb_devices) > 0:
                                target_device = self.owner_app.usb_devices[0]
                                if self.interface_serial.port != target_device["port"]:
                                    RNS.log("Updating serial device to "+str(target_device))
                                    self.interface_serial.port = target_device["port"]

                    if self.interface_modem != None and not self.interface_modem.online:
                        self.owner_app.discover_usb_devices()
                        last_usb_discovery = time.time()

                        if hasattr(self.owner_app, "usb_devices") and self.owner_app.usb_devices != None:
                            if len(self.owner_app.usb_devices) > 0:
                                target_device = self.owner_app.usb_devices[0]
                                if self.interface_modem.port != target_device["port"]:
                                    RNS.log("Updating modem device to "+str(target_device))
                                    self.interface_modem.port = target_device["port"]

    def _periodic_jobs(self):
        if self.is_service or self.is_standalone:
            while True:
                time.sleep(SidebandCore.PERIODIC_JOBS_INTERVAL)
                if self.config["lxmf_periodic_sync"] == True:
                    if self.getpersistent("lxmf.lastsync") == None:
                        self.setpersistent("lxmf.lastsync", time.time())
                    else:
                        now = time.time()
                        syncinterval = self.config["lxmf_sync_interval"]
                        lastsync = self.getpersistent("lxmf.lastsync")
                        nextsync = lastsync+syncinterval

                        RNS.log("Last sync was "+RNS.prettytime(now-lastsync)+" ago", RNS.LOG_DEBUG)
                        RNS.log("Next sync is "+("in "+RNS.prettytime(nextsync-now) if nextsync-now > 0 else "now"), RNS.LOG_DEBUG)
                        if now > nextsync:
                            if self.request_lxmf_sync():
                                RNS.log("Scheduled LXMF sync succeeded", RNS.LOG_DEBUG)
                                self.setpersistent("lxmf.lastsync", time.time())
                                self.setpersistent("lxmf.syncretrying", False)
                            else:
                                if not self.getpersistent("lxmf.syncretrying"):
                                    RNS.log("Scheduled LXMF sync failed, retrying in "+RNS.prettytime(SidebandCore.PERIODIC_SYNC_RETRY), RNS.LOG_DEBUG)
                                    self.setpersistent("lxmf.lastsync", lastsync+SidebandCore.PERIODIC_SYNC_RETRY)
                                    self.setpersistent("lxmf.syncretrying", True)
                                else:
                                    RNS.log("Retry of scheduled LXMF sync failed too, waiting until next scheduled sync to try again", RNS.LOG_DEBUG)
                                    self.setpersistent("lxmf.lastsync", time.time())
                                    self.setpersistent("lxmf.syncretrying", False)

    def __start_jobs_deferred(self):
        if self.is_service:
            self.service_thread = threading.Thread(target=self._service_jobs, daemon=True)
            self.service_thread.start()

        if self.is_standalone or self.is_service:            
            if self.config["start_announce"]:
                self.lxmf_announce()
                self.last_if_change_announce = time.time()

            self.periodic_thread = threading.Thread(target=self._periodic_jobs, daemon=True)
            self.periodic_thread.start()
        
    def __start_jobs_immediate(self):
        if self.log_verbose:
            selected_level = 7
        else:
            selected_level = 2

        self.setstate("init.loadingstate", "Substantiating Reticulum")
        self.reticulum = RNS.Reticulum(configdir=self.rns_configdir, loglevel=selected_level)

        if RNS.vendor.platformutils.get_platform() == "android":
            # TODO: Just log to console for, but add option to export log
            # files at some point.
            # if self.config["debug"]:
            #     self.reticulum.logdest = RNS.LOG_FILE
            #     if not self.reticulum.is_connected_to_shared_instance:
            #         self.reticulum.logfile = self.log_dir+"sideband_service.log"
            #     else:
            #         self.reticulum.logfile = self.log_dir+"sideband_core.log"

            if not self.reticulum.is_connected_to_shared_instance:
                RNS.log("Running as master or standalone instance, adding interfaces")
                
                self.interface_local  = None
                self.interface_tcp    = None
                self.interface_i2p    = None
                self.interface_rnode  = None
                self.interface_modem  = None
                self.interface_serial = None

                if self.config["connect_local"]:
                    self.setstate("init.loadingstate", "Discovering Topography")
                    try:
                        RNS.log("Adding Auto Interface...", RNS.LOG_DEBUG)
                        if self.config["connect_local_groupid"] == "":
                            group_id = None
                        else:
                            group_id = self.config["connect_local_groupid"]

                        if self.config["connect_local_ifac_netname"] == "":
                            ifac_netname = None
                        else:
                            ifac_netname = self.config["connect_local_ifac_netname"]

                        if self.config["connect_local_ifac_passphrase"] == "":
                            ifac_netkey = None
                        else:
                            ifac_netkey = self.config["connect_local_ifac_passphrase"]

                        autointerface = RNS.Interfaces.AutoInterface.AutoInterface(
                            RNS.Transport,
                            name = "AutoInterface",
                            group_id = group_id
                        )
                        autointerface.OUT = True

                        if RNS.Reticulum.transport_enabled():
                            if_mode = Interface.Interface.MODE_FULL
                            if self.config["connect_ifmode_local"] == "gateway":
                                if_mode = Interface.Interface.MODE_GATEWAY
                            elif self.config["connect_ifmode_local"] == "access point":
                                if_mode = Interface.Interface.MODE_ACCESS_POINT
                            elif self.config["connect_ifmode_local"] == "roaming":
                                if_mode = Interface.Interface.MODE_ROAMING
                            elif self.config["connect_ifmode_local"] == "boundary":
                                if_mode = Interface.Interface.MODE_BOUNDARY
                        else:
                            if_mode = None
                            
                        self.reticulum._add_interface(autointerface, mode = if_mode, ifac_netname = ifac_netname, ifac_netkey = ifac_netkey)
                        self.interface_local = autointerface

                    except Exception as e:
                        RNS.log("Error while adding AutoInterface. The contained exception was: "+str(e))
                        self.interface_local = None

                if self.config["connect_tcp"]:
                    self.setstate("init.loadingstate", "Connecting TCP Tunnel")
                    try:
                        RNS.log("Adding TCP Interface...", RNS.LOG_DEBUG)

                        if self.config["connect_tcp_host"] != "":
                            tcp_host = self.config["connect_tcp_host"]
                            tcp_port = int(self.config["connect_tcp_port"])

                            if tcp_port > 0 and tcp_port <= 65536:
                                if self.config["connect_tcp_ifac_netname"] == "":
                                    ifac_netname = None
                                else:
                                    ifac_netname = self.config["connect_tcp_ifac_netname"]

                                if self.config["connect_tcp_ifac_passphrase"] == "":
                                    ifac_netkey = None
                                else:
                                    ifac_netkey = self.config["connect_tcp_ifac_passphrase"]

                                tcpinterface = RNS.Interfaces.TCPInterface.TCPClientInterface(
                                    RNS.Transport,
                                    "TCPClientInterface",
                                    tcp_host,
                                    tcp_port,
                                    kiss_framing = False,
                                    i2p_tunneled = False
                                )

                                tcpinterface.OUT = True

                                if RNS.Reticulum.transport_enabled():
                                    if_mode = Interface.Interface.MODE_FULL
                                    if self.config["connect_ifmode_tcp"] == "gateway":
                                        if_mode = Interface.Interface.MODE_GATEWAY
                                    elif self.config["connect_ifmode_tcp"] == "access point":
                                        if_mode = Interface.Interface.MODE_ACCESS_POINT
                                    elif self.config["connect_ifmode_tcp"] == "roaming":
                                        if_mode = Interface.Interface.MODE_ROAMING
                                    elif self.config["connect_ifmode_tcp"] == "boundary":
                                        if_mode = Interface.Interface.MODE_BOUNDARY
                                else:
                                    if_mode = None
                                    
                                self.reticulum._add_interface(tcpinterface, mode=if_mode, ifac_netname=ifac_netname, ifac_netkey=ifac_netkey)
                                self.interface_tcp = tcpinterface

                    except Exception as e:
                        RNS.log("Error while adding TCP Interface. The contained exception was: "+str(e))
                        self.interface_tcp = None

                if self.config["connect_i2p"]:
                    self.setstate("init.loadingstate", "Opening I2P Endpoints")
                    try:
                        RNS.log("Adding I2P Interface...", RNS.LOG_DEBUG)
                        if self.config["connect_i2p_b32"].endswith(".b32.i2p"):

                            if self.config["connect_i2p_ifac_netname"] == "":
                                ifac_netname = None
                            else:
                                ifac_netname = self.config["connect_i2p_ifac_netname"]

                            if self.config["connect_i2p_ifac_passphrase"] == "":
                                ifac_netkey = None
                            else:
                                ifac_netkey = self.config["connect_i2p_ifac_passphrase"]

                            i2pinterface = RNS.Interfaces.I2PInterface.I2PInterface(
                                RNS.Transport,
                                "I2PInterface",
                                RNS.Reticulum.storagepath,
                                [self.config["connect_i2p_b32"]],
                                connectable = False,
                            )

                            i2pinterface.OUT = True

                            if RNS.Reticulum.transport_enabled():
                                if_mode = Interface.Interface.MODE_FULL
                                if self.config["connect_ifmode_i2p"] == "gateway":
                                    if_mode = Interface.Interface.MODE_GATEWAY
                                elif self.config["connect_ifmode_i2p"] == "access point":
                                    if_mode = Interface.Interface.MODE_ACCESS_POINT
                                elif self.config["connect_ifmode_i2p"] == "roaming":
                                    if_mode = Interface.Interface.MODE_ROAMING
                                elif self.config["connect_ifmode_i2p"] == "boundary":
                                    if_mode = Interface.Interface.MODE_BOUNDARY
                            else:
                                if_mode = None
                                
                            self.reticulum._add_interface(i2pinterface, mode = if_mode, ifac_netname=ifac_netname, ifac_netkey=ifac_netkey)
                            
                            for si in RNS.Transport.interfaces:
                                if type(si) == RNS.Interfaces.I2PInterface.I2PInterfacePeer:
                                    self.interface_i2p = si


                    except Exception as e:
                        RNS.log("Error while adding I2P Interface. The contained exception was: "+str(e))
                        self.interface_i2p = None

                if self.config["connect_rnode"]:
                    self.setstate("init.loadingstate", "Starting RNode")
                    try:
                        RNS.log("Adding RNode Interface...", RNS.LOG_DEBUG)
                        target_device = None
                        if len(self.owner_app.usb_devices) > 0:
                            # TODO: Add more intelligent selection here
                            target_device = self.owner_app.usb_devices[0]

                        # if target_device or self.config["hw_rnode_bluetooth"]:
                        if target_device != None:
                            target_port = target_device["port"]
                        else:
                            target_port = None
                    
                        bt_device_name = None
                        rnode_allow_bluetooth = False
                        if self.getpersistent("permissions.bluetooth"):
                            if self.config["hw_rnode_bluetooth"]:
                                RNS.log("Allowing RNode bluetooth", RNS.LOG_DEBUG)
                                rnode_allow_bluetooth = True
                                if self.config["hw_rnode_bt_device"] != None:
                                    bt_device_name = self.config["hw_rnode_bt_device"]

                            else:
                                RNS.log("Disallowing RNode bluetooth since config is disabled", RNS.LOG_DEBUG)
                                rnode_allow_bluetooth = False
                        else:
                            RNS.log("Disallowing RNode bluetooth due to missing permission", RNS.LOG_DEBUG)
                            rnode_allow_bluetooth = False

                        if self.config["connect_rnode_ifac_netname"] == "":
                            ifac_netname = None
                        else:
                            ifac_netname = self.config["connect_rnode_ifac_netname"]

                        if self.config["connect_rnode_ifac_passphrase"] == "":
                            ifac_netkey = None
                        else:
                            ifac_netkey = self.config["connect_rnode_ifac_passphrase"]

                        rnodeinterface = RNS.Interfaces.Android.RNodeInterface.RNodeInterface(
                                RNS.Transport,
                                "RNodeInterface",
                                target_port,
                                frequency = self.config["hw_rnode_frequency"],
                                bandwidth = self.config["hw_rnode_bandwidth"],
                                txpower = self.config["hw_rnode_tx_power"],
                                sf = self.config["hw_rnode_spreading_factor"],
                                cr = self.config["hw_rnode_coding_rate"],
                                flow_control = None,
                                id_interval = self.config["hw_rnode_beaconinterval"],
                                id_callsign = self.config["hw_rnode_beacondata"],
                                allow_bluetooth = rnode_allow_bluetooth,
                                target_device_name = bt_device_name,
                            )

                        rnodeinterface.OUT = True

                        if RNS.Reticulum.transport_enabled():
                            if_mode = Interface.Interface.MODE_FULL
                            if self.config["connect_ifmode_rnode"] == "gateway":
                                if_mode = Interface.Interface.MODE_GATEWAY
                            elif self.config["connect_ifmode_rnode"] == "access point":
                                if_mode = Interface.Interface.MODE_ACCESS_POINT
                            elif self.config["connect_ifmode_rnode"] == "roaming":
                                if_mode = Interface.Interface.MODE_ROAMING
                            elif self.config["connect_ifmode_rnode"] == "boundary":
                                if_mode = Interface.Interface.MODE_BOUNDARY
                        else:
                            if_mode = None
                            
                        self.reticulum._add_interface(rnodeinterface, mode = if_mode, ifac_netname = ifac_netname, ifac_netkey = ifac_netkey)
                        self.interface_rnode = rnodeinterface

                        if rnodeinterface != None:
                            if len(rnodeinterface.hw_errors) > 0:
                                self.setpersistent("startup.errors.rnode", rnodeinterface.hw_errors[0])

                        if self.interface_rnode.online:
                            self.interface_rnode.display_image(sideband_fb_data)
                            self.interface_rnode.enable_external_framebuffer()
                        else:
                            self.interface_rnode.last_imagedata = sideband_fb_data

                    except Exception as e:
                        RNS.log("Error while adding RNode Interface. The contained exception was: "+str(e))
                        self.interface_rnode = None

                elif self.config["connect_serial"]:
                    self.setstate("init.loadingstate", "Starting Serial Interface")
                    try:
                        RNS.log("Adding Serial Interface...", RNS.LOG_DEBUG)

                        target_device = None
                        if len(self.owner_app.usb_devices) > 0:
                            # TODO: Add more intelligent selection here
                            target_device = self.owner_app.usb_devices[0]

                        if target_device:
                            if self.config["connect_serial_ifac_netname"] == "":
                                ifac_netname = None
                            else:
                                ifac_netname = self.config["connect_serial_ifac_netname"]

                            if self.config["connect_serial_ifac_passphrase"] == "":
                                ifac_netkey = None
                            else:
                                ifac_netkey = self.config["connect_serial_ifac_passphrase"]

                            serialinterface = RNS.Interfaces.Android.SerialInterface.SerialInterface(
                                RNS.Transport,
                                "SerialInterface",
                                target_device["port"],
                                self.config["hw_serial_baudrate"],
                                self.config["hw_serial_databits"],
                                self.config["hw_serial_parity"],
                                self.config["hw_serial_stopbits"],
                            )

                            serialinterface.OUT = True

                            if RNS.Reticulum.transport_enabled():
                                if_mode = Interface.Interface.MODE_FULL
                                if self.config["connect_ifmode_serial"] == "gateway":
                                    if_mode = Interface.Interface.MODE_GATEWAY
                                elif self.config["connect_ifmode_serial"] == "access point":
                                    if_mode = Interface.Interface.MODE_ACCESS_POINT
                                elif self.config["connect_ifmode_serial"] == "roaming":
                                    if_mode = Interface.Interface.MODE_ROAMING
                                elif self.config["connect_ifmode_serial"] == "boundary":
                                    if_mode = Interface.Interface.MODE_BOUNDARY
                            else:
                                if_mode = None
                                
                            self.reticulum._add_interface(serialinterface, mode = if_mode, ifac_netname = ifac_netname, ifac_netkey = ifac_netkey)
                            self.interface_serial = serialinterface

                    except Exception as e:
                        RNS.log("Error while adding Serial Interface. The contained exception was: "+str(e))
                        self.interface_serial = None

                elif self.config["connect_modem"]:
                    self.setstate("init.loadingstate", "Starting Radio Modem")
                    try:
                        RNS.log("Adding Modem Interface...", RNS.LOG_DEBUG)

                        target_device = None
                        if len(self.owner_app.usb_devices) > 0:
                            # TODO: Add more intelligent selection here
                            target_device = self.owner_app.usb_devices[0]

                        if target_device:
                            if self.config["connect_modem_ifac_netname"] == "":
                                ifac_netname = None
                            else:
                                ifac_netname = self.config["connect_modem_ifac_netname"]

                            if self.config["connect_modem_ifac_passphrase"] == "":
                                ifac_netkey = None
                            else:
                                ifac_netkey = self.config["connect_modem_ifac_passphrase"]

                            modeminterface = RNS.Interfaces.Android.KISSInterface.KISSInterface(
                                RNS.Transport,
                                "ModemInterface",
                                target_device["port"],
                                self.config["hw_modem_baudrate"],
                                self.config["hw_modem_databits"],
                                self.config["hw_modem_parity"],
                                self.config["hw_modem_stopbits"],
                                self.config["hw_modem_preamble"],
                                self.config["hw_modem_tail"],
                                self.config["hw_modem_persistence"],
                                self.config["hw_modem_slottime"],
                                False, # flow control
                                self.config["hw_modem_beaconinterval"],
                                self.config["hw_modem_beacondata"],
                            )

                            modeminterface.OUT = True

                            if RNS.Reticulum.transport_enabled():
                                if_mode = Interface.Interface.MODE_FULL
                                if self.config["connect_ifmode_modem"] == "gateway":
                                    if_mode = Interface.Interface.MODE_GATEWAY
                                elif self.config["connect_ifmode_modem"] == "access point":
                                    if_mode = Interface.Interface.MODE_ACCESS_POINT
                                elif self.config["connect_ifmode_modem"] == "roaming":
                                    if_mode = Interface.Interface.MODE_ROAMING
                                elif self.config["connect_ifmode_modem"] == "boundary":
                                    if_mode = Interface.Interface.MODE_BOUNDARY
                            else:
                                if_mode = None
                                
                            self.reticulum._add_interface(modeminterface, mode = if_mode, ifac_netname = ifac_netname, ifac_netkey = ifac_netkey)
                            self.interface_modem = modeminterface

                    except Exception as e:
                        RNS.log("Error while adding Modem Interface. The contained exception was: "+str(e))
                        self.interface_modem = None

        RNS.log("Reticulum started, activating LXMF...")
        self.setstate("init.loadingstate", "Activating LXMF Router")
        self.message_router = LXMF.LXMRouter(identity = self.identity, storagepath = self.lxmf_storage, autopeer = True)
        self.message_router.register_delivery_callback(self.lxmf_delivery)

        self.lxmf_destination = self.message_router.register_delivery_identity(self.identity, display_name=self.config["display_name"])
        self.lxmf_destination.set_default_app_data(self.get_display_name_bytes)

        self.rns_dir = RNS.Reticulum.configdir

        self.update_active_lxmf_propagation_node()

    def update_active_lxmf_propagation_node(self):
        if self.config["lxmf_propagation_node"] != None and self.config["lxmf_propagation_node"] != "":
            self.set_active_propagation_node(self.config["lxmf_propagation_node"])
        else:
            if self.config["last_lxmf_propagation_node"] != None and self.config["last_lxmf_propagation_node"] != "":
                self.set_active_propagation_node(self.config["last_lxmf_propagation_node"])
            else:
                self.set_active_propagation_node(None)

    def message_notification(self, message):
        if message.state == LXMF.LXMessage.FAILED and hasattr(message, "try_propagation_on_fail") and message.try_propagation_on_fail:
            RNS.log("Direct delivery of "+str(message)+" failed. Retrying as propagated message.", RNS.LOG_VERBOSE)
            message.try_propagation_on_fail = None
            message.delivery_attempts = 0
            del message.next_delivery_attempt
            message.packed = None
            message.desired_method = LXMF.LXMessage.PROPAGATED
            self._db_message_set_method(message.hash, LXMF.LXMessage.PROPAGATED)
            self.message_router.handle_outbound(message)
        else:
            self.lxm_ingest(message, originator=True)

    def paper_message(self, content, destination_hash):
        try:
            if content == "":
                raise ValueError("Message content cannot be empty")

            dest_identity = RNS.Identity.recall(destination_hash)
            dest = RNS.Destination(dest_identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery")
            source = self.lxmf_destination
            
            desired_method = LXMF.LXMessage.PAPER
            lxm = LXMF.LXMessage(dest, source, content, title="", desired_method=desired_method)

            self.lxm_ingest(lxm, originator=True)

            return True

        except Exception as e:
            RNS.log("Error while creating paper message: "+str(e), RNS.LOG_ERROR)
            return False

    def send_message(self, content, destination_hash, propagation):
        try:
            if content == "":
                raise ValueError("Message content cannot be empty")

            dest_identity = RNS.Identity.recall(destination_hash)
            dest = RNS.Destination(dest_identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery")
            source = self.lxmf_destination
            
            if propagation:
                desired_method = LXMF.LXMessage.PROPAGATED
            else:
                desired_method = LXMF.LXMessage.DIRECT

            lxm = LXMF.LXMessage(dest, source, content, title="", desired_method=desired_method)
            lxm.register_delivery_callback(self.message_notification)
            lxm.register_failed_callback(self.message_notification)

            if self.message_router.get_outbound_propagation_node() != None:
                lxm.try_propagation_on_fail = True

            self.message_router.handle_outbound(lxm)
            self.lxm_ingest(lxm, originator=True)

            return True

        except Exception as e:
            RNS.log("Error while sending message: "+str(e), RNS.LOG_ERROR)
            return False

    def new_conversation(self, dest_str, name = "", trusted = False):
        if len(dest_str) != RNS.Reticulum.TRUNCATED_HASHLENGTH//8*2:
            return False

        try:
            addr_b = bytes.fromhex(dest_str)
            self._db_create_conversation(addr_b, name, trusted)

        except Exception as e:
            RNS.log("Error while creating conversation: "+str(e), RNS.LOG_ERROR)
            return False

        return True

    def create_conversation(self, context_dest, name = None, trusted = False):
        try:
            self._db_create_conversation(context_dest, name, trusted)

        except Exception as e:
            RNS.log("Error while creating conversation: "+str(e), RNS.LOG_ERROR)
            return False

        return True

    def lxm_ingest_uri(self, uri):
        local_delivery_signal = "local_delivery_occurred"
        duplicate_signal = "duplicate_lxm"
        ingest_result = self.message_router.ingest_lxm_uri(
            uri,
            signal_local_delivery=local_delivery_signal,
            signal_duplicate=duplicate_signal
        )

        if ingest_result == False:
            response = "The URI contained no decodable messages"
        
        elif ingest_result == local_delivery_signal:
            response = "Message was decoded, decrypted successfully, and added to your conversation list."

        elif ingest_result == duplicate_signal:
            response = "The decoded message has already been processed by the LXMF Router, and will not be ingested again."
        
        else:
            # TODO: Add message to sneakernet queues
            response = "The decoded message was not addressed to your LXMF address, and has been discarded."

        self.setstate("lxm_uri_ingest.result", response)

    def lxm_ingest(self, message, originator = False):
        should_notify = False
        is_trusted = False

        if originator:
            context_dest = message.destination_hash
        else:
            context_dest = message.source_hash
            is_trusted = self.is_trusted(context_dest)

        if self._db_message(message.hash):
            RNS.log("Message exists, setting state to: "+str(message.state), RNS.LOG_DEBUG)
            self._db_message_set_state(message.hash, message.state)
        else:
            RNS.log("Message does not exist, saving", RNS.LOG_DEBUG)
            self._db_save_lxm(message, context_dest)

            if is_trusted:
                should_notify = True

        if self._db_conversation(context_dest) == None:
            self._db_create_conversation(context_dest)
            self.setstate("app.flags.new_conversations", True)

        if self.gui_display() == "messages_screen":
            if self.gui_conversation() != context_dest:
                self.unread_conversation(context_dest)
                self.setstate("app.flags.unread_conversations", True)
            else:
                if self.gui_foreground():
                    should_notify = False
        else:
            self.unread_conversation(context_dest)
            self.setstate("app.flags.unread_conversations", True)

            if RNS.vendor.platformutils.is_android():
                if self.gui_display() == "conversations_screen" and self.gui_foreground():
                    should_notify = False

        if self.is_client:
            should_notify = False

        if should_notify:
            nlen = 128
            text = message.content.decode("utf-8")
            notification_content = text[:nlen]
            if len(text) > nlen:
                text += "..."

            self.notify(title=self.peer_display_name(context_dest), content=notification_content, group="LXM", context_id=RNS.hexrep(context_dest, delimit=False))

    def start(self):
        self._db_clean_messages()
        self.__start_jobs_immediate()

        thread = threading.Thread(target=self.__start_jobs_deferred)
        thread.setDaemon(True)
        thread.start()

        self._db_setstate("core.started", True)
        RNS.log("Sideband Core "+str(self)+" started")

    def request_lxmf_sync(self, limit = None):
        if self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_IDLE or self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_COMPLETE:
            self.message_router.request_messages_from_propagation_node(self.identity, max_messages = limit)
            RNS.log("LXMF message sync requested from propagation node "+RNS.prettyhexrep(self.message_router.get_outbound_propagation_node())+" for "+str(self.identity))
            return True
        else:
            return False

    def cancel_lxmf_sync(self):
        if self.message_router.propagation_transfer_state != LXMF.LXMRouter.PR_IDLE:
            self.message_router.cancel_propagation_node_requests()

    def get_sync_progress(self):
        return self.message_router.propagation_transfer_progress

    def lxmf_delivery(self, message):
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp))
        signature_string = "Signature is invalid, reason undetermined"
        if message.signature_validated:
            signature_string = "Validated"
        else:
            if message.unverified_reason == LXMF.LXMessage.SIGNATURE_INVALID:
                signature_string = "Invalid signature"
            if message.unverified_reason == LXMF.LXMessage.SOURCE_UNKNOWN:
                signature_string = "Cannot verify, source is unknown"

        RNS.log("LXMF delivery "+str(time_string)+". "+str(signature_string)+".")

        try:
            self.lxm_ingest(message)
        except Exception as e:
            RNS.log("Error while ingesting LXMF message "+RNS.prettyhexrep(message.hash)+" to database: "+str(e))

    def get_display_name_bytes(self):
        return self.config["display_name"].encode("utf-8")

    def get_sync_status(self):
        if self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_IDLE:
            return "Idle"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_PATH_REQUESTED:
            return "Path requested"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_LINK_ESTABLISHING:
            return "Establishing link"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_LINK_ESTABLISHED:
            return "Link established"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_REQUEST_SENT:
            return "Sync request sent"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_RECEIVING:
            return "Receiving messages"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_RESPONSE_RECEIVED:
            return "Messages received"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_COMPLETE:
            new_msgs = self.message_router.propagation_transfer_last_result
            if new_msgs == 0:
                return "Done, no new messages"
            else:
                return "Downloaded "+str(new_msgs)+" new messages"
        else:
            return "Unknown"

    def cleanup(self):
        if RNS.vendor.platformutils.get_platform() == "android":
            if not self.reticulum.is_connected_to_shared_instance:
                RNS.Transport.detach_interfaces()

rns_config = """
[reticulum]
enable_transport = TRANSPORT_IS_ENABLED
share_instance = Yes
shared_instance_port = 37428
instance_control_port = 37429
panic_on_interface_error = No

[logging]
loglevel = 3

"""
