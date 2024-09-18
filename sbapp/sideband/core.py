import RNS
import LXMF
import threading
import os.path
import time
import struct
import sqlite3
import random
import shlex

import RNS.vendor.umsgpack as msgpack
import RNS.Interfaces.Interface as Interface

import multiprocessing.connection

from copy import deepcopy
from threading import Lock
from .res import sideband_fb_data
from .sense import Telemeter, Commands
from .plugins import SidebandCommandPlugin, SidebandServicePlugin, SidebandTelemetryPlugin

if RNS.vendor.platformutils.get_platform() == "android":
    import plyer
    from jnius import autoclass, cast
    # Squelch excessive method signature logging
    import jnius.reflect
    class redirect_log():
        def isEnabledFor(self, arg):
            return False
        def debug(self, arg):
            pass
    def mod(method, name, signature):
        pass
    jnius.reflect.log_method = mod
    jnius.reflect.log = redirect_log()
    ############################################
else:
    import sbapp.plyer as plyer

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
    TELEMETRY_INTERVAL = 60
    SERVICE_TELEMETRY_INTERVAL = 300

    IF_CHANGE_ANNOUNCE_MIN_INTERVAL = 3.5  # In seconds
    AUTO_ANNOUNCE_RANDOM_MIN        = 90   # In minutes
    AUTO_ANNOUNCE_RANDOM_MAX        = 300  # In minutes

    DEFAULT_APPEARANCE = ["account", [0,0,0,1], [1,1,1,1]]

    aspect_filter = "lxmf.delivery"
    def received_announce(self, destination_hash, announced_identity, app_data):
        # Add the announce to the directory announce
        # stream logger

        # This reformats the new v0.5.0 announce data back to the expected format
        # for Sidebands database and other handling functions.
        dn = LXMF.display_name_from_app_data(app_data)
        sc = LXMF.stamp_cost_from_app_data(app_data)
        app_data = b""
        if dn != None:
            app_data = dn.encode("utf-8")

        self.log_announce(destination_hash, app_data, dest_type=SidebandCore.aspect_filter, stamp_cost=sc)

    def __init__(self, owner_app, config_path = None, is_service=False, is_client=False, android_app_dir=None, verbose=False, owner_service=None, service_context=None, is_daemon=False, load_config_only=False):
        self.is_service = is_service
        self.is_client = is_client
        self.is_daemon = is_daemon
        self.msg_audio = None
        self.last_msg_audio = None
        self.ptt_playback_lock = threading.Lock()
        self.ui_recording = False
        self.db = None
        self.db_lock = threading.Lock()

        if not self.is_service and not self.is_client:
            self.is_standalone = True
        else:
            self.is_standalone = False

        self.log_verbose = verbose
        self.owner_app = owner_app
        self.reticulum = None
        self.webshare_server = None
        self.telemeter = None
        self.telemetry_running = False
        self.latest_telemetry = None
        self.latest_packed_telemetry = None
        self.telemetry_changes = 0
        self.pending_telemetry_send = False
        self.pending_telemetry_send_try = 0
        self.pending_telemetry_send_maxtries = 2
        self.telemetry_send_blocked_until = 0
        self.pending_telemetry_request = False
        self.telemetry_request_max_history = 7*24*60*60
        self.default_lxm_limit = 128*1000
        self.state_db = {}
        self.state_lock = Lock()
        self.rpc_connection = None
        self.service_stopped = False
        self.service_context = service_context
        self.owner_service = owner_service
        self.allow_service_dispatch = True
        self.version_str = ""

        if config_path == None:
            self.app_dir     = plyer.storagepath.get_home_dir()+"/.config/sideband"
            if self.app_dir.startswith("file://"):
                self.app_dir = self.app_dir.replace("file://", "")
        else:
            self.app_dir     = config_path

        self.cache_dir       = self.app_dir+"/cache"
        
        self.rns_configdir = None
        if RNS.vendor.platformutils.is_android():
            self.app_dir = android_app_dir+"/io.unsigned.sideband/files/"
            self.cache_dir = self.app_dir+"/cache"
            self.rns_configdir = self.app_dir+"/app_storage/reticulum"
            self.asset_dir     = self.app_dir+"/app/assets"
        elif RNS.vendor.platformutils.is_darwin():
            core_path          = os.path.abspath(__file__)
            self.asset_dir     = core_path.replace("/sideband/core.py", "/assets")
        elif RNS.vendor.platformutils.get_platform() == "linux":
            core_path          = os.path.abspath(__file__)
            self.asset_dir     = core_path.replace("/sideband/core.py", "/assets")
        elif RNS.vendor.platformutils.is_windows():
            core_path          = os.path.abspath(__file__)
            self.asset_dir     = core_path.replace("\\sideband\\core.py", "\\assets")
        else:
            self.asset_dir     = plyer.storagepath.get_application_dir()+"/sbapp/assets"

        self.map_cache         = self.cache_dir+"/maps"
        if not os.path.isdir(self.map_cache):
            os.makedirs(self.map_cache)

        self.rec_cache         = self.cache_dir+"/rec"
        if not os.path.isdir(self.rec_cache):
            os.makedirs(self.rec_cache)

        self.icon              = self.asset_dir+"/icon.png"
        self.icon_48           = self.asset_dir+"/icon_48.png"
        self.icon_32           = self.asset_dir+"/icon_32.png"
        self.icon_macos        = self.asset_dir+"/icon_macos.png"
        self.notification_icon = self.asset_dir+"/notification_icon.png"

        os.environ["TELEMETER_GEOID_PATH"] = os.path.join(self.asset_dir, "geoids")

        if not os.path.isdir(self.app_dir+"/app_storage"):
            os.makedirs(self.app_dir+"/app_storage")

        self.config_path   = self.app_dir+"/app_storage/sideband_config"
        self.identity_path = self.app_dir+"/app_storage/primary_identity"
        self.db_path       = self.app_dir+"/app_storage/sideband.db"
        self.lxmf_storage  = self.app_dir+"/app_storage/"
        self.log_dir       = self.app_dir+"/app_storage/"
        self.tmp_dir       = self.app_dir+"/app_storage/tmp"
        self.exports_dir   = self.app_dir+"/exports"
        self.webshare_dir  = "./share/"
        
        self.first_run     = True
        self.saving_configuration = False
        self.last_lxmf_announce = 0
        self.last_if_change_announce = 0
        self.interface_local_adding = False
        self.next_auto_announce = time.time() + 60*(random.random()*(SidebandCore.AUTO_ANNOUNCE_RANDOM_MAX-SidebandCore.AUTO_ANNOUNCE_RANDOM_MIN)+SidebandCore.AUTO_ANNOUNCE_RANDOM_MIN)

        try:
            if not os.path.isfile(self.config_path):
                self.__init_config()
                self.__load_config()
            else:
                try:
                    self.__load_config()
                except Exception as e:
                    self.__init_config()
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

        if load_config_only:
            return

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

        self.active_command_plugins = {}
        self.active_service_plugins = {}
        self.active_telemetry_plugins = {}
        if self.is_service or self.is_standalone:
            def load_job():
                time.sleep(1)
                self.__load_plugins()

            threading.Thread(target=load_job, daemon=True).start()

            if RNS.vendor.platformutils.is_linux():
                try:
                    if not self.is_daemon:
                        lde_level = RNS.LOG_DEBUG
                        RNS.log("Checking desktop integration...", lde_level)
                        local_share_dir = os.path.expanduser("~/.local/share")
                        app_entry_dir = os.path.expanduser("~/.local/share/applications")
                        icon_dir = os.path.expanduser("~/.local/share/icons/hicolor/512x512/apps")
                        de_filename = "io.unsigned.sideband.desktop"
                        de_source = self.asset_dir+"/"+de_filename
                        de_target = app_entry_dir+"/"+de_filename
                        icn_source = self.asset_dir+"/icon.png"
                        icn_target = icon_dir+"/io.unsigned.sideband.png"
                        if os.path.isdir(local_share_dir):
                            if not os.path.exists(app_entry_dir):
                                os.makedirs(app_entry_dir)

                            update_de = False
                            if not os.path.exists(de_target):
                                update_de = True
                            else:
                                included_de_version = ""
                                with open(de_source, "rb") as sde_file:
                                    included_de_version = sde_file.readline()
                                existing_de_version = None
                                with open(de_target, "rb") as de_file:
                                    existing_de_version = de_file.readline()

                                if included_de_version != existing_de_version:
                                    update_de = True
                                    RNS.log("Existing desktop entry doesn't match included, updating it", lde_level)
                                else:
                                    update_de = False
                                    RNS.log("Existing desktop entry matches included, not updating it", lde_level)

                            if update_de:
                                RNS.log("Setting up desktop integration...", lde_level)
                                import shutil
                                RNS.log("Installing menu entry to \""+str(de_target)+"\"...", lde_level)
                                shutil.copy(de_source, de_target)
                                if not os.path.exists(icon_dir):
                                    os.makedirs(icon_dir)
                                RNS.log("Installing icon to \""+str(icn_target)+"\"...", lde_level)
                                shutil.copy(icn_source, icn_target)
                            else:
                                RNS.log("Desktop integration is already set up", lde_level)

                except Exception as e:
                    RNS.log("An error occurred while setting up desktop integration: "+str(e), RNS.LOG_ERROR)
                    RNS.trace_exception(e)


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
        self.config["lxmf_ignore_unknown"] = False
        self.config["lxmf_sync_interval"] = 43200
        self.config["lxmf_require_stamps"] = False
        self.config["lxmf_inbound_stamp_cost"] = None
        self.config["last_lxmf_propagation_node"] = None
        self.config["nn_home_node"] = None
        self.config["print_command"] = "lp"
        self.config["eink_mode"] = False
        self.config["lxm_limit_1mb"] = True

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

        # Telemetry
        self.config["telemetry_enabled"] = False
        self.config["telemetry_icon"] = SidebandCore.DEFAULT_APPEARANCE[0]
        self.config["telemetry_send_to_trusted"] = False
        self.config["telemetry_send_to_collector"] = False

        if not os.path.isfile(self.db_path):
            self.__db_init()
        else:
            self._db_initstate()
            self._db_initpersistent()
            self._db_inittelemetry()
            self._db_upgradetables()

        self.__save_config()

    def clear_map_cache(self):
        for entry in os.scandir(self.map_cache):
            os.unlink(entry.path)
            
    def get_map_cache_size(self):
        total = 0
        for entry in os.scandir(self.map_cache):
            if entry.is_dir(follow_symlinks=False):
                pass
            else:
                total += entry.stat(follow_symlinks=False).st_size
        return total

    def should_persist_data(self):
        if self.reticulum != None:
            self.reticulum._should_persist_data()

        self.save_configuration()

    def __load_config(self):
        RNS.log("Loading Sideband identity...", RNS.LOG_DEBUG)
        self.identity = RNS.Identity.from_file(self.identity_path)

        self.rpc_addr = ("127.0.0.1", 48165)
        self.rpc_key  = RNS.Identity.full_hash(self.identity.get_private_key())

        RNS.log("Loading Sideband configuration... "+str(self.config_path), RNS.LOG_DEBUG)
        config_file = open(self.config_path, "rb")
        self.config = msgpack.unpackb(config_file.read())
        config_file.close()

        # Migration actions from earlier config formats
        if not "debug" in self.config:
            self.config["debug"] = False
        if not "dark_ui" in self.config:
            self.config["dark_ui"] = True
        if not "advanced_stats" in self.config:
            self.config["advanced_stats"] = False
        if not "lxmf_periodic_sync" in self.config:
            self.config["lxmf_periodic_sync"] = False
        if not "lxmf_ignore_unknown" in self.config:
            self.config["lxmf_ignore_unknown"] = False
        if not "lxmf_sync_interval" in self.config:
            self.config["lxmf_sync_interval"] = 43200
        if not "lxmf_try_propagation_on_fail" in self.config:
            self.config["lxmf_try_propagation_on_fail"] = True
        if not "lxmf_require_stamps" in self.config:
            self.config["lxmf_require_stamps"] = False
        if not "lxmf_ignore_invalid_stamps" in self.config:
            self.config["lxmf_ignore_invalid_stamps"] = True
        if not "lxmf_inbound_stamp_cost" in self.config:
            self.config["lxmf_inbound_stamp_cost"] = None
        if not "notifications_on" in self.config:
            self.config["notifications_on"] = True
        if not "print_command" in self.config:
            self.config["print_command"] = "lp"
        if not "eink_mode" in self.config:
            self.config["eink_mode"] = False
        if not "display_style_in_contact_list" in self.config:
            self.config["display_style_in_contact_list"] = False
        if not "lxm_limit_1mb" in self.config:
            self.config["lxm_limit_1mb"] = True

        if not "input_language" in self.config:
            self.config["input_language"] = None
        if not "allow_predictive_text" in self.config:
            self.config["allow_predictive_text"] = False

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
        if not "hw_rnode_enable_framebuffer" in self.config:
            self.config["hw_rnode_enable_framebuffer"] = False
        if not "hw_rnode_bt_device" in self.config:
            self.config["hw_rnode_bt_device"] = None
        if not "hw_rnode_atl_short" in self.config:
            self.config["hw_rnode_atl_short"] = None
        if not "hw_rnode_atl_long" in self.config:
            self.config["hw_rnode_atl_long"] = None

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

        if not "telemetry_enabled" in self.config:
            self.config["telemetry_enabled"] = False
        if not "telemetry_collector" in self.config:
            self.config["telemetry_collector"] = None
        if not "telemetry_send_to_trusted" in self.config:
            self.config["telemetry_send_to_trusted"] = False
        if not "telemetry_send_to_collector" in self.config:
            self.config["telemetry_send_to_collector"] = False
        if not "telemetry_request_from_collector" in self.config:
            self.config["telemetry_request_from_collector"] = False
        if not "telemetry_send_interval" in self.config:
            self.config["telemetry_send_interval"] = 43200
        if not "telemetry_request_interval" in self.config:
            self.config["telemetry_request_interval"] = 43200
        if not "telemetry_collector_enabled" in self.config:
            self.config["telemetry_collector_enabled"] = False

        if not "telemetry_icon" in self.config:
            self.config["telemetry_icon"] = SidebandCore.DEFAULT_APPEARANCE[0]
        if not "telemetry_fg" in self.config:
            self.config["telemetry_fg"] = SidebandCore.DEFAULT_APPEARANCE[1]
        if not "telemetry_bg" in self.config:
            self.config["telemetry_bg"] = SidebandCore.DEFAULT_APPEARANCE[2]
        if not "telemetry_send_appearance" in self.config:
            self.config["telemetry_send_appearance"] = False
        if not "telemetry_display_trusted_only" in self.config:
            self.config["telemetry_display_trusted_only"] = False
        if not "display_style_from_all" in self.config:
            self.config["display_style_from_all"] = False
        if not "telemetry_receive_trusted_only" in self.config:
            self.config["telemetry_receive_trusted_only"] = False

        if not "telemetry_send_all_to_collector" in self.config:
            self.config["telemetry_send_all_to_collector"] = False
        if not "telemetry_use_propagation_only" in self.config:
            self.config["telemetry_use_propagation_only"] = False
        if not "telemetry_try_propagation_on_fail" in self.config:
            self.config["telemetry_try_propagation_on_fail"] = True
        if not "telemetry_requests_only_send_latest" in self.config:
            self.config["telemetry_requests_only_send_latest"] = True
        if not "telemetry_allow_requests_from_trusted" in self.config:
            self.config["telemetry_allow_requests_from_trusted"] = False
        if not "telemetry_allow_requests_from_anyone" in self.config:
            self.config["telemetry_allow_requests_from_anyone"] = False

        if not "telemetry_s_location" in self.config:
            self.config["telemetry_s_location"] = False
        if not "telemetry_s_battery" in self.config:
            self.config["telemetry_s_battery"] = False
        if not "telemetry_s_pressure" in self.config:
            self.config["telemetry_s_pressure"] = False
        if not "telemetry_s_temperature" in self.config:
            self.config["telemetry_s_temperature"] = False
        if not "telemetry_s_humidity" in self.config:
            self.config["telemetry_s_humidity"] = False
        if not "telemetry_s_magnetic_field" in self.config:
            self.config["telemetry_s_magnetic_field"] = False
        if not "telemetry_s_ambient_light" in self.config:
            self.config["telemetry_s_ambient_light"] = False
        if not "telemetry_s_gravity" in self.config:
            self.config["telemetry_s_gravity"] = False
        if not "telemetry_s_angular_velocity" in self.config:
            self.config["telemetry_s_angular_velocity"] = False
        if not "telemetry_s_acceleration" in self.config:
            self.config["telemetry_s_acceleration"] = False
        if not "telemetry_s_proximity" in self.config:
            self.config["telemetry_s_proximity"] = False
        if not "telemetry_s_fixed_location" in self.config:
            self.config["telemetry_s_fixed_location"] = False
        if not "telemetry_s_fixed_latlon" in self.config:
            self.config["telemetry_s_fixed_latlon"] = [0.0, 0.0]
        if not "telemetry_s_fixed_altitude" in self.config:
            self.config["telemetry_s_fixed_altitude"] = 0.0
        if not "telemetry_s_information" in self.config:
            self.config["telemetry_s_information"] = False
        if not "telemetry_s_information_text" in self.config:
            self.config["telemetry_s_information_text"] = ""

        if not "service_plugins_enabled" in self.config:
            self.config["service_plugins_enabled"] = False
        if not "command_plugins_enabled" in self.config:
            self.config["command_plugins_enabled"] = False
        if not "command_plugins_path" in self.config:
            self.config["command_plugins_path"] = None

        if not "map_history_limit" in self.config:
            self.config["map_history_limit"] = 7*24*60*60
        if not "map_lat" in self.config:
            self.config["map_lat"] = 0.0
        if not "map_lon" in self.config:
            self.config["map_lon"] = 0.0
        if not "map_zoom" in self.config:
            self.config["map_zoom"] = 3
        if not "map_storage_external" in self.config:
            self.config["map_storage_external"] = False
        if not "map_use_offline" in self.config:
            self.config["map_use_offline"] = False
        if not "map_use_online" in self.config:
            self.config["map_use_online"] = True
        if not "map_layer" in self.config:
            self.config["map_layer"] = None
        
        if not "map_storage_path" in self.config:
            self.config["map_storage_path"] = None
        if not "map_storage_file" in self.config:
            self.config["map_storage_file"] = None

        # Make sure we have a database
        if not os.path.isfile(self.db_path):
            self.__db_init()
        else:
            self._db_initstate()
            self._db_initpersistent()
            self._db_inittelemetry()
            self._db_upgradetables()
            self.__db_indices()

    def __reload_config(self):
        RNS.log("Reloading Sideband configuration... ", RNS.LOG_DEBUG)
        with open(self.config_path, "rb") as config_file:
            config_data = config_file.read()

        try:
            unpacked_config = msgpack.unpackb(config_data)
            if unpacked_config != None and len(unpacked_config) != 0:
                self.config = unpacked_config
                self.update_active_lxmf_propagation_node()
                self.update_ignore_invalid_stamps()
        except Exception as e:
            RNS.log("Error while reloading configuration: "+str(e), RNS.LOG_ERROR)

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

    def __load_plugins(self):
        plugins_path = self.config["command_plugins_path"]
        command_plugins_enabled = self.config["command_plugins_enabled"] == True
        service_plugins_enabled = self.config["service_plugins_enabled"] == True
        plugins_enabled = service_plugins_enabled
        
        if plugins_enabled:
            if plugins_path != None:
                RNS.log("Loading Sideband plugins...", RNS.LOG_DEBUG)
                if os.path.isdir(plugins_path):
                    for file in os.listdir(plugins_path):
                        if file.lower().endswith(".py"):
                            plugin_globals = {}
                            plugin_globals["SidebandServicePlugin"] = SidebandServicePlugin
                            plugin_globals["SidebandCommandPlugin"] = SidebandCommandPlugin
                            plugin_globals["SidebandTelemetryPlugin"] = SidebandTelemetryPlugin
                            RNS.log("Loading plugin \""+str(file)+"\"", RNS.LOG_NOTICE)
                            plugin_path = os.path.join(plugins_path, file)
                            exec(open(plugin_path).read(), plugin_globals)
                            plugin_class = plugin_globals["plugin_class"]
                            
                            if plugin_class != None:
                                plugin = plugin_class(self)
                                plugin.start()

                                if plugin.is_running():
                                    if issubclass(type(plugin), SidebandCommandPlugin) and command_plugins_enabled:
                                        command_name = plugin.command_name
                                        if not command_name in self.active_command_plugins:
                                            self.active_command_plugins[command_name] = plugin
                                            RNS.log("Registered "+str(plugin)+" as handler for command \""+str(command_name)+"\"", RNS.LOG_NOTICE)
                                        else:
                                            RNS.log("Could not register "+str(plugin)+" as handler for command \""+str(command_name)+"\". Command name was already registered", RNS.LOG_ERROR)
                                    
                                    elif issubclass(type(plugin), SidebandServicePlugin):
                                        service_name = plugin.service_name
                                        if not service_name in self.active_service_plugins:
                                            self.active_service_plugins[service_name] = plugin
                                            RNS.log("Registered "+str(plugin)+" for service \""+str(service_name)+"\"", RNS.LOG_NOTICE)
                                        else:
                                            RNS.log("Could not register "+str(plugin)+" for service \""+str(service_name)+"\". Service name was already registered", RNS.LOG_ERROR)
                                            try:
                                                plugin.stop()
                                            except Exception as e:
                                                pass
                                            del plugin

                                    elif issubclass(type(plugin), SidebandTelemetryPlugin):
                                        plugin_name = plugin.plugin_name
                                        if not plugin_name in self.active_telemetry_plugins:
                                            self.active_telemetry_plugins[plugin_name] = plugin
                                            RNS.log("Registered "+str(plugin)+" as telemetry plugin \""+str(plugin_name)+"\"", RNS.LOG_NOTICE)
                                        else:
                                            RNS.log("Could not register "+str(plugin)+" as telemetry plugin \""+str(plugin_name)+"\". Telemetry type was already registered", RNS.LOG_ERROR)
                                            try:
                                                plugin.stop()
                                            except Exception as e:
                                                pass
                                            del plugin

                                    else:
                                        RNS.log("Unknown plugin type was loaded, ignoring it.", RNS.LOG_ERROR)
                                        try:
                                            plugin.stop()
                                        except Exception as e:
                                            pass
                                        del plugin

                                else:
                                    RNS.log("Plugin "+str(plugin)+" failed to start, ignoring it.", RNS.LOG_ERROR)
                                    del plugin


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
        if not self.is_daemon:
            if RNS.vendor.platformutils.is_linux():
                from sbapp.ui.helpers import strip_emojis
                title = strip_emojis(title)
                content = strip_emojis(content)

        
            if self.config["notifications_on"]:
                if RNS.vendor.platformutils.is_android():
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

    def log_announce(self, dest, app_data, dest_type, stamp_cost=None):
        try:
            if app_data == None:
                app_data = b""
            app_data = msgpack.packb([app_data, stamp_cost])
            RNS.log("Received "+str(dest_type)+" announce for "+RNS.prettyhexrep(dest)+" with data: "+str(app_data), RNS.LOG_DEBUG)
            self._db_save_announce(dest, app_data, dest_type)
            self.setstate("app.flags.new_announces", True)

        except Exception as e:
            RNS.log("Exception while decoding LXMF destination announce data:"+str(e))

    def list_conversations(self, conversations=True, objects=False):
        result = self._db_conversations(conversations, objects)
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

    def is_trusted(self, context_dest, conv_data = None):
        try:
            if conv_data == None:
                existing_conv = self._db_conversation(context_dest)
            else:
                existing_conv = conv_data

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

    def is_object(self, context_dest, conv_data = None):
        try:
            if conv_data == None:
                existing_conv = self._db_conversation(context_dest)
            else:
                existing_conv = conv_data

            if existing_conv != None:
                data_dict = existing_conv["data"]
                if data_dict != None:
                    if "is_object" in data_dict:
                        return data_dict["is_object"]

            return False

        except Exception as e:
            RNS.log("Error while checking trust for "+RNS.prettyhexrep(context_dest)+": "+str(e), RNS.LOG_ERROR)
            return False

    def ptt_enabled(self, context_dest, conv_data = None):
        try:
            if conv_data == None:
                existing_conv = self._db_conversation(context_dest)
            else:
                existing_conv = conv_data

            if existing_conv != None:
                data_dict = existing_conv["data"]
                if data_dict != None:
                    if "ptt_enabled" in data_dict:
                        return data_dict["ptt_enabled"]

            return False

        except Exception as e:
            RNS.log("Error while checking PTT-enabled for "+RNS.prettyhexrep(context_dest)+": "+str(e), RNS.LOG_ERROR)
            return False

    def should_send_telemetry(self, context_dest, conv_data=None):
        try:
            if self.config["telemetry_enabled"]:
                if conv_data == None:
                    existing_conv = self._db_conversation(context_dest)
                else:
                    existing_conv = conv_data

                if existing_conv != None:
                    cd = existing_conv["data"]
                    if cd != None and "telemetry" in cd and cd["telemetry"] == True:
                        return True
                    else:
                        if self.is_trusted(context_dest, conv_data=existing_conv) and self.config["telemetry_send_to_trusted"]:
                            return True
                        else:
                            return False
                else:
                    return False

            else:
                return False

        except Exception as e:
            RNS.log("Error while checking telemetry sending for "+RNS.prettyhexrep(context_dest)+": "+str(e), RNS.LOG_ERROR)
            return False

    def allow_request_from(self, context_dest):
        try:
            if self.config["telemetry_allow_requests_from_anyone"] == True:
                return True

            if self.config["telemetry_allow_requests_from_trusted"] == True:
                existing_conv = self._db_conversation(context_dest)
                return existing_conv["trust"] == 1

            return self.requests_allowed_from(context_dest)
        
        except Exception as e:
            RNS.log("Error while checking request permissions for "+RNS.prettyhexrep(context_dest)+": "+str(e), RNS.LOG_ERROR)
            return False

    def requests_allowed_from(self, context_dest, conv_data=None):
        try:
            if conv_data == None:
                existing_conv = self._db_conversation(context_dest)
            else:
                existing_conv = conv_data

            if existing_conv != None:
                cd = existing_conv["data"]
                if cd != None and "allow_requests" in cd and cd["allow_requests"] == True:
                    return True
                else:
                    return False
            else:
                return False

        except Exception as e:
            RNS.log("Error while checking request permissions for "+RNS.prettyhexrep(context_dest)+": "+str(e), RNS.LOG_ERROR)
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

    def peer_appearance(self, context_dest, conv=None):
        appearance = self._db_get_appearance(context_dest, conv=conv)
        if appearance == None:
            return SidebandCore.DEFAULT_APPEARANCE
        for e in appearance:
            if e == None:
                return SidebandCore.DEFAULT_APPEARANCE
        return appearance

    def peer_display_name(self, context_dest):
        if context_dest == self.lxmf_destination.hash:
            return self.config["display_name"]
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
                            return LXMF.display_name_from_app_data(app_data)
                        else:
                            return LXMF.display_name_from_app_data(app_data)+" "+RNS.prettyhexrep(context_dest)
                    else:
                        return RNS.prettyhexrep(context_dest)
            else:
                app_data = RNS.Identity.recall_app_data(context_dest)
                if app_data != None:
                    name_str = LXMF.display_name_from_app_data(app_data)
                    addr_str = RNS.prettyhexrep(context_dest)
                    return name_str+" "+addr_str
                else:
                    return "Anonymous Peer "+RNS.prettyhexrep(context_dest)


        except Exception as e:
            RNS.log("Could not decode a valid peer name from data: "+str(e), RNS.LOG_DEBUG)
            return RNS.prettyhexrep(context_dest)

    def clear_conversation(self, context_dest):
        self._db_clear_conversation(context_dest)

    def clear_telemetry(self, context_dest):
        self._db_clear_telemetry(context_dest)

    def delete_announce(self, context_dest):
        self._db_delete_announce(context_dest)

    def delete_conversation(self, context_dest):
        self._db_clear_conversation(context_dest)
        self._db_clear_telemetry(context_dest)
        self._db_delete_conversation(context_dest)

    def delete_message(self, message_hash):
        self._db_delete_message(message_hash)

    def read_conversation(self, context_dest):
        self._db_conversation_set_unread(context_dest, False)

    def unread_conversation(self, context_dest, tx=False):
        self._db_conversation_set_unread(context_dest, True, tx=tx)

    def txtime_conversation(self, context_dest):
        self._db_conversation_update_txtime(context_dest)

    def trusted_conversation(self, context_dest):
        self._db_conversation_set_trusted(context_dest, True)

    def untrusted_conversation(self, context_dest):
        self._db_conversation_set_trusted(context_dest, False)

    def conversation_set_object(self, context_dest, is_object):
        self._db_conversation_set_object(context_dest, is_object)

    def conversation_set_ptt_enabled(self, context_dest, ptt_enabled):
        self._db_conversation_set_ptt_enabled(context_dest, ptt_enabled)

    def send_telemetry_in_conversation(self, context_dest):
        self._db_conversation_set_telemetry(context_dest, True)

    def no_telemetry_in_conversation(self, context_dest):
        self._db_conversation_set_telemetry(context_dest, False)

    def allow_requests_from(self, context_dest):
        self._db_conversation_set_requests(context_dest, True)

    def disallow_requests_from(self, context_dest):
        self._db_conversation_set_requests(context_dest, False)

    def named_conversation(self, name, context_dest):
        self._db_conversation_set_name(context_dest, name)

    def count_messages(self, context_dest):
        result = self._db_message_count(context_dest)
        if result != None:
            return result
        else:
            return None

    def outbound_telemetry_finished(self, message):
        if message.state == LXMF.LXMessage.FAILED and hasattr(message, "try_propagation_on_fail") and message.try_propagation_on_fail:
            RNS.log("Direct delivery of telemetry update "+str(message)+" failed. Retrying as propagated message.", RNS.LOG_VERBOSE)
            message.try_propagation_on_fail = None
            message.delivery_attempts = 0
            del message.next_delivery_attempt
            message.packed = None
            message.desired_method = LXMF.LXMessage.PROPAGATED
            self.message_router.handle_outbound(message)
        else:
            if message.state == LXMF.LXMessage.DELIVERED:
                self.setpersistent(f"telemetry.{RNS.hexrep(message.destination_hash, delimit=False)}.last_send_success_timebase", message.telemetry_timebase)
                self.setstate(f"telemetry.{RNS.hexrep(message.destination_hash, delimit=False)}.update_sending", False)
                if message.destination_hash == self.config["telemetry_collector"]:
                    self.pending_telemetry_send = False
                    self.pending_telemetry_send_try = 0
                    self.telemetry_send_blocked_until = 0
            else:
                self.setstate(f"telemetry.{RNS.hexrep(message.destination_hash, delimit=False)}.update_sending", False)


    def telemetry_request_finished(self, message):
        if message.state == LXMF.LXMessage.FAILED and hasattr(message, "try_propagation_on_fail") and message.try_propagation_on_fail:
            RNS.log("Direct delivery of telemetry request "+str(message)+" failed. Retrying as propagated message.", RNS.LOG_VERBOSE)
            message.try_propagation_on_fail = None
            message.delivery_attempts = 0
            del message.next_delivery_attempt
            message.packed = None
            message.desired_method = LXMF.LXMessage.PROPAGATED
            self.message_router.handle_outbound(message)
        else:
            if message.state == LXMF.LXMessage.DELIVERED:
                self.setpersistent(f"telemetry.{RNS.hexrep(message.destination_hash, delimit=False)}.last_request_success_timebase", message.request_timebase)
                self.setstate(f"telemetry.{RNS.hexrep(message.destination_hash, delimit=False)}.request_sending", False)
                if message.destination_hash == self.config["telemetry_collector"]:
                    self.pending_telemetry_request = False
                    self.pending_telemetry_request_try = 0
                    self.telemetry_request_blocked_until = 0
            else:
                self.setstate(f"telemetry.{RNS.hexrep(message.destination_hash, delimit=False)}.request_sending", False)

    def _service_request_latest_telemetry(self, from_addr=None):
        if not RNS.vendor.platformutils.is_android():
            return False
        else:
            if self.is_client:
                try:
                    if self.rpc_connection == None:
                        self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)

                    self.rpc_connection.send({"request_latest_telemetry": {"from_addr": from_addr}})
                    response = self.rpc_connection.recv()
                    return response
                
                except Exception as e:
                    RNS.log("Error while requesting latest telemetry over RPC: "+str(e), RNS.LOG_DEBUG)
                    RNS.trace_exception(e)
                    return False
            else:
                return False

    def request_latest_telemetry(self, from_addr=None):
        if self.allow_service_dispatch and self.is_client:
            try:
                return self._service_request_latest_telemetry(from_addr)

            except Exception as e:
                RNS.log("Error requesting latest telemetry: "+str(e), RNS.LOG_ERROR)
                RNS.trace_exception(e)
                return "not_sent"

        else:            
            if from_addr == None or from_addr == self.lxmf_destination.hash:
                return "no_address"
            else:
                if self.getstate(f"telemetry.{RNS.hexrep(from_addr, delimit=False)}.request_sending") == True:
                    RNS.log("Not sending new telemetry request, since an earlier transfer is already in progress", RNS.LOG_DEBUG)
                    return "in_progress"

                if from_addr != None:
                    dest_identity = RNS.Identity.recall(from_addr)
                    
                    if dest_identity == None:
                        RNS.log("The identity for "+RNS.prettyhexrep(from_addr)+" could not be recalled. Requesting identity from network...", RNS.LOG_DEBUG)
                        RNS.Transport.request_path(from_addr)
                        return "destination_unknown"

                    else:
                        now = time.time()
                        dest = RNS.Destination(dest_identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery")
                        source = self.lxmf_destination
                        
                        if self.config["telemetry_use_propagation_only"] == True:
                            desired_method = LXMF.LXMessage.PROPAGATED
                        else:
                            desired_method = LXMF.LXMessage.DIRECT

                        request_timebase = self.getpersistent(f"telemetry.{RNS.hexrep(from_addr, delimit=False)}.timebase") or now - self.telemetry_request_max_history
                        lxm_fields = { LXMF.FIELD_COMMANDS: [
                            {Commands.TELEMETRY_REQUEST: request_timebase},
                        ]}

                        lxm = LXMF.LXMessage(dest, source, "", desired_method=desired_method, fields = lxm_fields, include_ticket=True)
                        lxm.request_timebase = request_timebase
                        lxm.register_delivery_callback(self.telemetry_request_finished)
                        lxm.register_failed_callback(self.telemetry_request_finished)

                        if self.message_router.get_outbound_propagation_node() != None:
                            if self.config["telemetry_try_propagation_on_fail"]:
                                lxm.try_propagation_on_fail = True

                        RNS.log(f"Sending telemetry request with timebase {request_timebase}", RNS.LOG_DEBUG)
                        self.setpersistent(f"telemetry.{RNS.hexrep(from_addr, delimit=False)}.last_request_attempt", time.time())
                        self.setstate(f"telemetry.{RNS.hexrep(from_addr, delimit=False)}.request_sending", True)
                        self.message_router.handle_outbound(lxm)
                        return "sent"

                else:
                    return "not_sent"

    def _service_send_latest_telemetry(self, to_addr=None, stream=None, is_authorized_telemetry_request=False):
        if not RNS.vendor.platformutils.is_android():
            return False
        else:
            if self.is_client:
                try:
                    if self.rpc_connection == None:
                        self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)

                    self.rpc_connection.send({"send_latest_telemetry": {
                        "to_addr": to_addr,
                        "stream": stream,
                        "is_authorized_telemetry_request": is_authorized_telemetry_request}
                    })
                    response = self.rpc_connection.recv()
                    return response
                
                except Exception as e:
                    RNS.log("Error while sending latest telemetry over RPC: "+str(e), RNS.LOG_DEBUG)
                    RNS.trace_exception(e)
                    return False
            else:
                return False

    def send_latest_telemetry(self, to_addr=None, stream=None, is_authorized_telemetry_request=False):
        if self.allow_service_dispatch and self.is_client:
            try:
                return self._service_send_latest_telemetry(to_addr, stream, is_authorized_telemetry_request)

            except Exception as e:
                RNS.log("Error requesting latest telemetry: "+str(e), RNS.LOG_ERROR)
                RNS.trace_exception(e)
                return "not_sent"

        else:
            if to_addr == None or to_addr == self.lxmf_destination.hash:
                return "no_address"
            else:
                if to_addr == self.config["telemetry_collector"]:
                    is_authorized_telemetry_request = True

                if self.getstate(f"telemetry.{RNS.hexrep(to_addr, delimit=False)}.update_sending") == True:
                    RNS.log("Not sending new telemetry update, since an earlier transfer is already in progress", RNS.LOG_DEBUG)
                    return "in_progress"

                if (self.latest_packed_telemetry != None and self.latest_telemetry != None) or stream != None:
                    dest_identity = RNS.Identity.recall(to_addr)
                    
                    if dest_identity == None:
                        RNS.log("The identity for "+RNS.prettyhexrep(to_addr)+" could not be recalled. Requesting identity from network...", RNS.LOG_DEBUG)
                        RNS.Transport.request_path(to_addr)
                        return "destination_unknown"

                    else:
                        dest = RNS.Destination(dest_identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery")
                        source = self.lxmf_destination
                        
                        if self.config["telemetry_use_propagation_only"] == True:
                            desired_method = LXMF.LXMessage.PROPAGATED
                        else:
                            desired_method = LXMF.LXMessage.DIRECT

                        lxm_fields = self.get_message_fields(to_addr, is_authorized_telemetry_request=is_authorized_telemetry_request, signal_already_sent=True)
                        if lxm_fields == False and stream == None:
                            return "already_sent"

                        if stream != None and len(stream) > 0:
                            if lxm_fields == False:
                                lxm_fields = {}
                            lxm_fields[LXMF.FIELD_TELEMETRY_STREAM] = stream

                        if lxm_fields != None and lxm_fields != False and (LXMF.FIELD_TELEMETRY in lxm_fields or LXMF.FIELD_TELEMETRY_STREAM in lxm_fields):
                            if LXMF.FIELD_TELEMETRY in lxm_fields:
                                telemeter = Telemeter.from_packed(lxm_fields[LXMF.FIELD_TELEMETRY])
                                telemetry_timebase = telemeter.read_all()["time"]["utc"]
                            elif LXMF.FIELD_TELEMETRY_STREAM in lxm_fields:
                                telemetry_timebase = 0
                                for te in lxm_fields[LXMF.FIELD_TELEMETRY_STREAM]:
                                    ts = te[1]
                                    telemetry_timebase = max(telemetry_timebase, ts)

                            if telemetry_timebase > (self.getpersistent(f"telemetry.{RNS.hexrep(to_addr, delimit=False)}.last_send_success_timebase") or 0):
                                lxm = LXMF.LXMessage(dest, source, "", desired_method=desired_method, fields = lxm_fields, include_ticket=self.is_trusted(to_addr))
                                lxm.telemetry_timebase = telemetry_timebase
                                lxm.register_delivery_callback(self.outbound_telemetry_finished)
                                lxm.register_failed_callback(self.outbound_telemetry_finished)

                                if self.message_router.get_outbound_propagation_node() != None:
                                    if self.config["telemetry_try_propagation_on_fail"]:
                                        lxm.try_propagation_on_fail = True

                                RNS.log(f"Sending telemetry update with timebase {telemetry_timebase}", RNS.LOG_DEBUG)

                                self.setpersistent(f"telemetry.{RNS.hexrep(to_addr, delimit=False)}.last_send_attempt", time.time())
                                self.setstate(f"telemetry.{RNS.hexrep(to_addr, delimit=False)}.update_sending", True)
                                self.message_router.handle_outbound(lxm)
                                return "sent"
                            
                            else:
                                RNS.log(f"Telemetry update with timebase {telemetry_timebase} was already successfully sent", RNS.LOG_DEBUG)
                                return "already_sent"
                        else:
                            return "nothing_to_send"

                else:
                    RNS.log("A telemetry update was requested, but there was nothing to send.", RNS.LOG_WARNING)
                    return "nothing_to_send"


    def list_telemetry(self, context_dest = None, after = None, before = None, limit = None):
        return self._db_telemetry(context_dest = context_dest, after = after, before = before, limit = limit) or []

    def peer_telemetry(self, context_dest, after = None, before = None, limit = None):
        if context_dest == self.lxmf_destination.hash and limit == 1:
            try:
                if self.latest_telemetry != None and self.latest_packed_telemetry != None:
                    return [[self.latest_telemetry["time"]["utc"], self.latest_packed_telemetry]]
                else:
                    return []

            except Exception as e:
                RNS.log("An error occurred while retrieving telemetry from the database: "+str(e), RNS.LOG_ERROR)
                return []

        try:
            pts = self._db_telemetry(context_dest, after = after, before = before, limit = limit)
            if pts != None:
                if context_dest in pts:
                    return pts[context_dest]
        except Exception as e:
            RNS.log("An error occurred while retrieving telemetry from the database: "+str(e), RNS.LOG_ERROR)

        return []

    def owm_location(self):
        return self.peer_location(self.lxmf_destination.hash)

    def peer_location(self, context_dest):
        if context_dest == None:
            return None

        if context_dest == self.lxmf_destination.hash:
            try:
                if self.latest_telemetry != None:
                    lt = self.latest_telemetry
                    if "location" in lt and lt["location"] != None:
                        l = lt["location"]
                        if "latitude" in l and "longitude" in l:
                            if l["latitude"] != None and l["longitude"] != None:
                                return l
                return None

            except Exception as e:
                RNS.log("Error while getting own location: "+str(e), RNS.LOG_ERROR)

        after_time = time.time()-3*30*24*60*60
        pts = self.peer_telemetry(context_dest, after=after_time)
        for pt in pts:
            try:
                t = Telemeter.from_packed(pt[1]).read_all()
                if "location" in t and t["location"] != None:
                    l = t["location"]
                    if "latitude" in l and "longitude" in l:
                        if l["latitude"] != None and l["longitude"] != None:
                            return l
            except:
                pass

        return None

    def list_messages(self, context_dest, after = None, before = None, limit = None):
        result = self._db_messages(context_dest, after, before, limit)
        if result != None:
            return result
        else:
            return []

    def service_available(self):
        heartbeat_stale_time = 7.5
        now = time.time()
        service_heartbeat = self.getstate("service.heartbeat")
        if not service_heartbeat:
            RNS.log("No service heartbeat available at "+str(now), RNS.LOG_DEBUG)
            return False
        else:
            try:
                if now - service_heartbeat > heartbeat_stale_time:
                    RNS.log("Stale service heartbeat at "+str(now)+", retrying...", RNS.LOG_DEBUG)
                    now = time.time()
                    service_heartbeat = self.getstate("service.heartbeat")
                    if now - service_heartbeat > heartbeat_stale_time:
                        RNS.log("Service heartbeat did not recover after retry", RNS.LOG_DEBUG)
                        return False
                    else:
                        RNS.log("Service heartbeat recovered at"+str(time), RNS.LOG_DEBUG)
                        return True
                else:
                    return True
            except Exception as e:
                RNS.log("Error while getting service heartbeat: "+str(e), RNS.LOG_ERROR)
                RNS.log("Response was: "+str(service_heartbeat), RNS.LOG_ERROR)
                return False

    def gui_foreground(self):
        return self.getstate("app.foreground")

    def gui_display(self):
        return self.getstate("app.displaying")

    def gui_conversation(self):
        return self.getstate("app.active_conversation")

    def setstate(self, prop, val):
        with self.state_lock:
            if not self.service_stopped:
                if not RNS.vendor.platformutils.is_android():
                    self.state_db[prop] = val
                    return True
                else:
                    if self.is_service:
                        self.state_db[prop] = val
                        return True
                    else:
                        def set():
                            if self.rpc_connection == None:
                                self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)
                            self.rpc_connection.send({"setstate": (prop, val)})
                            response = self.rpc_connection.recv()
                            return response

                        try:
                            set()
                        except Exception as e:
                            RNS.log("Error while setting state over RPC: "+str(e)+". Retrying once.", RNS.LOG_DEBUG)
                            try:
                                set()
                            except Exception as e:
                                RNS.log("Error on retry as well: "+str(e)+". Giving up.", RNS.LOG_DEBUG)
                                return False

    def service_set_latest_telemetry(self, latest_telemetry, latest_packed_telemetry):
        if not RNS.vendor.platformutils.is_android():
            pass
        else:
            if self.is_service:
                self.latest_telemetry = latest_telemetry
                self.latest_packed_telemetry = latest_packed_telemetry
                return True
            else:
                try:
                    if self.rpc_connection == None:
                        self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)
                    self.rpc_connection.send({"latest_telemetry": (latest_telemetry, latest_packed_telemetry)})
                    response = self.rpc_connection.recv()
                    return response
                except Exception as e:
                    RNS.log("Error while setting telemetry over RPC: "+str(e), RNS.LOG_DEBUG)
                    return False

    def service_rpc_set_debug(self, debug):
        if not RNS.vendor.platformutils.is_android():
            pass
        else:
            if self.is_service:
                if debug:
                    RNS.loglevel = 6
                else:
                    RNS.loglevel = 2
                return True
            else:
                try:
                    if self.rpc_connection == None:
                        self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)
                    self.rpc_connection.send({"set_debug": debug})
                    response = self.rpc_connection.recv()
                    return response
                except Exception as e:
                    RNS.log("Error while setting log level over RPC: "+str(e), RNS.LOG_DEBUG)
                    return False

    def service_rpc_set_ui_recording(self, recording):
        if not RNS.vendor.platformutils.is_android():
            pass
        else:
            if self.is_service:
                self.ui_recording = recording
                return True
            else:
                try:
                    if self.rpc_connection == None:
                        self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)
                    self.rpc_connection.send({"set_ui_recording": recording})
                    response = self.rpc_connection.recv()
                    return response
                except Exception as e:
                    RNS.log("Error while setting UI recording status over RPC: "+str(e), RNS.LOG_DEBUG)
                    return False

    def getstate(self, prop, allow_cache=False):
        with self.state_lock:
            if not self.service_stopped:

                if not RNS.vendor.platformutils.is_android():
                    if prop in self.state_db:
                        return self.state_db[prop]
                    else:
                        return None
                else:
                    if self.is_service:
                        if prop in self.state_db:
                            return self.state_db[prop]
                        else:
                            return None
                    else:
                        try:
                            if self.rpc_connection == None:
                                self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)
                            self.rpc_connection.send({"getstate": prop})
                            response = self.rpc_connection.recv()
                            return response

                        except Exception as e:
                            RNS.log("Error while retrieving state "+str(prop)+" over RPC: "+str(e), RNS.LOG_DEBUG)
                            self.rpc_connection = None
                            return None

    def _get_plugins_info(self):
        np = 0
        plugins_info_text = ""
        for name in self.active_service_plugins:
            np += 1
            plugins_info_text += f"\n- Service Plugin [b]{name}[/b]"
        for name in self.active_telemetry_plugins:
            np += 1
            plugins_info_text += f"\n- Telemetry Plugin [b]{name}[/b]"
        for name in self.active_command_plugins:
            np += 1
            plugins_info_text += f"\n- Command Plugin [b]{name}[/b]"
        if np == 0:
            plugins_info_text = "[i]No plugins are currently loaded[/i]"
        elif np == 1:
            plugins_info_text = "Currently, 1 plugin is loaded and active:\n" + plugins_info_text
        else:
            plugins_info_text = f"Currently, {np} plugins are loaded and active:\n" + plugins_info_text
        return plugins_info_text

    def get_plugins_info(self):
        if not RNS.vendor.platformutils.is_android():
            return self._get_plugins_info()
        else:
            if self.is_service:
                return self._get_plugins_info()
            else:
                try:
                    if self.rpc_connection == None:
                        self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)
                    self.rpc_connection.send({"get_plugins_info": True})
                    response = self.rpc_connection.recv()
                    return response
                except Exception as e:
                    ed = "Error while getting plugins info over RPC: "+str(e)
                    RNS.log(ed, RNS.LOG_DEBUG)
                    return ed

    def _get_destination_establishment_rate(self, destination_hash):
        try:
            mr = self.message_router
            oh = destination_hash
            ol = None
            if oh in mr.direct_links:
                ol = mr.direct_links[oh]
            elif oh in mr.backchannel_links:
                ol = mr.backchannel_links[oh]

            if ol != None:
                ler = ol.get_establishment_rate()
                if ler:
                    return ler

            return None

        except Exception as e:
            RNS.trace_exception(e)
            return None

    def get_destination_establishment_rate(self, destination_hash):
        if not RNS.vendor.platformutils.is_android():
            return self._get_destination_establishment_rate(destination_hash)
        else:
            if self.is_service:
                return self._get_destination_establishment_rate(destination_hash)
            else:
                try:
                    if self.rpc_connection == None:
                        self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)
                    self.rpc_connection.send({"get_destination_establishment_rate": destination_hash})
                    response = self.rpc_connection.recv()
                    return response
                except Exception as e:
                    ed = "Error while getting destination link etablishment rate over RPC: "+str(e)
                    RNS.log(ed, RNS.LOG_DEBUG)
                    return None

    def __start_rpc_listener(self):
        try:
            RNS.log("Starting RPC listener", RNS.LOG_DEBUG)
            self.rpc_listener = multiprocessing.connection.Listener(self.rpc_addr, authkey=self.rpc_key)
            thread = threading.Thread(target=self.__rpc_loop)
            thread.daemon = True
            thread.start()
        except Exception as e:
            RNS.log("Could not start RPC listener on "+str(self.rpc_addr)+". Terminating now. Clear up anything using the port and try again.", RNS.LOG_ERROR)
            RNS.panic()

    def __rpc_loop(self):
        while True:
            try:
                RNS.log("Ready for next RPC client", RNS.LOG_DEBUG)
                rpc_connection = self.rpc_listener.accept()
                RNS.log("Accepted RPC client", RNS.LOG_DEBUG)
                
                def job_factory(connection):
                    def rpc_client_job():
                        try:
                            while connection:
                                call = connection.recv()
                                if "getstate" in call:
                                    prop = call["getstate"]
                                    connection.send(self.getstate(prop))
                                elif "setstate" in call:
                                    prop, val = call["setstate"]
                                    connection.send(self.setstate(prop, val))
                                elif "latest_telemetry" in call:
                                    t,p = call["latest_telemetry"]
                                    self.latest_telemetry = t
                                    self.latest_packed_telemetry = p
                                    connection.send(True)
                                elif "set_debug" in call:
                                    self.service_rpc_set_debug(call["set_debug"])
                                    connection.send(True)
                                elif "set_ui_recording" in call:
                                    self.service_rpc_set_ui_recording(call["set_ui_recording"])
                                    connection.send(True)
                                elif "get_plugins_info" in call:
                                    connection.send(self._get_plugins_info())
                                elif "get_destination_establishment_rate" in call:
                                    connection.send(self._get_destination_establishment_rate(call["get_destination_establishment_rate"]))
                                elif "send_message" in call:
                                    args = call["send_message"]
                                    send_result = self.send_message(
                                        args["content"],
                                        args["destination_hash"],
                                        args["propagation"],
                                        skip_fields=args["skip_fields"],
                                        no_display=args["no_display"],
                                        attachment=args["attachment"],
                                        image=args["image"],
                                        audio=args["audio"])
                                    connection.send(send_result)
                                elif "send_command" in call:
                                    args = call["send_command"]
                                    send_result = self.send_command(
                                        args["content"],
                                        args["destination_hash"],
                                        args["propagation"])
                                    connection.send(send_result)
                                elif "request_latest_telemetry" in call:
                                    args = call["request_latest_telemetry"]
                                    send_result = self.request_latest_telemetry(args["from_addr"])
                                    connection.send(send_result)
                                elif "send_latest_telemetry" in call:
                                    args = call["send_latest_telemetry"]
                                    send_result = self.send_latest_telemetry(
                                        to_addr=args["to_addr"],
                                        stream=args["stream"],
                                        is_authorized_telemetry_request=args["is_authorized_telemetry_request"]
                                    )
                                    connection.send(send_result)
                                elif "get_lxm_progress" in call:
                                    args = call["get_lxm_progress"]
                                    connection.send(self.get_lxm_progress(args["lxm_hash"]))
                                else:
                                    connection.send(None)

                        except Exception as e:
                            RNS.log("Error on client RPC connection: "+str(e), RNS.LOG_ERROR)
                            try:
                                connection.close()
                            except:
                                pass

                    return rpc_client_job

                threading.Thread(target=job_factory(rpc_connection), daemon=True).start()

            except Exception as e:
                RNS.log("An error ocurred while handling RPC call from local client: "+str(e), RNS.LOG_ERROR)


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
            self.db = sqlite3.connect(self.db_path, check_same_thread=False, timeout=15.0)

        return self.db

    def __db_reconnect(self):
        if self.db != None:
            try:
                self.db.close()
            except Exception as e:
                RNS.log("Error while closing database for reconnect. The contained exception was:", RNS.LOG_ERROR)
                RNS.trace_exception(e)
        self.db = None
        return self.__db_connect()

    def __db_init(self):
        db = self.__db_connect()
        dbc = db.cursor()

        dbc.execute("DROP TABLE IF EXISTS lxm")
        dbc.execute("CREATE TABLE lxm (lxm_hash BLOB PRIMARY KEY, dest BLOB, source BLOB, title BLOB, tx_ts INTEGER, rx_ts INTEGER, state INTEGER, method INTEGER, t_encrypted INTEGER, t_encryption INTEGER, data BLOB, extra BLOB)")

        dbc.execute("DROP TABLE IF EXISTS conv")
        dbc.execute("CREATE TABLE conv (dest_context BLOB PRIMARY KEY, last_tx INTEGER, last_rx INTEGER, unread INTEGER, type INTEGER, trust INTEGER, name BLOB, data BLOB)")

        dbc.execute("DROP TABLE IF EXISTS announce")
        dbc.execute("CREATE TABLE announce (id PRIMARY KEY, received INTEGER, source BLOB, data BLOB, dest_type BLOB)")

        dbc.execute("DROP TABLE IF EXISTS telemetry")
        dbc.execute("CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY, dest_context BLOB, ts INTEGER, data BLOB)")

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

    def _db_inittelemetry(self):
        db = self.__db_connect()
        dbc = db.cursor()

        dbc.execute("CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY, dest_context BLOB, ts INTEGER, data BLOB)")
        db.commit()

    def _db_upgradetables(self):
        # TODO: Remove this again at some point in the future
        db = self.__db_connect()
        dbc = db.cursor()
        dbc.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'lxm' AND sql LIKE '%extra%'")
        result = dbc.fetchall()
        if len(result) == 0:
            dbc.execute("ALTER TABLE lxm ADD COLUMN extra BLOB")
        db.commit()

    def _db_initstate(self):
        # db = self.__db_connect()
        # dbc = db.cursor()

        # dbc.execute("DROP TABLE IF EXISTS state")
        # dbc.execute("CREATE TABLE state (property BLOB PRIMARY KEY, value BLOB)")
        # db.commit()
        self.setstate("database_ready", True)

    def _db_initpersistent(self):
        db = self.__db_connect()
        dbc = db.cursor()

        dbc.execute("CREATE TABLE IF NOT EXISTS persistent (property BLOB PRIMARY KEY, value BLOB)")
        db.commit()

    def _db_getpersistent(self, prop):
        with self.db_lock:
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
        existing_prop = self._db_getpersistent(prop)

        with self.db_lock:
            try:
                db = self.__db_connect()
                dbc = db.cursor()
                uprop = prop.encode("utf-8")
                bval = msgpack.packb(val)

                if existing_prop == None:
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

    def _db_conversation_update_txtime(self, context_dest, is_retry = False):
        with self.db_lock:
            try:
                db = self.__db_connect()
                dbc = db.cursor()

                query = "UPDATE conv set last_tx = ? where dest_context = ?"
                data = (time.time(), context_dest)

                dbc.execute(query, data)
                result = dbc.fetchall()
                db.commit()
            except Exception as e:
                RNS.log("An error occurred while updating conversation TX time: "+str(e), RNS.LOG_ERROR)
                self.__db_reconnect()
                # if not is_retry:
                #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                #     self._db_conversation_update_txtime(context_dest, is_retry=True)

    def _db_conversation_set_unread(self, context_dest, unread, tx = False, is_retry = False):
        with self.db_lock:
            try:
                db = self.__db_connect()
                dbc = db.cursor()
                
                if unread:
                    if tx:
                        query = "UPDATE conv set unread = ?, last_tx = ? where dest_context = ?"
                        data = (unread, time.time(), context_dest)
                    else:
                        query = "UPDATE conv set unread = ?, last_rx = ? where dest_context = ?"
                        data = (unread, time.time(), context_dest)
                else:
                    query = "UPDATE conv set unread = ? where dest_context = ?"
                    data = (unread, context_dest)

                dbc.execute(query, data)
                result = dbc.fetchall()
                db.commit()
            except Exception as e:
                RNS.log("An error occurred while updating conversation unread flag: "+str(e), RNS.LOG_ERROR)
                self.__db_reconnect()
                # if not is_retry:
                #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                #     self._db_conversation_set_unread(context_dest, unread, tx, is_retry=True)

    def _db_telemetry(self, context_dest = None, after = None, before = None, limit = None):
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()

            limit_part = ""
            if limit:
                limit_part = " LIMIT "+str(int(limit))
            order_part = " order by ts DESC"+limit_part
            if context_dest == None:
                if after != None and before == None:
                    query = "select * from telemetry where ts>:after_ts"+order_part
                    dbc.execute(query, {"after_ts": after})
                elif after == None and before != None:
                    query = "select * from telemetry where ts<:before_ts"+order_part
                    dbc.execute(query, {"before_ts": before})
                elif after != None and before != None:
                    query = "select * from telemetry where ts<:before_ts and ts>:after_ts"+order_part
                    dbc.execute(query, {"before_ts": before, "after_ts": after})
                else:
                    query = query = "select * from telemetry"
                    dbc.execute(query, {})

            else:        
                if after != None and before == None:
                    query = "select * from telemetry where dest_context=:context_dest and ts>:after_ts"+order_part
                    dbc.execute(query, {"context_dest": context_dest, "after_ts": after})
                elif after == None and before != None:
                    query = "select * from telemetry where dest_context=:context_dest and ts<:before_ts"+order_part
                    dbc.execute(query, {"context_dest": context_dest, "before_ts": before})
                elif after != None and before != None:
                    query = "select * from telemetry where dest_context=:context_dest and ts<:before_ts and ts>:after_ts"+order_part
                    dbc.execute(query, {"context_dest": context_dest, "before_ts": before, "after_ts": after})
                else:
                    query = query = "select * from telemetry where dest_context=:context_dest"+order_part
                    dbc.execute(query, {"context_dest": context_dest})

            result = dbc.fetchall()

            if len(result) < 1:
                return None
            else:
                results = {}
                for entry in result:
                    telemetry_source = entry[1]
                    telemetry_timestamp = entry[2]
                    telemetry_data = entry[3]
                    
                    if not telemetry_source in results:
                        results[telemetry_source] = []

                    results[telemetry_source].append([telemetry_timestamp, telemetry_data])
                
                return results

    def _db_save_telemetry(self, context_dest, telemetry, physical_link = None, source_dest = None, via = None, is_retry = False):
        with self.db_lock:
            try:
                remote_telemeter = Telemeter.from_packed(telemetry)
                read_telemetry = remote_telemeter.read_all()
                telemetry_timestamp = read_telemetry["time"]["utc"]

                db = self.__db_connect()
                dbc = db.cursor()

                query = "select * from telemetry where dest_context=:ctx and ts=:tts"
                dbc.execute(query, {"ctx": context_dest, "tts": telemetry_timestamp})
                result = dbc.fetchall()

                if len(result) != 0:
                    RNS.log("Telemetry entry with source "+RNS.prettyhexrep(context_dest)+" and timestamp "+str(telemetry_timestamp)+" already exists, skipping save", RNS.LOG_DEBUG)
                    return None

                if physical_link != None and len(physical_link) != 0:
                    remote_telemeter.synthesize("physical_link")
                    if "rssi" in physical_link: remote_telemeter.sensors["physical_link"].rssi = physical_link["rssi"]
                    if "snr" in physical_link: remote_telemeter.sensors["physical_link"].snr = physical_link["snr"]
                    if "q" in physical_link: remote_telemeter.sensors["physical_link"].q = physical_link["q"]
                    remote_telemeter.sensors["physical_link"].update_data()
                    telemetry = remote_telemeter.packed()

                if source_dest != None:
                    remote_telemeter.synthesize("received")
                    remote_telemeter.sensors["received"].by = self.lxmf_destination.hash
                    remote_telemeter.sensors["received"].via = source_dest

                    rl = remote_telemeter.read("location")
                    if rl and "latitude" in rl and "longitude" in rl and "altitude" in rl:
                        if self.latest_telemetry != None and "location" in self.latest_telemetry:
                            ol = self.latest_telemetry["location"]
                            if ol != None:
                                if "latitude" in ol and "longitude" in ol and "altitude" in ol:
                                    olat = ol["latitude"]; olon = ol["longitude"]; oalt = ol["altitude"]
                                    rlat = rl["latitude"]; rlon = rl["longitude"]; ralt = rl["altitude"]
                                    if olat != None and olon != None and oalt != None:
                                        if rlat != None and rlon != None and ralt != None:
                                            remote_telemeter.sensors["received"].set_distance(
                                                (olat, olon, oalt), (rlat, rlon, ralt)
                                            )

                    remote_telemeter.sensors["received"].update_data()
                    telemetry = remote_telemeter.packed()

                if via != None:
                    if not "received" in remote_telemeter.sensors:
                        remote_telemeter.synthesize("received")

                    if "by" in remote_telemeter.sensors["received"].data:
                        remote_telemeter.sensors["received"].by = remote_telemeter.sensors["received"].data["by"]
                    if "distance" in remote_telemeter.sensors["received"].data:
                        remote_telemeter.sensors["received"].geodesic_distance = remote_telemeter.sensors["received"].data["distance"]["geodesic"]
                        remote_telemeter.sensors["received"].euclidian_distance = remote_telemeter.sensors["received"].data["distance"]["euclidian"]

                    remote_telemeter.sensors["received"].via = via
                    remote_telemeter.sensors["received"].update_data()
                    telemetry = remote_telemeter.packed()
                    
                query = "INSERT INTO telemetry (dest_context, ts, data) values (?, ?, ?)"
                data = (context_dest, telemetry_timestamp, telemetry)
                dbc.execute(query, data)

                try:
                    db.commit()
                except Exception as e:
                    RNS.log("An error occurred while commiting telemetry to database: "+str(e), RNS.LOG_ERROR)
                    self.__db_reconnect()
                    # if not is_retry:
                    #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                    #     self._db_save_telemetry(context_dest, telemetry, physical_link, source_dest, via, is_retry = True)
                    return

                self.setstate("app.flags.last_telemetry", time.time())

                return telemetry

            except Exception as e:
                import traceback
                exception_info = "".join(traceback.TracebackException.from_exception(e).format())
                RNS.log(f"A {str(type(e))} occurred while saving telemetry to database: {str(e)}", RNS.LOG_ERROR)
                RNS.log(exception_info, RNS.LOG_ERROR)
                self.db = None

    def _db_update_appearance(self, context_dest, timestamp, appearance, from_bulk_telemetry=False):
        conv = self._db_conversation(context_dest)

        if conv == None:
            ae = [appearance, int(time.time())]
            # TODO: Clean out these temporary values at some interval.
            # Probably expire after 14 days or so.
            self.setpersistent("temp.peer_appearance."+RNS.hexrep(context_dest, delimit=False), ae)
        
        else:
            with self.db_lock:
                data_dict = conv["data"]
                if data_dict == None:
                    data_dict = {}

                if not "appearance" in data_dict:
                    data_dict["appearance"] = None

                if from_bulk_telemetry and data_dict["appearance"] != SidebandCore.DEFAULT_APPEARANCE:
                    RNS.log("Aborting appearance update from bulk transfer, since conversation already has appearance set: "+str(appearance)+" / "+str(data_dict["appearance"]), RNS.LOG_DEBUG)
                    return

                if data_dict["appearance"] != appearance:
                    data_dict["appearance"] = appearance
                    packed_dict = msgpack.packb(data_dict)
                
                    db = self.__db_connect()
                    dbc = db.cursor()
                
                    query = "UPDATE conv set data = ? where dest_context = ?"
                    data = (packed_dict, context_dest)
                    dbc.execute(query, data)
                    result = dbc.fetchall()
                    db.commit()

    def _db_get_appearance(self, context_dest, conv = None, raw=False):
        if context_dest == self.lxmf_destination.hash:
            return [self.config["telemetry_icon"], self.config["telemetry_fg"], self.config["telemetry_bg"]]
        else:
            data_dict = None
            if conv != None:
                data_dict = conv["data"]

            else:
                conv = self._db_conversation(context_dest)
                if conv != None:
                    data_dict = conv["data"]
                else:
                    data_dict = {}

            if data_dict != None:
                if not "appearance" in data_dict or data_dict["appearance"] == None:
                    apd = self.getpersistent("temp.peer_appearance."+RNS.hexrep(context_dest, delimit=False))
                    if apd != None:
                        try:
                            data_dict["appearance"] = apd[0]
                        except Exception as e:
                            RNS.log("Could not get appearance data from database: "+str(e),RNS.LOG_ERROR)
                            data_dict = None

                try:
                    if data_dict != None and "appearance" in data_dict:
                        def htf(cbytes):
                            d = 1.0/255.0
                            r = round(struct.unpack("!B", bytes([cbytes[0]]))[0]*d, 4)
                            g = round(struct.unpack("!B", bytes([cbytes[1]]))[0]*d, 4)
                            b = round(struct.unpack("!B", bytes([cbytes[2]]))[0]*d, 4)
                            return [r,g,b]

                        if raw:
                            appearance = data_dict["appearance"]
                        else:
                            appearance = [data_dict["appearance"][0], htf(data_dict["appearance"][1]), htf(data_dict["appearance"][2])]
                        
                        return appearance
                except Exception as e:
                    RNS.log("Could not retrieve appearance for "+RNS.prettyhexrep(context_dest)+": "+str(e), RNS.LOG_ERROR)

        return None


    def _db_conversation_set_telemetry(self, context_dest, send_telemetry=False, is_retry = False):
        conv = self._db_conversation(context_dest)
        data_dict = conv["data"]
        if data_dict == None:
            data_dict = {}

        data_dict["telemetry"] = send_telemetry
        packed_dict = msgpack.packb(data_dict)
        
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()
            
            query = "UPDATE conv set data = ? where dest_context = ?"
            data = (packed_dict, context_dest)
            dbc.execute(query, data)
            result = dbc.fetchall()

            try:
                db.commit()
            except Exception as e:
                RNS.log("An error occurred while updating conversation telemetry options: "+str(e), RNS.LOG_ERROR)
                self.__db_reconnect()
                # if not is_retry:
                #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                #     self._db_conversation_set_telemetry(context_dest, send_telemetry, is_retry=True)

    def _db_conversation_set_requests(self, context_dest, allow_requests=False, is_retry=False):
        conv = self._db_conversation(context_dest)
        data_dict = conv["data"]
        if data_dict == None:
            data_dict = {}

        data_dict["allow_requests"] = allow_requests
        packed_dict = msgpack.packb(data_dict)
        
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()
            
            query = "UPDATE conv set data = ? where dest_context = ?"
            data = (packed_dict, context_dest)
            dbc.execute(query, data)
            result = dbc.fetchall()

            try:
                db.commit()
            except Exception as e:
                RNS.log("An error occurred while updating conversation request options: "+str(e), RNS.LOG_ERROR)
                self.__db_reconnect()
                if not is_retry:
                    RNS.log("Retrying operation...", RNS.LOG_ERROR)
                    self._db_conversation_set_requests(context_dest, allow_requests, is_retry=True)

    def _db_conversation_set_object(self, context_dest, is_object=False):
        conv = self._db_conversation(context_dest)
        data_dict = conv["data"]
        if data_dict == None:
            data_dict = {}

        data_dict["is_object"] = is_object
        packed_dict = msgpack.packb(data_dict)
        
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()
            
            query = "UPDATE conv set data = ? where dest_context = ?"
            data = (packed_dict, context_dest)
            dbc.execute(query, data)
            result = dbc.fetchall()

            try:
                db.commit()
            except Exception as e:
                RNS.log("An error occurred while updating conversation object option: "+str(e), RNS.LOG_ERROR)
                self.__db_reconnect()
                # if not is_retry:
                #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                #     self._db_conversation_set_object(context_dest, is_object, is_retry=True)

    def _db_conversation_set_ptt_enabled(self, context_dest, ptt_enabled=False):
        conv = self._db_conversation(context_dest)
        data_dict = conv["data"]
        if data_dict == None:
            data_dict = {}

        data_dict["ptt_enabled"] = ptt_enabled
        packed_dict = msgpack.packb(data_dict)
        
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()
            
            query = "UPDATE conv set data = ? where dest_context = ?"
            data = (packed_dict, context_dest)
            dbc.execute(query, data)
            result = dbc.fetchall()

            try:
                db.commit()
            except Exception as e:
                RNS.log("An error occurred while updating conversation PTT option: "+str(e), RNS.LOG_ERROR)
                self.__db_reconnect()
                # if not is_retry:
                #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                #     self._db_conversation_set_ptt_enabled(context_dest, ptt_enabled, is_retry=True)

    def _db_conversation_set_trusted(self, context_dest, trusted):
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()
            
            query = "UPDATE conv set trust = ? where dest_context = ?"
            data = (trusted, context_dest)
            dbc.execute(query, data)
            result = dbc.fetchall()

            try:
                db.commit()
            except Exception as e:
                RNS.log("An error occurred while updating conversation trusted option: "+str(e), RNS.LOG_ERROR)
                self.__db_reconnect()
                # if not is_retry:
                #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                #     self._db_conversation_set_trusted(context_dest, trusted, is_retry=True)

    def _db_conversation_set_name(self, context_dest, name):
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()
            
            query = "UPDATE conv set name=:name_data where dest_context=:ctx;"
            dbc.execute(query, {"ctx": context_dest, "name_data": name.encode("utf-8")})
            result = dbc.fetchall()
            
            try:
                db.commit()
            except Exception as e:
                RNS.log("An error occurred while updating conversation name option: "+str(e), RNS.LOG_ERROR)
                self.__db_reconnect()
                # if not is_retry:
                #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                #     self._db_conversation_set_name(context_dest, name, is_retry=True)

    def _db_conversations(self, conversations=True, objects=False):
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()
            
            dbc.execute("select * from conv")
            result = dbc.fetchall()

            if len(result) < 1:
                return None
            else:
                convs = []
                for entry in result:
                    is_object = False
                    last_rx = entry[1]
                    last_tx = entry[2]
                    last_activity = max(last_rx, last_tx)
                    data = None
                    try:
                        data = msgpack.unpackb(entry[7])
                        if "is_object" in data:
                            is_object = data["is_object"]
                    except:
                        pass

                    conv = {
                        "dest": entry[0],
                        "unread": entry[3],
                        "last_rx": last_rx,
                        "last_tx": last_tx,
                        "last_activity": last_activity,
                        "trust": entry[5],
                        "data": data,
                    }
                    should_add = False
                    if conversations and not is_object:
                        should_add = True
                    if objects and is_object:
                        should_add = True

                    if should_add:
                        convs.append(conv)

                return sorted(convs, key=lambda c: c["last_activity"], reverse=True)

    def _db_announces(self):
        with self.db_lock:
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
                            app_data = entry[3]
                            announce = {
                                "dest": entry[2],
                                "name": LXMF.display_name_from_app_data(app_data),
                                "cost": LXMF.stamp_cost_from_app_data(app_data),
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
        with self.db_lock:
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
                conv["last_activity"] = max(c[1], c[2])
                return conv

    def _db_clear_conversation(self, context_dest):
        RNS.log("Clearing conversation with "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()

            query = "delete from lxm where (dest=:ctx_dst or source=:ctx_dst);"
            dbc.execute(query, {"ctx_dst": context_dest})
            db.commit()

    def _db_clear_telemetry(self, context_dest):
        RNS.log("Clearing telemetry for "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()

            query = "delete from telemetry where dest_context=:ctx_dst;"
            dbc.execute(query, {"ctx_dst": context_dest})
            db.commit()

        self.setstate("app.flags.last_telemetry", time.time())

    def _db_delete_conversation(self, context_dest):
        RNS.log("Deleting conversation with "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()

            query = "delete from conv where (dest_context=:ctx_dst);"
            dbc.execute(query, {"ctx_dst": context_dest})
            db.commit()


    def _db_delete_announce(self, context_dest):
        RNS.log("Deleting announce with "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()

            query = "delete from announce where (source=:ctx_dst);"
            dbc.execute(query, {"ctx_dst": context_dest})
            db.commit()

    def _db_create_conversation(self, context_dest, name = None, trust = False):
        RNS.log("Creating conversation for "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()

            def_name = "".encode("utf-8")
            query = "INSERT INTO conv (dest_context, last_tx, last_rx, unread, type, trust, name, data) values (?, ?, ?, ?, ?, ?, ?, ?)"
            data = (context_dest, 0, time.time(), 0, SidebandCore.CONV_P2P, 0, def_name, msgpack.packb(None))

            dbc.execute(query, data)
            db.commit()

        if trust:
            self._db_conversation_set_trusted(context_dest, True)

        if name != None and name != "":
            self._db_conversation_set_name(context_dest, name)

        self.__event_conversations_changed()

    def _db_delete_message(self, msg_hash):
        RNS.log("Deleting message "+RNS.prettyhexrep(msg_hash))
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()

            query = "delete from lxm where (lxm_hash=:mhash);"
            dbc.execute(query, {"mhash": msg_hash})
            db.commit()

    def _db_clean_messages(self):
        RNS.log("Purging stale messages... "+str(self.db_path))
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()

            query = "delete from lxm where (state=:outbound_state or state=:sending_state);"
            dbc.execute(query, {"outbound_state": LXMF.LXMessage.OUTBOUND, "sending_state": LXMF.LXMessage.SENDING})
            db.commit()

    def _db_message_set_state(self, lxm_hash, state, is_retry=False, ratchet_id=None, originator_stamp=None):
        msg_extras = None
        if ratchet_id != None:
            try:
                msg = self._db_message(lxm_hash)
                if msg != None:
                    msg_extras = msg["extras"]

                if ratchet_id:
                    msg_extras["ratchet_id"] = ratchet_id

                if originator_stamp:
                    msg_extras["stamp_checked"] = False
                    msg_extras["stamp_raw"] = originator_stamp[0]
                    msg_extras["stamp_valid"] = originator_stamp[1]
                    msg_extras["stamp_value"] = originator_stamp[2]

            except Exception as e:
                RNS.log("An error occurred while getting message extras: "+str(e))

        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()

            if msg_extras != None:
                extras = msgpack.packb(msg_extras)
                query = "UPDATE lxm set state = ?, extra = ? where lxm_hash = ?"
                data = (state, extras, lxm_hash)
                
            else:
                query = "UPDATE lxm set state = ? where lxm_hash = ?"
                data = (state, lxm_hash)

            dbc.execute(query, data)

            try:
                db.commit()
                result = dbc.fetchall()
            except Exception as e:
                RNS.log("An error occurred while updating message state: "+str(e), RNS.LOG_ERROR)
                self.__db_reconnect()
                # if not is_retry:
                #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                #     self._db_message_set_state(lxm_hash, state, is_retry=True)

    def _db_message_set_method(self, lxm_hash, method):
        with self.db_lock:
            db = self.__db_connect()
            dbc = db.cursor()
            
            query = "UPDATE lxm set method = ? where lxm_hash = ?"
            data = (method, lxm_hash)
            dbc.execute(query, data)

            try:
                db.commit()
                result = dbc.fetchall()
            except Exception as e:
                RNS.log("An error occurred while updating message method: "+str(e), RNS.LOG_ERROR)
                self.__db_reconnect()
                # if not is_retry:
                #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                #     self._db_message_set_method(lxm_hash, method, is_retry=True)

    def message(self, msg_hash):
        return self._db_message(msg_hash)

    def _db_message(self, msg_hash):
        with self.db_lock:
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

                extras = None
                try:
                    extras = msgpack.unpackb(entry[11])
                except:
                    pass

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
                    "lxm": lxm,
                    "extras": extras,
                }
                return message

    def _db_message_count(self, context_dest):
        with self.db_lock:
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
        with self.db_lock:
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

                    extras = None
                    try:
                        extras = msgpack.unpackb(entry[11])
                    except:
                        pass
                    
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
                        "lxm": lxm,
                        "extras": extras,
                    }

                    messages.append(message)
                if len(messages) > limit:
                    messages = messages[-limit:]
                return messages

    def _db_save_lxm(self, lxm, context_dest, originator = False, own_command = False, is_retry = False):
        state = lxm.state

        packed_telemetry = None
        if not originator and lxm.fields != None:
            if self.config["telemetry_receive_trusted_only"] == False or (self.config["telemetry_receive_trusted_only"] == True and self.is_trusted(context_dest)):
                if LXMF.FIELD_ICON_APPEARANCE in lxm.fields:
                    peer_appearance = lxm.fields[LXMF.FIELD_ICON_APPEARANCE]
                    if peer_appearance != None and len(peer_appearance) > 0 and len(peer_appearance) < 96:
                        self._db_update_appearance(context_dest, lxm.timestamp, peer_appearance)

                if LXMF.FIELD_TELEMETRY in lxm.fields:
                    physical_link = {}
                    if lxm.rssi or lxm.snr or lxm.q:
                        physical_link["rssi"] = lxm.rssi
                        physical_link["snr"] = lxm.snr
                        physical_link["q"] = lxm.q
                    packed_telemetry = self._db_save_telemetry(context_dest, lxm.fields[LXMF.FIELD_TELEMETRY], physical_link=physical_link, source_dest=context_dest)

                if LXMF.FIELD_TELEMETRY_STREAM in lxm.fields:
                    max_timebase = self.getpersistent(f"telemetry.{RNS.hexrep(context_dest, delimit=False)}.timebase") or 0
                    if lxm.fields[LXMF.FIELD_TELEMETRY_STREAM] != None and len(lxm.fields[LXMF.FIELD_TELEMETRY_STREAM]) > 0:
                        for telemetry_entry in lxm.fields[LXMF.FIELD_TELEMETRY_STREAM]:
                            tsource = telemetry_entry[0]
                            ttstamp = telemetry_entry[1]
                            tpacked = telemetry_entry[2]
                            appearance = telemetry_entry[3]
                            max_timebase = max(max_timebase, ttstamp)
                            if self._db_save_telemetry(tsource, tpacked, via = context_dest):
                                RNS.log("Saved telemetry stream entry from "+RNS.prettyhexrep(tsource), RNS.LOG_DEBUG)
                                if appearance != None:
                                    self._db_update_appearance(tsource, ttstamp, appearance, from_bulk_telemetry=True)
                                    RNS.log("Updated appearance entry from "+RNS.prettyhexrep(tsource), RNS.LOG_DEBUG)

                        self.setpersistent(f"telemetry.{RNS.hexrep(context_dest, delimit=False)}.timebase", max_timebase)

                    else:
                        RNS.log("Received telemetry stream field with no data: "+str(lxm.fields[LXMF.FIELD_TELEMETRY_STREAM]), RNS.LOG_DEBUG)

        if own_command or len(lxm.content) != 0 or len(lxm.title) != 0:
            with self.db_lock:
                db = self.__db_connect()
                dbc = db.cursor()

                if not lxm.packed:
                    lxm.pack()

                if lxm.method == LXMF.LXMessage.PAPER:
                    packed_lxm = msgpack.packb([lxm.packed, lxm.paper_packed])
                else:
                    packed_lxm = lxm.packed

                extras = {}
                if lxm.rssi or lxm.snr or lxm.q:
                    extras["rssi"] = lxm.rssi
                    extras["snr"] = lxm.snr
                    extras["q"] = lxm.q

                if lxm.stamp_checked:
                    extras["stamp_checked"] = True
                    extras["stamp_valid"] = lxm.stamp_valid
                    extras["stamp_value"] = lxm.stamp_value
                    extras["stamp_raw"] = lxm.stamp

                if lxm.ratchet_id:
                    extras["ratchet_id"] = lxm.ratchet_id

                if packed_telemetry != None:
                    extras["packed_telemetry"] = packed_telemetry

                extras = msgpack.packb(extras)

                query = "INSERT INTO lxm (lxm_hash, dest, source, title, tx_ts, rx_ts, state, method, t_encrypted, t_encryption, data, extra) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
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
                    extras
                )

                dbc.execute(query, data)

                try:
                    db.commit()
                except Exception as e:
                    RNS.log("An error occurred while saving message to database: "+str(e), RNS.LOG_ERROR)
                    self.__db_reconnect()
                    # if not is_retry:
                    #     RNS.log("Retrying operation...", RNS.LOG_ERROR)
                    #     self._db_save_lxm(lxm, context_dest, originator = originator, own_command = own_command, is_retry = True)
                    # return

            self.__event_conversation_changed(context_dest)

    def _db_save_announce(self, destination_hash, app_data, dest_type="lxmf.delivery"):
        with self.db_lock:
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
            if self.config["lxmf_require_stamps"]:
                self.message_router.set_inbound_stamp_cost(self.lxmf_destination.hash, self.config["lxmf_inbound_stamp_cost"])
                self.message_router.announce(self.lxmf_destination.hash, attached_interface=attached_interface)
            else:
                self.message_router.set_inbound_stamp_cost(self.lxmf_destination.hash, None)
                self.lxmf_destination.announce(attached_interface=attached_interface)
            self.last_lxmf_announce = time.time()
            self.next_auto_announce = time.time() + 60*(random.random()*(SidebandCore.AUTO_ANNOUNCE_RANDOM_MAX-SidebandCore.AUTO_ANNOUNCE_RANDOM_MIN)+SidebandCore.AUTO_ANNOUNCE_RANDOM_MIN)
            RNS.log("Next auto announce in "+RNS.prettytime(self.next_auto_announce-time.time()), RNS.LOG_DEBUG)
            self.setstate("wants.announce", False)
        
        else:
            if self.config["lxmf_require_stamps"]:
                self.message_router.set_inbound_stamp_cost(self.lxmf_destination.hash, self.config["lxmf_inbound_stamp_cost"])
            else:
                self.message_router.set_inbound_stamp_cost(self.lxmf_destination.hash, None)
            
            self.setstate("wants.announce", True)

    def run_telemetry(self):
        if not self.telemetry_running:
            self.telemetry_running = True
            def telemetry_job():
                while self.telemetry_running:
                    self.update_telemetry()
                    time.sleep(SidebandCore.TELEMETRY_INTERVAL)

            threading.Thread(target=telemetry_job, daemon=True).start()

    def run_service_telemetry(self):
        if not self.telemetry_running:
            self.telemetry_running = True
            def telemetry_job():
                while self.telemetry_running:
                    try:
                        if self.owner_service._gps_started:
                            self.update_telemetry()
                    except Exception as e:
                        import traceback
                        exception_info = "".join(traceback.TracebackException.from_exception(e).format())
                        RNS.log(f"An {str(type(e))} occurred while updating service telemetry: {str(e)}", RNS.LOG_ERROR)
                        RNS.log(exception_info, RNS.LOG_ERROR)

                    time.sleep(SidebandCore.SERVICE_TELEMETRY_INTERVAL)

            threading.Thread(target=telemetry_job, daemon=True).start()

    def stop_telemetry(self):
        self.telemetry_running = False
        self.telemeter.stop_all()
        self.update_telemeter_config()
        self.setstate("app.flags.last_telemetry", time.time())

    def update_telemetry(self):
        try:
            try:
                latest_telemetry = deepcopy(self.latest_telemetry)
            except:
                latest_telemetry = None

            telemetry = self.get_telemetry()
            packed_telemetry = self.get_packed_telemetry()
            telemetry_changed = False

            if telemetry != None and packed_telemetry != None:
                if latest_telemetry == None or len(telemetry) != len(latest_telemetry):
                    telemetry_changed = True

                if latest_telemetry != None:

                    if not telemetry_changed:
                        for sn in telemetry:
                            if telemetry_changed:
                                break

                            if sn != "time":
                                if sn in latest_telemetry:
                                    if telemetry[sn] != latest_telemetry[sn]:
                                        telemetry_changed = True
                                else:
                                    telemetry_changed = True

                    if not telemetry_changed:
                        for sn in latest_telemetry:

                            if telemetry_changed:
                                break

                            if sn != "time":
                                if not sn in telemetry:
                                    telemetry_changed = True

                if telemetry_changed:
                    self.telemetry_changes += 1
                    self.latest_telemetry = telemetry
                    self.latest_packed_telemetry = packed_telemetry
                    self.setstate("app.flags.last_telemetry", time.time())

                    if self.is_client:
                        try:
                            self.service_set_latest_telemetry(self.latest_telemetry, self.latest_packed_telemetry)
                        except Exception as e:
                            RNS.log("Error while sending latest telemetry to service: "+str(e), RNS.LOG_ERROR)

        except Exception as e:
            import traceback
            exception_info = "".join(traceback.TracebackException.from_exception(e).format())
            RNS.log(f"An {str(type(e))} occurred while updating telemetry: {str(e)}", RNS.LOG_ERROR)
            RNS.log(exception_info, RNS.LOG_ERROR)

    def update_telemeter_config(self):
        if self.config["telemetry_enabled"] == True:
            if self.telemeter == None:
                if self.service_context == None:
                    self.telemeter = Telemeter()
                else:
                    self.telemeter = Telemeter(android_context=self.service_context, service=True, location_provider=self.owner_service)

            sensors = ["location", "information", "battery", "pressure", "temperature", "humidity", "magnetic_field", "ambient_light", "gravity", "angular_velocity", "acceleration", "proximity"]
            for sensor in sensors:
                if self.config["telemetry_s_"+sensor]:
                    self.telemeter.enable(sensor)
                else:
                    if sensor == "location":
                        if "location" in self.telemeter.sensors:
                            if self.telemeter.sensors["location"].active:
                                if self.telemeter.sensors["location"].synthesized:
                                    if not self.config["telemetry_s_fixed_location"]:
                                        self.telemeter.disable(sensor)
                                else:
                                    self.telemeter.disable(sensor)
                    else:
                        self.telemeter.disable(sensor)

            for telemetry_plugin in self.active_telemetry_plugins:
                try:
                    plugin = self.active_telemetry_plugins[telemetry_plugin]
                    plugin.update_telemetry(self.telemeter)

                except Exception as e:
                    RNS.log("An error occurred while "+str(telemetry_plugin)+" was handling telemetry. The contained exception was: "+str(e), RNS.LOG_ERROR)
                    RNS.trace_exception(e)
            
            if self.config["telemetry_s_fixed_location"]:
                self.telemeter.synthesize("location")
                self.telemeter.sensors["location"].latitude = self.config["telemetry_s_fixed_latlon"][0]
                self.telemeter.sensors["location"].longitude = self.config["telemetry_s_fixed_latlon"][1]
                self.telemeter.sensors["location"].altitude = self.config["telemetry_s_fixed_altitude"]
                self.telemeter.sensors["location"].stale_time = 12*60*60

                if time.time() > self.telemeter.sensors["location"].last_update + self.telemeter.sensors["location"].stale_time:
                    self.telemeter.sensors["location"].update_data()

            if self.config["telemetry_s_information"]:
                self.telemeter.synthesize("information")
                self.telemeter.sensors["information"].set_contents(self.config["telemetry_s_information_text"])

        else:
            self.telemeter = None
            self.latest_telemetry = None
            self.latest_packed_telemetry = None

    def get_telemetry(self):
        if self.config["telemetry_enabled"] == True:
            self.update_telemeter_config()
            if self.telemeter != None:
                return self.telemeter.read_all()
            else:
                return {}
        else:
            return {}

    def get_packed_telemetry(self):
        if self.config["telemetry_enabled"] == True:
            self.update_telemeter_config()
            if self.telemeter != None:
                packed = self.telemeter.packed()
                return packed
            else:
                return None
        else:
            return None

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

    def _update_delivery_limits(self):
        try:
            if self.config["lxm_limit_1mb"]:
                lxm_limit = 1000
            else:
                lxm_limit = self.default_lxm_limit
            if self.message_router.delivery_per_transfer_limit != lxm_limit:
                self.message_router.delivery_per_transfer_limit = lxm_limit
                RNS.log("Updated delivery limit to "+RNS.prettysize(self.message_router.delivery_per_transfer_limit*1000), RNS.LOG_DEBUG)
                
        except Exception as e:
            RNS.log("Error while updating LXMF router delivery limit: "+str(e), RNS.LOG_ERROR)

    def _service_jobs(self):
        if self.is_service:
            last_usb_discovery = time.time()
            last_multicast_lock_check = time.time()
            while True:
                time.sleep(SidebandCore.SERVICE_JOB_INTERVAL)
                now = time.time()
                needs_if_change_announce = False

                try:
                    if hasattr(self, "interface_local"):
                        if self.interface_local != None:
                            if self.interface_local.carrier_changed:
                                RNS.log("AutoInterface carrier change detected, retaking wake locks", RNS.LOG_DEBUG)
                                self.owner_service.take_locks(force_multicast=True)
                                self.interface_local.carrier_changed = False
                                last_multicast_lock_check = now
                                needs_if_change_announce = True
                                self.last_if_change_announce = 0

                        if (self.interface_local != None and len(self.interface_local.adopted_interfaces) == 0) or (self.config["connect_local"] and self.interface_local == None):
                            if not self.interface_local_adding:
                                RNS.log("No suitable interfaces on AutoInterface, scheduling re-init", RNS.LOG_DEBUG)
                                if self.interface_local in RNS.Transport.interfaces:
                                    RNS.Transport.interfaces.remove(self.interface_local)
                                del self.interface_local
                                self.interface_local = None
                                self.interface_local_adding = True
                                def job():
                                    self.__add_localinterface(delay=60)
                                    if self.config["start_announce"] == True:
                                        time.sleep(12)
                                        self.lxmf_announce(attached_interface=self.interface_local)
                                threading.Thread(target=job, daemon=True).start()

                    if (now - last_multicast_lock_check > 120):
                        RNS.log("Checking multicast and wake locks", RNS.LOG_DEBUG)
                        self.owner_service.take_locks()
                        last_multicast_lock_check = now

                except Exception as e:
                    import traceback
                    exception_info = "".join(traceback.TracebackException.from_exception(e).format())
                    RNS.log(f"An {str(type(e))} occurred while running interface checks: {str(e)}", RNS.LOG_ERROR)
                    RNS.log(exception_info, RNS.LOG_ERROR)

                announce_wanted = self.getstate("wants.announce")
                announce_attached_interface = None
                announce_delay = 0
                # TODO: The "start_announce" config entry should be
                # renamed to "auto_announce", which is its current
                # meaning.
                if self.config["start_announce"] == True:
                    if hasattr(self, "interface_local") and self.interface_local != None:
                        have_peers = len(self.interface_local.peers) > 0

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
                                    self.setstate("hardware_operation.error", "An error occurred while trying to communicate with the device. Please make sure that Sideband has been granted permissions to access the device.\n\nThe reported error was:\n\n[i]"+str(e)+"[/i]")
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
                if self.owner_service != None:
                    self.owner_service.update_location_provider()

                self._update_delivery_limits()

                if self.config["lxmf_periodic_sync"] == True:
                    if self.getpersistent("lxmf.lastsync") == None:
                        self.setpersistent("lxmf.lastsync", time.time())
                    else:
                        now = time.time()
                        syncinterval = self.config["lxmf_sync_interval"]
                        lastsync = self.getpersistent("lxmf.lastsync")
                        nextsync = lastsync+syncinterval

                        RNS.log("Last LXMF sync was "+RNS.prettytime(now-lastsync)+" ago", RNS.LOG_EXTREME)
                        RNS.log("Next LXMF sync is "+("in "+RNS.prettytime(nextsync-now) if nextsync-now > 0 else "now"), RNS.LOG_EXTREME)
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

                if self.config["telemetry_enabled"]:
                    if self.config["telemetry_send_to_collector"]:
                        if self.config["telemetry_collector"] != None and self.config["telemetry_collector"] != self.lxmf_destination.hash:
                            try:
                                now = time.time()
                                collector_address = self.config["telemetry_collector"]
                                last_send_timebase = self.getpersistent(f"telemetry.{RNS.hexrep(collector_address, delimit=False)}.last_send_success_timebase") or 0
                                send_interval = self.config["telemetry_send_interval"]
                                next_send = last_send_timebase+send_interval

                                scheduled = next_send-now; blocked = self.telemetry_send_blocked_until-now
                                next_send_in = max(scheduled, blocked)
                                RNS.log("Last telemetry send was "+RNS.prettytime(now-last_send_timebase)+" ago", RNS.LOG_EXTREME)
                                RNS.log("Next telemetry send is "+("in "+RNS.prettytime(next_send_in) if next_send_in > 0 else "now"), RNS.LOG_EXTREME)

                                if now > last_send_timebase+send_interval and now > self.telemetry_send_blocked_until:
                                    RNS.log("Initiating telemetry send to collector", RNS.LOG_DEBUG)
                                    if not self.pending_telemetry_send_try >= self.pending_telemetry_send_maxtries:
                                        self.pending_telemetry_send = True
                                        self.pending_telemetry_send_try += 1
                                        if self.config["telemetry_send_all_to_collector"]:
                                            last_timebase = (self.getpersistent(f"telemetry.{RNS.hexrep(collector_address, delimit=False)}.last_send_success_timebase") or 0)
                                            self.create_telemetry_collector_response(to_addr=collector_address, timebase=last_timebase, is_authorized_telemetry_request=True)
                                        else:
                                            self.send_latest_telemetry(to_addr=collector_address)
                                    else:
                                        if self.telemetry_send_blocked_until < now:
                                            next_slot = now+send_interval
                                            self.telemetry_send_blocked_until = next_slot
                                            RNS.log(f"Sending telemetry to collector failed after {self.pending_telemetry_send_try} tries.", RNS.LOG_WARNING)
                                            RNS.log(f"Not scheduling further retries until next send slot in {RNS.prettytime(next_slot-now)}.", RNS.LOG_WARNING)
                                            self.pending_telemetry_send_try = 0

                            except Exception as e:
                                RNS.log("An error occurred while sending scheduled telemetry to collector: "+str(e), RNS.LOG_ERROR)

                    if self.config["telemetry_request_from_collector"]:
                        if self.config["telemetry_collector"] != None and self.config["telemetry_collector"] != self.lxmf_destination.hash:
                            try:
                                now = time.time()
                                collector_address = self.config["telemetry_collector"]
                                last_request_timebase = self.getpersistent(f"telemetry.{RNS.hexrep(collector_address, delimit=False)}.last_request_success_timebase") or 0
                                request_interval = self.config["telemetry_request_interval"]
                                next_request = last_request_timebase+request_interval

                                RNS.log("Last telemetry request was "+RNS.prettytime(now-last_request_timebase)+" ago", RNS.LOG_EXTREME)
                                RNS.log("Next telemetry request is "+("in "+RNS.prettytime(next_request-now) if next_request-now > 0 else "now"), RNS.LOG_EXTREME)

                                if now > last_request_timebase+request_interval:
                                    try:
                                        RNS.log("Initiating telemetry request to collector", RNS.LOG_DEBUG)
                                        self.request_latest_telemetry(from_addr=self.config["telemetry_collector"])
                                    except Exception as e:
                                        RNS.log("An error occurred while requesting a telemetry update from collector. The contained exception was: "+str(e), RNS.LOG_ERROR)

                            except Exception as e:
                                RNS.log("An error occurred while requesting scheduled telemetry from collector: "+str(e), RNS.LOG_ERROR)

    def __start_jobs_deferred(self):
        if self.is_service:
            self.service_thread = threading.Thread(target=self._service_jobs, daemon=True)
            self.service_thread.start()

        if self.is_standalone or self.is_service:            
            if self.config["start_announce"]:
                def da():
                    time.sleep(8)
                    self.lxmf_announce()
                    self.last_if_change_announce = time.time()
                threading.Thread(target=da, daemon=True).start()

            self.periodic_thread = threading.Thread(target=self._periodic_jobs, daemon=True)
            self.periodic_thread.start()

        if self.is_standalone or self.is_client:
            if self.config["telemetry_enabled"]:
                self.run_telemetry()
        elif self.is_service:
            self.run_service_telemetry()

    def __add_localinterface(self, delay=None):
        self.interface_local_adding = True
        if delay:
            time.sleep(delay)

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
            self.interface_local_adding = False

        except Exception as e:
            RNS.log("Error while adding AutoInterface. The contained exception was: "+str(e))
            self.interface_local = None
            self.interface_local_adding = False

    def _reticulum_log_debug(self, debug=False):
        self.log_verbose = debug
        if self.log_verbose:
            selected_level = 6
        else:
            selected_level = 2

        RNS.loglevel = selected_level
        if self.is_client:
            self.service_rpc_set_debug(debug)

    def __start_jobs_immediate(self):
        if self.log_verbose:
            selected_level = 6
        else:
            selected_level = 2

        self.setstate("init.loadingstate", "Substantiating Reticulum")
        self.reticulum = RNS.Reticulum(configdir=self.rns_configdir, loglevel=selected_level)

        if self.is_service:
            self.__start_rpc_listener()

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
                    self.__add_localinterface()

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

                                if ifac_netname != None or ifac_netkey != None:
                                    ifac_size = 16
                                else:
                                    ifac_size = None

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
                                    
                                self.reticulum._add_interface(tcpinterface, mode=if_mode, ifac_netname=ifac_netname, ifac_netkey=ifac_netkey, ifac_size=ifac_size)
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

                            if ifac_netname != None or ifac_netkey != None:
                                ifac_size = 16
                            else:
                                ifac_size = None

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
                                
                            self.reticulum._add_interface(i2pinterface, mode = if_mode, ifac_netname=ifac_netname, ifac_netkey=ifac_netkey, ifac_size=ifac_size)
                            
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

                        if self.config["hw_rnode_atl_short"] == "":
                            atl_short = None
                        else:
                            atl_short = self.config["hw_rnode_atl_short"]

                        if self.config["hw_rnode_atl_long"] == "":
                            atl_long = None
                        else:
                            atl_long = self.config["hw_rnode_atl_long"]

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
                                st_alock = atl_short,
                                lt_alock = atl_long,
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

                        if self.config["hw_rnode_enable_framebuffer"] == True:
                            if self.interface_rnode.online:
                                self.interface_rnode.display_image(sideband_fb_data)
                                self.interface_rnode.enable_external_framebuffer()
                            else:
                                self.interface_rnode.last_imagedata = sideband_fb_data
                        else:
                            if self.interface_rnode.online:
                                self.interface_rnode.disable_external_framebuffer()

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
        
        if self.config["lxm_limit_1mb"]:
            lxm_limit = 1000
        else:
            lxm_limit = self.default_lxm_limit

        self.message_router = LXMF.LXMRouter(identity = self.identity, storagepath = self.lxmf_storage, autopeer = True, delivery_limit = lxm_limit)
        self.message_router.register_delivery_callback(self.lxmf_delivery)

        configured_stamp_cost = None
        if self.config["lxmf_require_stamps"]:
            configured_stamp_cost = self.config["lxmf_inbound_stamp_cost"]

        self.lxmf_destination = self.message_router.register_delivery_identity(self.identity, display_name=self.config["display_name"], stamp_cost=configured_stamp_cost)
        if self.config["lxmf_ignore_invalid_stamps"]:
            self.message_router.enforce_stamps()
        else:
            self.message_router.ignore_stamps()
        
        # TODO: Update to announce call in LXMF when full 0.5.0 support is added (get app data from LXMRouter instead)
        # Currently overrides the LXMF routers auto-generated announce data so that Sideband will announce old-format
        # LXMF announces if require_stamps is disabled.
        # if not self.config["lxmf_require_stamps"]:
        #     self.lxmf_destination.set_default_app_data(self.get_display_name_bytes)

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

    def update_ignore_invalid_stamps(self):
        if self.config["lxmf_ignore_invalid_stamps"]:
            self.message_router.enforce_stamps()
        else:
            self.message_router.ignore_stamps()

    def message_notification_no_display(self, message):
        self.message_notification(message, no_display=True)

    def message_notification(self, message, no_display=False):
        if message.state == LXMF.LXMessage.FAILED and hasattr(message, "try_propagation_on_fail") and message.try_propagation_on_fail:
            if hasattr(message, "stamp_generation_failed") and message.stamp_generation_failed == True:
                RNS.log(f"Could not send {message} due to a stamp generation failure", RNS.LOG_ERROR)
                if not no_display:
                    self.lxm_ingest(message, originator=True)
            else:
                RNS.log("Direct delivery of "+str(message)+" failed. Retrying as propagated message.", RNS.LOG_VERBOSE)
                message.try_propagation_on_fail = None
                message.delivery_attempts = 0
                if hasattr(message, "next_delivery_attempt"):
                    del message.next_delivery_attempt
                message.packed = None
                message.desired_method = LXMF.LXMessage.PROPAGATED
                self._db_message_set_method(message.hash, LXMF.LXMessage.PROPAGATED)
                self.message_router.handle_outbound(message)
        else:
            if not no_display:
                self.lxm_ingest(message, originator=True)

            if message.fields != None and LXMF.FIELD_TELEMETRY in message.fields:
                if len(message.fields[LXMF.FIELD_TELEMETRY]) > 0:
                    try:
                        telemeter = Telemeter.from_packed(message.fields[LXMF.FIELD_TELEMETRY])
                        telemetry_timebase = telemeter.read_all()["time"]["utc"]
                        RNS.log("Setting last successul telemetry timebase for "+RNS.prettyhexrep(message.destination_hash)+" to "+str(telemetry_timebase), RNS.LOG_DEBUG)
                        self.setpersistent(f"telemetry.{RNS.hexrep(message.destination_hash, delimit=False)}.last_send_success_timebase", telemetry_timebase)
                    except Exception as e:
                        RNS.log("Error while setting last successul telemetry timebase for "+RNS.prettyhexrep(message.destination_hash), RNS.LOG_DEBUG)

    def get_message_fields(self, context_dest, telemetry_update=False, is_authorized_telemetry_request=False, signal_already_sent=False):
        fields = {}
        send_telemetry = (telemetry_update == True) or (self.should_send_telemetry(context_dest) or is_authorized_telemetry_request)
        send_appearance = self.config["telemetry_send_appearance"] or send_telemetry

        if send_telemetry and self.latest_packed_telemetry != None:
            telemeter = Telemeter.from_packed(self.latest_packed_telemetry)
            telemetry_timebase = telemeter.read_all()["time"]["utc"]
            last_success_tb = (self.getpersistent(f"telemetry.{RNS.hexrep(context_dest, delimit=False)}.last_send_success_timebase") or 0)
            if telemetry_timebase > last_success_tb:
                RNS.log("Embedding own telemetry in message since current telemetry is newer than latest successful timebase", RNS.LOG_DEBUG)
            else:
                RNS.log("Not embedding own telemetry in message since current telemetry timebase ("+str(telemetry_timebase)+") is not newer than latest successful timebase ("+str(last_success_tb)+")", RNS.LOG_DEBUG)
                send_telemetry = False
                send_appearance = False
                if signal_already_sent:
                    return False

        else:
            RNS.log("Not embedding telemetry in message since no telemetry is available", RNS.LOG_DEBUG)
            send_telemetry = False

        if send_telemetry or send_appearance:
            if send_appearance:
                def fth(c):
                    r = c[0]; g = c[1]; b = c[2]
                    r = min(max(0, r), 1); g = min(max(0, g), 1); b = min(max(0, b), 1)
                    d = 1.0/255.0
                    return struct.pack("!BBB", int(r/d), int(g/d), int(b/d))

                icon = self.config["telemetry_icon"]
                fg = fth(self.config["telemetry_fg"][:-1])
                bg = fth(self.config["telemetry_bg"][:-1])

                fields[LXMF.FIELD_ICON_APPEARANCE] = [icon, fg, bg]

            if send_telemetry:
                fields[LXMF.FIELD_TELEMETRY] = self.latest_packed_telemetry

        return fields

    def paper_message(self, content, destination_hash):
        try:
            if content == "":
                raise ValueError("Message content cannot be empty")

            dest_identity = RNS.Identity.recall(destination_hash)
            dest = RNS.Destination(dest_identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery")
            source = self.lxmf_destination
            
            desired_method = LXMF.LXMessage.PAPER
            # TODO: Should paper messages also include a ticket to trusted peers?
            lxm = LXMF.LXMessage(dest, source, content, title="", desired_method=desired_method, fields = self.get_message_fields(destination_hash), include_ticket=self.is_trusted(destination_hash))

            self.lxm_ingest(lxm, originator=True)

            return True

        except Exception as e:
            RNS.log("Error while creating paper message: "+str(e), RNS.LOG_ERROR)
            return False

    def _service_get_lxm_progress(self, lxm_hash):
        if not RNS.vendor.platformutils.is_android():
            return False
        else:
            if self.is_client:
                try:
                    if self.rpc_connection == None:
                        self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)

                    self.rpc_connection.send({"get_lxm_progress": {"lxm_hash": lxm_hash}})
                    response = self.rpc_connection.recv()
                    return response
                
                except Exception as e:
                    RNS.log("Error while getting LXM progress over RPC: "+str(e), RNS.LOG_DEBUG)
                    RNS.trace_exception(e)
                    return False
            else:
                return False


    def get_lxm_progress(self, lxm_hash):
        try:
            prg = self.message_router.get_outbound_progress(lxm_hash)
            if not prg and self.is_client:
                prg = self._service_get_lxm_progress(lxm_hash)

            return prg
        except Exception as e:
            RNS.log("An error occurred while getting message transfer progress: "+str(e), RNS.LOG_ERROR)
            return None

    def get_lxm_stamp_cost(self, lxm_hash):
        try:
            return self.message_router.get_outbound_lxm_stamp_cost(lxm_hash)
        except Exception as e:
            RNS.log("An error occurred while getting message transfer stamp cost: "+str(e), RNS.LOG_ERROR)
            return None

    def _service_send_message(self, content, destination_hash, propagation, skip_fields=False, no_display=False, attachment = None, image = None, audio = None):
        if not RNS.vendor.platformutils.is_android():
            return False
        else:
            if self.is_client:
                try:
                    if self.rpc_connection == None:
                        self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)

                    self.rpc_connection.send({"send_message": {
                        "content": content,
                        "destination_hash": destination_hash,
                        "propagation": propagation,
                        "skip_fields": skip_fields,
                        "no_display": no_display,
                        "attachment": attachment,
                        "image": image,
                        "audio": audio}
                    })
                    response = self.rpc_connection.recv()
                    return response
                
                except Exception as e:
                    RNS.log("Error while sending message over RPC: "+str(e), RNS.LOG_DEBUG)
                    RNS.trace_exception(e)
                    return False
            else:
                return False

    def _service_send_command(self, content, destination_hash, propagation):
        if not RNS.vendor.platformutils.is_android():
            return False
        else:
            if self.is_client:
                try:
                    if self.rpc_connection == None:
                        self.rpc_connection = multiprocessing.connection.Client(self.rpc_addr, authkey=self.rpc_key)

                    self.rpc_connection.send({"send_command": {
                        "content": content,
                        "destination_hash": destination_hash,
                        "propagation": propagation}
                    })
                    response = self.rpc_connection.recv()
                    return response
                
                except Exception as e:
                    RNS.log("Error while sending command over RPC: "+str(e), RNS.LOG_DEBUG)
                    RNS.trace_exception(e)
                    return False
            else:
                return False

    def send_message(self, content, destination_hash, propagation, skip_fields=False, no_display=False, attachment = None, image = None, audio = None):
        if self.allow_service_dispatch and self.is_client:
            try:
                return self._service_send_message(content, destination_hash, propagation, skip_fields, no_display, attachment, image, audio)

            except Exception as e:
                RNS.log("Error while sending message: "+str(e), RNS.LOG_ERROR)
                RNS.trace_exception(e)
                return False

        else:
            try:
                if content == "":
                    raise ValueError("Message content cannot be empty")

                dest_identity = RNS.Identity.recall(destination_hash)
                dest = RNS.Destination(dest_identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery")
                source = self.lxmf_destination
                
                if propagation:
                    desired_method = LXMF.LXMessage.PROPAGATED
                else:
                    if not self.message_router.delivery_link_available(destination_hash) and RNS.Identity.current_ratchet_id(destination_hash) != None:
                        RNS.log(f"Have ratchet for {RNS.prettyhexrep(destination_hash)}, requesting opportunistic delivery of message", RNS.LOG_DEBUG)
                        desired_method = LXMF.LXMessage.OPPORTUNISTIC
                    else:
                        desired_method = LXMF.LXMessage.DIRECT

                if skip_fields:
                    fields = {}
                else:
                    fields = self.get_message_fields(destination_hash)

                if attachment != None:
                    fields[LXMF.FIELD_FILE_ATTACHMENTS] = [attachment]
                if image != None:
                    fields[LXMF.FIELD_IMAGE] = image
                if audio != None:
                    fields[LXMF.FIELD_AUDIO] = audio

                lxm = LXMF.LXMessage(dest, source, content, title="", desired_method=desired_method, fields = fields, include_ticket=self.is_trusted(destination_hash))
                
                if not no_display:
                    lxm.register_delivery_callback(self.message_notification)
                    lxm.register_failed_callback(self.message_notification)
                else:
                    lxm.register_delivery_callback(self.message_notification_no_display)
                    lxm.register_failed_callback(self.message_notification_no_display)

                if self.message_router.get_outbound_propagation_node() != None:
                    if self.config["lxmf_try_propagation_on_fail"]:
                        lxm.try_propagation_on_fail = True

                self.message_router.handle_outbound(lxm)

                if not no_display:
                    self.lxm_ingest(lxm, originator=True)

                return True

            except Exception as e:
                RNS.log("Error while sending message: "+str(e), RNS.LOG_ERROR)
                RNS.trace_exception(e)
                return False

    def send_command(self, content, destination_hash, propagation):
        if self.allow_service_dispatch and self.is_client:
            try:
                return self._service_send_command(content, destination_hash, propagation)

            except Exception as e:
                RNS.log("Error while sending message: "+str(e), RNS.LOG_ERROR)
                RNS.trace_exception(e)
                return False

        else:
            try:
                if content == "":
                    return False

                commands = []
                if content.startswith("echo "):
                    echo_content = content.replace("echo ", "").encode("utf-8")
                    if len(echo_content) > 0:
                        commands.append({Commands.ECHO: echo_content})
                elif content.startswith("sig"):
                    commands.append({Commands.SIGNAL_REPORT: True})
                elif content.startswith("ping"):
                    commands.append({Commands.PING: True})
                else:
                    commands.append({Commands.PLUGIN_COMMAND: content})

                if len(commands) == 0:
                    return False

                dest_identity = RNS.Identity.recall(destination_hash)
                dest = RNS.Destination(dest_identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery")
                source = self.lxmf_destination
                
                if propagation:
                    desired_method = LXMF.LXMessage.PROPAGATED
                else:
                    if not self.message_router.delivery_link_available(destination_hash) and RNS.Identity.current_ratchet_id(destination_hash) != None:
                        RNS.log(f"Have ratchet for {RNS.prettyhexrep(destination_hash)}, requesting opportunistic delivery of command", RNS.LOG_DEBUG)
                        desired_method = LXMF.LXMessage.OPPORTUNISTIC
                    else:
                        desired_method = LXMF.LXMessage.DIRECT

                lxm = LXMF.LXMessage(dest, source, "", title="", desired_method=desired_method, fields = {LXMF.FIELD_COMMANDS: commands}, include_ticket=self.is_trusted(destination_hash))
                lxm.register_delivery_callback(self.message_notification)
                lxm.register_failed_callback(self.message_notification)

                if self.message_router.get_outbound_propagation_node() != None:
                    if self.config["lxmf_try_propagation_on_fail"]:
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
        ptt_enabled = False
        telemetry_only = False
        own_command = False
        unread_reason_tx = False

        if originator:
            context_dest = message.destination_hash
            unread_reason_tx = True
        else:
            context_dest = message.source_hash
            is_trusted = self.is_trusted(context_dest)
            ptt_enabled = self.ptt_enabled(context_dest)

        if originator and LXMF.FIELD_COMMANDS in message.fields:
            own_command = True

        if self._db_message(message.hash):
            RNS.log("Message exists, setting state to: "+str(message.state), RNS.LOG_DEBUG)
            stamp = None
            if originator and message.stamp != None:
                stamp = [message.stamp, message.stamp_valid, message.stamp_value]
            self._db_message_set_state(message.hash, message.state, ratchet_id=message.ratchet_id, originator_stamp=stamp)
        else:
            RNS.log("Message does not exist, saving", RNS.LOG_DEBUG)
            self._db_save_lxm(message, context_dest, originator, own_command=own_command)

            if is_trusted:
                should_notify = True

            if len(message.content) == 0 and len(message.title) == 0:
                if (LXMF.FIELD_TELEMETRY in message.fields or LXMF.FIELD_TELEMETRY_STREAM in message.fields or LXMF.FIELD_COMMANDS in message.fields):
                    RNS.log("Squelching notification due to telemetry-only message", RNS.LOG_DEBUG)
                    telemetry_only = True

            if LXMF.FIELD_TICKET in message.fields:
                if self.is_service:
                    RNS.log("Notifying UI of newly arrived delivery ticket", RNS.LOG_DEBUG)
                    self.setstate("app.flags.new_ticket", True)

        if not telemetry_only:
            if self._db_conversation(context_dest) == None:
                self._db_create_conversation(context_dest)
                self.setstate("app.flags.new_conversations", True)

            if self.gui_display() == "messages_screen":
                if self.gui_conversation() != context_dest:
                    self.unread_conversation(context_dest, tx=unread_reason_tx)
                    self.setstate("app.flags.unread_conversations", True)
                else:
                    self.txtime_conversation(context_dest)
                    self.setstate("wants.viewupdate.conversations", True)
                    if self.gui_foreground():
                        RNS.log("Squelching notification since GUI is in foreground", RNS.LOG_DEBUG)
                        should_notify = False
            else:
                self.unread_conversation(context_dest, tx=unread_reason_tx)
                self.setstate("app.flags.unread_conversations", True)

                if RNS.vendor.platformutils.is_android():
                    if self.gui_display() == "conversations_screen" and self.gui_foreground():
                        should_notify = False

            if not originator and LXMF.FIELD_AUDIO in message.fields and ptt_enabled:
                self.ptt_event(message)
                should_notify = False

        if self.is_client:
            should_notify = False

        if telemetry_only:
            should_notify = False

        if should_notify:
            nlen = 128
            text = message.content.decode("utf-8")
            notification_content = text[:nlen]
            if len(text) > nlen:
                notification_content += " [...]"

            if len(text) < 2 and LXMF.FIELD_AUDIO in message.fields:
                notification_content = "Audio message"
            if len(text) < 2 and LXMF.FIELD_IMAGE in message.fields:
                notification_content = "Image"
            if len(text) < 2 and LXMF.FIELD_FILE_ATTACHMENTS in message.fields:
                notification_content = "File attachment"

            try:
                self.notify(title=self.peer_display_name(context_dest), content=notification_content, group="LXM", context_id=RNS.hexrep(context_dest, delimit=False))
            except Exception as e:
                RNS.log("Could not post notification for received message: "+str(e), RNS.LOG_ERROR)

    def ptt_playback(self, message):
        ptt_timeout = 60
        event_time = time.time()
        while hasattr(self, "msg_sound") and self.msg_sound != None and self.msg_sound.playing() and time.time() < event_time+ptt_timeout:
            time.sleep(0.1)
        time.sleep(0.5)

        if self.msg_audio == None:
            if RNS.vendor.platformutils.is_android():
                from plyer import audio
            else:
                from sbapp.plyer import audio

            RNS.log("Audio init done")
            self.msg_audio = audio
        try:
            temp_path = None
            audio_field = message.fields[LXMF.FIELD_AUDIO]
            if self.last_msg_audio != audio_field[1]:
                RNS.log("Reloading audio source", RNS.LOG_DEBUG)
                if len(audio_field[1]) > 10:
                    self.last_msg_audio = audio_field[1]
                else:
                    self.last_msg_audio = None
                    return

                if audio_field[0] == LXMF.AM_OPUS_OGG:
                    temp_path = self.rec_cache+"/msg.ogg"
                    with open(temp_path, "wb") as af:
                        af.write(self.last_msg_audio)

                elif audio_field[0] >= LXMF.AM_CODEC2_700C and audio_field[0] <= LXMF.AM_CODEC2_3200:
                    temp_path = self.rec_cache+"/msg.ogg"
                    from sideband.audioproc import samples_to_ogg, decode_codec2, detect_codec2
                    
                    target_rate = 8000
                    if RNS.vendor.platformutils.is_linux():
                        target_rate = 48000

                    if detect_codec2():
                        if samples_to_ogg(decode_codec2(audio_field[1], audio_field[0]), temp_path, input_rate=8000, output_rate=target_rate):
                            RNS.log("Wrote OGG file to: "+temp_path, RNS.LOG_DEBUG)
                        else:
                            RNS.log("OGG write failed", RNS.LOG_DEBUG)
                    else:
                        self.last_msg_audio = None
                        return
                
                else:
                    # Unimplemented audio type
                    pass

                self.msg_sound = self.msg_audio
                self.msg_sound._file_path = temp_path
                self.msg_sound.reload()

            if self.msg_sound != None:
                RNS.log("Starting playback", RNS.LOG_DEBUG)
                self.msg_sound.play()
            else:
                RNS.log("Playback was requested, but no audio data was loaded for playback", RNS.LOG_ERROR)

        except Exception as e:
            RNS.log("Error while playing message audio:"+str(e))
            RNS.trace_exception(e)

    def ptt_event(self, message):
        def ptt_job():
            try:
                self.ptt_playback_lock.acquire()
                while self.ui_recording:
                    time.sleep(0.5)
                self.ptt_playback(message)
            except Exception as e:
                RNS.log("Error while starting playback for PTT-enabled conversation: "+str(e), RNS.LOG_ERROR)
            finally:
                self.ptt_playback_lock.release()

        threading.Thread(target=ptt_job, daemon=True).start()

    def ui_started_recording(self):
        self.ui_recording = True
        self.service_rpc_set_ui_recording(True)

    def ui_stopped_recording(self):
        self.ui_recording = False
        self.service_rpc_set_ui_recording(False)

    def start(self):
        self._db_clean_messages()
        self.__start_jobs_immediate()

        thread = threading.Thread(target=self.__start_jobs_deferred)
        thread.setDaemon(True)
        thread.start()

        self.setstate("core.started", True)
        RNS.log("Sideband Core "+str(self)+" version "+str(self.version_str)+" started")

    def stop_webshare(self):
        if self.webshare_server != None:
            self.webshare_server.shutdown()
            self.webshare_server = None

    def start_webshare(self):
        if self.webshare_server == None:
            def webshare_job():
                from http import server
                import socketserver
                import json

                webshare_dir = self.webshare_dir
                port = 4444
                class RequestHandler(server.SimpleHTTPRequestHandler):
                    def do_GET(self):
                        serve_root = webshare_dir
                        if "?" in self.path:
                            self.path = self.path.split("?")[0]
                        path = serve_root + self.path
                        if self.path == "/":
                            path = serve_root + "/index.html"
                        if "/.." in self.path:
                            self.send_response(403)
                            self.end_headers()
                            self.write("Forbidden".encode("utf-8"))
                        elif self.path == "/pkglist":
                            try:
                                self.send_response(200)
                                self.send_header("Content-type", "text/json")
                                self.end_headers()
                                json_result = json.dumps(os.listdir(serve_root+"/pkg"))
                                self.wfile.write(json_result.encode("utf-8"))
                            except Exception as e:
                                self.send_response(500)
                                self.end_headers()
                                RNS.log("Error listing directory "+str(path)+": "+str(e), RNS.LOG_ERROR)
                                es = "Error"
                                self.wfile.write(es.encode("utf-8"))
                        else:
                            try:
                                with open(path, 'rb') as f:
                                    data = f.read()
                                self.send_response(200)
                                if path.lower().endswith(".apk"):
                                    self.send_header("Content-type", "application/vnd.android.package-archive")
                                self.end_headers()
                                self.wfile.write(data)
                            except Exception as e:
                                self.send_response(500)
                                self.end_headers()
                                RNS.log("Error serving file "+str(path)+": "+str(e), RNS.LOG_ERROR)
                                es = "Error"
                                self.wfile.write(es.encode("utf-8"))

                with socketserver.TCPServer(("", port), RequestHandler) as webserver:
                    self.webshare_server = webserver
                    webserver.serve_forever()
                    self.webshare_server = None
                    RNS.log("Webshare server closed", RNS.LOG_DEBUG)

            threading.Thread(target=webshare_job, daemon=True).start()

    def request_lxmf_sync(self, limit = None):
        if self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_IDLE or self.message_router.propagation_transfer_state >= LXMF.LXMRouter.PR_COMPLETE:
            self.message_router.request_messages_from_propagation_node(self.identity, max_messages = limit)
            RNS.log("LXMF message sync requested from propagation node "+RNS.prettyhexrep(self.message_router.get_outbound_propagation_node())+" for "+str(self.identity))
            return True
        else:
            return False

    def cancel_lxmf_sync(self):
        if self.message_router.propagation_transfer_state != LXMF.LXMRouter.PR_IDLE:
            self.message_router.cancel_propagation_node_requests()

    def get_sync_progress(self):
        state = self.message_router.propagation_transfer_state
        if state == LXMF.LXMRouter.PR_PATH_REQUESTED:
            state_val = 0.05
        elif state == LXMF.LXMRouter.PR_LINK_ESTABLISHING:
            state_val = 0.1
        elif state == LXMF.LXMRouter.PR_LINK_ESTABLISHED:
            state_val = 0.15
        elif state >= LXMF.LXMRouter.PR_REQUEST_SENT:
            state_val = 0.2
        else:
            state_val = 0.0
        return (self.message_router.propagation_transfer_progress*0.8)+state_val

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

        RNS.log("LXMF delivery "+str(time_string)+". "+str(signature_string)+".", RNS.LOG_DEBUG)

        try:
            context_dest = message.source_hash
            if self.config["lxmf_ignore_unknown"] == True:
                if self._db_conversation(context_dest) == None:
                    RNS.log("Dropping message from unknown sender "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
                    return

            if message.signature_validated and LXMF.FIELD_COMMANDS in message.fields:
                if self.allow_request_from(context_dest):
                    commands = message.fields[LXMF.FIELD_COMMANDS]
                    self.handle_commands(commands, message)
                else:
                    # TODO: Add these event to built-in log/event viewer
                    # when it is implemented.
                    RNS.log("Unauthorized command received from "+RNS.prettyhexrep(context_dest), RNS.LOG_WARNING)

            else:
                self.lxm_ingest(message)

        except Exception as e:
            RNS.log("Error while ingesting LXMF message "+RNS.prettyhexrep(message.hash)+" to database: "+str(e), RNS.LOG_ERROR)

    def handle_plugin_command(self, command_string, message):
        try:
            call = shlex.split(command_string)
            command = call[0]
            arguments = call[1:]
            if command in self.active_command_plugins:
                RNS.log("Handling command \""+str(command)+"\" via command plugin "+str(self.active_command_plugins[command]), RNS.LOG_DEBUG)
                self.active_command_plugins[command].handle_command(arguments, message)

        except Exception as e:
            RNS.log("An error occurred while handling a plugin command. The contained exception was: "+str(e), RNS.LOG_ERROR)
            RNS.trace_exception(e)

    def handle_commands(self, commands, message):
        try:
            context_dest = message.source_hash
            RNS.log("Handling commands from "+RNS.prettyhexrep(context_dest), RNS.LOG_DEBUG)
            for command in commands:
                if Commands.TELEMETRY_REQUEST in command:
                    timebase = int(command[Commands.TELEMETRY_REQUEST])
                    RNS.log("Handling telemetry request with timebase "+str(timebase), RNS.LOG_DEBUG)
                    if self.config["telemetry_collector_enabled"]:
                        RNS.log(f"Collector requests enabled, returning complete telemetry response for all known objects since {timebase}", RNS.LOG_DEBUG)
                        self.create_telemetry_collector_response(to_addr=context_dest, timebase=timebase, is_authorized_telemetry_request=True)
                    else:
                        RNS.log("Responding with own latest telemetry", RNS.LOG_DEBUG)
                        self.send_latest_telemetry(to_addr=context_dest)
                
                elif Commands.PING in command:
                    RNS.log("Handling ping request", RNS.LOG_DEBUG)
                    self.send_message("Ping reply", context_dest, False, skip_fields=True, no_display=True)
                
                elif Commands.ECHO in command:
                    msg_content = "Echo reply: "+command[Commands.ECHO].decode("utf-8")
                    RNS.log("Handling echo request", RNS.LOG_DEBUG)
                    self.send_message(msg_content, context_dest, False, skip_fields=True, no_display=True)
                
                elif Commands.SIGNAL_REPORT in command:
                    RNS.log("Handling signal report", RNS.LOG_DEBUG)
                    phy_str = ""
                    if message.q != None:
                        phy_str += f"Link Quality: {message.q}%\n"
                    if message.rssi != None:
                        phy_str += f"RSSI: {message.rssi} dBm\n"
                    if message.snr != None:
                        phy_str += f"SNR: {message.snr} dB\n"
                    if len(phy_str) != 0:
                        phy_str = phy_str[:-1]
                    else:
                        phy_str = "No reception info available"

                    self.send_message(phy_str, context_dest, False, skip_fields=True, no_display=True)

                elif self.config["command_plugins_enabled"] and Commands.PLUGIN_COMMAND in command:
                    self.handle_plugin_command(command[Commands.PLUGIN_COMMAND], message)

        except Exception as e:
            RNS.log("Error while handling commands: "+str(e), RNS.LOG_ERROR)

    def create_telemetry_collector_response(self, to_addr, timebase, is_authorized_telemetry_request=False):
        added_sources = {}
        sources = self.list_telemetry(after=timebase)
        only_latest = self.config["telemetry_requests_only_send_latest"]

        elements = 0; added = 0
        telemetry_stream = []
        for source in sources:
            if source != to_addr:
                for entry in sources[source]:
                    elements += 1
                    timestamp = entry[0]; packed_telemetry = entry[1]
                    appearance = self._db_get_appearance(source, raw=True)
                    te = [source, timestamp, packed_telemetry, appearance]
                    if only_latest:
                        if not source in added_sources:
                            added_sources[source] = True
                            telemetry_stream.append(te)
                            added += 1
                    else:
                        telemetry_stream.append(te)
                        added += 1

        if len(telemetry_stream) == 0:
            RNS.log(f"No new telemetry for request with timebase {timebase}", RNS.LOG_DEBUG)

        return self.send_latest_telemetry(
            to_addr=to_addr,
            stream=telemetry_stream,
            is_authorized_telemetry_request=is_authorized_telemetry_request
        )


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
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_NO_PATH:
            return "No path to propagation node"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_LINK_FAILED:
            return "Link establisment failed"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_TRANSFER_FAILED:
            return "Sync request failed"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_NO_IDENTITY_RCVD:
            return "No identity received by remote"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_NO_ACCESS:
            return "No access to specified node"
        elif self.message_router.propagation_transfer_state == LXMF.LXMRouter.PR_FAILED:
            return "Sync failed"
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
