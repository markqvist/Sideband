import RNS
import LXMF
import threading
import plyer
import os.path
import time
import sqlite3

import RNS.vendor.umsgpack as msgpack

class PropagationNodeDetector():
    EMITTED_DELTA_GRACE = 300
    EMITTED_DELTA_IGNORE = 10

    aspect_filter = "lxmf.propagation"

    def received_announce(self, destination_hash, announced_identity, app_data):
        try:
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

    MAX_ANNOUNCES  = 64

    aspect_filter = "lxmf.delivery"
    def received_announce(self, destination_hash, announced_identity, app_data):
        # Add the announce to the directory announce
        # stream logger
        self.log_announce(destination_hash, app_data, dest_type=SidebandCore.aspect_filter)

    def __init__(self, owner_app):
        self.owner_app = owner_app
        self.reticulum = None

        self.app_dir       = plyer.storagepath.get_home_dir()+"/.sideband"
        
        self.rns_configdir = None
        if RNS.vendor.platformutils.get_platform() == "android":
            self.app_dir = plyer.storagepath.get_application_dir()+"/io.unsigned.sideband/files/"
            self.rns_configdir = self.app_dir+"/app_storage/reticulum"

        if not os.path.isdir(self.app_dir+"/app_storage"):
            os.makedirs(self.app_dir+"/app_storage")

        self.asset_dir     = self.app_dir+"/assets"
        self.kv_dir        = self.app_dir+"/views/kv"
        self.config_path   = self.app_dir+"/app_storage/sideband_config"
        self.identity_path = self.app_dir+"/app_storage/primary_identity"
        self.db_path       = self.app_dir+"/app_storage/sideband.db"
        self.lxmf_storage  = self.app_dir+"/app_storage/"

        try:
            if not os.path.isfile(self.config_path):
                self.__init_config()
            else:
                self.__load_config()
                
        except Exception as e:
            RNS.log("Error while configuring Sideband: "+str(e), RNS.LOG_ERROR)


        # Initialise Reticulum configuration
        if RNS.vendor.platformutils.get_platform() == "android":
            try:
                self.rns_configdir = self.app_dir+"/app_storage/reticulum"
                if not os.path.isdir(self.rns_configdir):
                    os.makedirs(self.rns_configdir)

                RNS.log("Configuring Reticulum instance...")
                config_file = open(self.rns_configdir+"/config", "wb")
                config_file.write(rns_config)
                config_file.close()

            except Exception as e:
                RNS.log("Error while configuring Reticulum instance: "+str(e), RNS.LOG_ERROR)
        
        else:
            pass

        self.active_propagation_node = None
        self.propagation_detector = PropagationNodeDetector(self)

        RNS.Transport.register_announce_handler(self)
        RNS.Transport.register_announce_handler(self.propagation_detector)

        self.start()


    def __init_config(self):
        RNS.log("Creating new Sideband configuration...")
        if os.path.isfile(self.identity_path):
            self.identity = RNS.Identity.from_file(self.identity_path)
        else:
            self.identity = RNS.Identity()
            self.identity.to_file(self.identity_path)

        self.config = {}
        # Settings
        self.config["display_name"] = "Anonymous Peer"
        self.config["start_announce"] = False
        self.config["propagation_by_default"] = False
        self.config["home_node_as_broadcast_repeater"] = False
        self.config["send_telemetry_to_home_node"] = False
        self.config["lxmf_propagation_node"] = None
        self.config["lxmf_sync_limit"] = None
        self.config["lxmf_sync_max"] = 3
        self.config["last_lxmf_propagation_node"] = None
        self.config["nn_home_node"] = None
        # Connectivity
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
        self.config["connect_i2p_b32"] = "mrwqlsioq4hoo2lmeeud7dkfscnm7yxak7dmiyvsrnpfag3z5tsq.b32.i2p"
        self.config["connect_i2p_ifac_netname"] = ""
        self.config["connect_i2p_ifac_passphrase"] = ""

        self.__save_config()

        if not os.path.isfile(self.db_path):
            self.__db_init()


    def __load_config(self):
        RNS.log("Loading Sideband identity...")
        self.identity = RNS.Identity.from_file(self.identity_path)

        RNS.log("Loading Sideband configuration... "+str(self.config_path))
        config_file = open(self.config_path, "rb")
        self.config = msgpack.unpackb(config_file.read())
        config_file.close()

        if not os.path.isfile(self.db_path):
            self.__db_init()


    def __save_config(self):
        RNS.log("Saving Sideband configuration...")
        config_file = open(self.config_path, "wb")
        config_file.write(msgpack.packb(self.config))
        config_file.close()

    
    def save_configuration(self):
        RNS.log("Saving configuration")
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


    def log_announce(self, dest, app_data, dest_type):
        try:
            RNS.log("Received "+str(dest_type)+" announce for "+RNS.prettyhexrep(dest)+" with data: "+app_data.decode("utf-8"))
            self._db_save_announce(dest, app_data, dest_type)
            self.owner_app.flag_new_announces = True

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

    def list_messages(self, context_dest, after = None):
        result = self._db_messages(context_dest, after)
        if result != None:
            return result
        else:
            return []

    def __event_conversations_changed(self):
        pass

    def __event_conversation_changed(self, context_dest):
        pass

    def __db_init(self):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()

        dbc.execute("DROP TABLE IF EXISTS lxm")
        dbc.execute("CREATE TABLE lxm (lxm_hash BLOB PRIMARY KEY, dest BLOB, source BLOB, title BLOB, tx_ts INTEGER, rx_ts INTEGER, state INTEGER, method INTEGER, t_encrypted INTEGER, t_encryption INTEGER, data BLOB)")

        dbc.execute("DROP TABLE IF EXISTS conv")
        dbc.execute("CREATE TABLE conv (dest_context BLOB PRIMARY KEY, last_tx INTEGER, last_rx INTEGER, unread INTEGER, type INTEGER, trust INTEGER, name BLOB, data BLOB)")

        dbc.execute("DROP TABLE IF EXISTS announce")
        dbc.execute("CREATE TABLE announce (id PRIMARY KEY, received INTEGER, source BLOB, data BLOB, dest_type BLOB)")

        db.commit()
        db.close()

    def _db_conversation_set_unread(self, context_dest, unread):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()
        
        query = "UPDATE conv set unread = ? where dest_context = ?"
        data = (unread, context_dest)
        dbc.execute(query, data)
        result = dbc.fetchall()
        db.commit()

        db.close()

    def _db_conversation_set_trusted(self, context_dest, trusted):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()
        
        query = "UPDATE conv set trust = ? where dest_context = ?"
        data = (trusted, context_dest)
        dbc.execute(query, data)
        result = dbc.fetchall()
        db.commit()

        db.close()

    def _db_conversation_set_name(self, context_dest, name):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()
        
        query = "UPDATE conv set name=:name_data where dest_context=:ctx;"
        dbc.execute(query, {"ctx": context_dest, "name_data": name.encode("utf-8")})
        result = dbc.fetchall()
        db.commit()

        db.close()

    def _db_conversations(self):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()
        
        dbc.execute("select * from conv")
        result = dbc.fetchall()

        db.close()

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
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()
        
        dbc.execute("select * from announce order by received desc")
        result = dbc.fetchall()

        db.close()

        if len(result) < 1:
            return None
        else:
            announces = []
            for entry in result:
                try:
                    announce = {
                        "dest": entry[2],
                        "data": entry[3].decode("utf-8"),
                        "time": entry[1],
                        "type": entry[4]
                    }
                    announces.append(announce)
                except Exception as e:
                    RNS.log("Exception while fetching announce from DB: "+str(e), RNS.LOG_ERROR)

            return announces


    def _db_conversation(self, context_dest):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()
        
        query = "select * from conv where dest_context=:ctx"
        dbc.execute(query, {"ctx": context_dest})
        result = dbc.fetchall()

        db.close()

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
        RNS.log("Clearing conversation with "+RNS.prettyhexrep(context_dest))
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()

        query = "delete from lxm where (dest=:ctx_dst or source=:ctx_dst);"
        dbc.execute(query, {"ctx_dst": context_dest})
        db.commit()

        db.close()

    def _db_delete_conversation(self, context_dest):
        RNS.log("Deleting conversation with "+RNS.prettyhexrep(context_dest))
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()

        query = "delete from conv where (dest_context=:ctx_dst);"
        dbc.execute(query, {"ctx_dst": context_dest})
        db.commit()

        db.close()

    def _db_create_conversation(self, context_dest, name = None, trust = False):
        RNS.log("Creating conversation for "+RNS.prettyhexrep(context_dest))
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()

        def_name = "".encode("utf-8")
        query = "INSERT INTO conv (dest_context, last_tx, last_rx, unread, type, trust, name, data) values (?, ?, ?, ?, ?, ?, ?, ?)"
        data = (context_dest, 0, 0, 0, SidebandCore.CONV_P2P, 0, def_name, msgpack.packb(None))

        dbc.execute(query, data)

        db.commit()
        db.close()

        if trust:
            self._db_conversation_set_trusted(context_dest, True)

        if name != None and name != "":
            self._db_conversation_set_name(context_dest, name)

        self.__event_conversations_changed()

    def _db_delete_message(self, msg_hash):
        RNS.log("Deleting message "+RNS.prettyhexrep(msg_hash))
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()

        query = "delete from lxm where (lxm_hash=:mhash);"
        dbc.execute(query, {"mhash": msg_hash})
        db.commit()

        db.close()

    def _db_clean_messages(self):
        RNS.log("Purging stale messages... "+str(self.db_path))
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()

        query = "delete from lxm where (state=:outbound_state or state=:sending_state);"
        dbc.execute(query, {"outbound_state": LXMF.LXMessage.OUTBOUND, "sending_state": LXMF.LXMessage.SENDING})
        db.commit()

        db.close()

    def _db_message_set_state(self, lxm_hash, state):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()
        
        query = "UPDATE lxm set state = ? where lxm_hash = ?"
        data = (state, lxm_hash)
        dbc.execute(query, data)
        db.commit()
        result = dbc.fetchall()

        db.close()

    def _db_message_set_method(self, lxm_hash, method):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()
        
        query = "UPDATE lxm set method = ? where lxm_hash = ?"
        data = (method, lxm_hash)
        dbc.execute(query, data)
        db.commit()
        result = dbc.fetchall()

        db.close()

    def message(self, msg_hash):
        return self._db_message(msg_hash)

    def _db_message(self, msg_hash):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()
        
        query = "select * from lxm where lxm_hash=:mhash"
        dbc.execute(query, {"mhash": msg_hash})
        result = dbc.fetchall()

        db.close()

        if len(result) < 1:
            return None
        else:
            entry = result[0]
            lxm = LXMF.LXMessage.unpack_from_bytes(entry[10])
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

    def _db_messages(self, context_dest, after = None):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()
        
        if after == None:
            query = "select * from lxm where dest=:context_dest or source=:context_dest"
            dbc.execute(query, {"context_dest": context_dest})
        else:
            query = "select * from lxm where (dest=:context_dest or source=:context_dest) and rx_ts>:after_ts"
            dbc.execute(query, {"context_dest": context_dest, "after_ts": after})

        result = dbc.fetchall()

        db.close()

        if len(result) < 1:
            return None
        else:
            messages = []
            for entry in result:
                lxm = LXMF.LXMessage.unpack_from_bytes(entry[10])
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

            return messages


    def _db_save_lxm(self, lxm, context_dest):    
        state = lxm.state

        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()

        if not lxm.packed:
            lxm.pack()

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
            lxm.packed
        )

        dbc.execute(query, data)

        db.commit()
        db.close()

        self.__event_conversation_changed(context_dest)

    def _db_save_announce(self, destination_hash, app_data, dest_type="lxmf.delivery"):
        db = sqlite3.connect(self.db_path)
        dbc = db.cursor()

        query = "INSERT INTO announce (received, source, data, dest_type) values (?, ?, ?, ?)"
        data = (
            time.time(),
            destination_hash,
            app_data,
            dest_type,
        )

        dbc.execute(query, data)

        query = "delete from announce where id not in (select id from announce order by received desc limit "+str(self.MAX_ANNOUNCES)+")"
        dbc.execute(query)

        db.commit()
        db.close()

    def lxmf_announce(self):
        self.lxmf_destination.announce()

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

    def __start_jobs_deferred(self):
        if self.config["start_announce"]:
            self.lxmf_destination.announce()

    def __start_jobs_immediate(self):
        self.reticulum = RNS.Reticulum(configdir=self.rns_configdir)
        RNS.log("Reticulum started, activating LXMF...")

        if RNS.vendor.platformutils.get_platform() == "android":
            if not self.reticulum.is_connected_to_shared_instance:
                RNS.log("Running as master or standalone instance, adding interfaces")
                
                self.interface_local = None
                self.interface_tcp   = None
                self.interface_i2p   = None

                if self.config["connect_local"]:
                    try:
                        RNS.log("Adding Auto Interface...")
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
                        self.reticulum._add_interface(autointerface,ifac_netname=ifac_netname,ifac_netkey=ifac_netkey)
                        self.interface_local = autointerface

                    except Exception as e:
                        RNS.log("Error while adding AutoInterface. The contained exception was: "+str(e))
                        self.interface_local = None

                if self.config["connect_tcp"]:
                    try:
                        RNS.log("Adding TCP Interface...")

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
                                self.reticulum._add_interface(tcpinterface,ifac_netname=ifac_netname,ifac_netkey=ifac_netkey)
                                self.interface_tcp = tcpinterface

                    except Exception as e:
                        RNS.log("Error while adding TCP Interface. The contained exception was: "+str(e))
                        self.interface_tcp = None

                if self.config["connect_i2p"]:
                    try:
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
                            self.reticulum._add_interface(i2pinterface,ifac_netname=ifac_netname,ifac_netkey=ifac_netkey)
                            
                            for si in RNS.Transport.interfaces:
                                if type(si) == RNS.Interfaces.I2PInterface.I2PInterfacePeer:
                                    self.interface_i2p = si


                    except Exception as e:
                        RNS.log("Error while adding I2P Interface. The contained exception was: "+str(e))
                        self.interface_i2p = None


        self.message_router = LXMF.LXMRouter(identity = self.identity, storagepath = self.lxmf_storage, autopeer = True)
        self.message_router.register_delivery_callback(self.lxmf_delivery)

        self.lxmf_destination = self.message_router.register_delivery_identity(self.identity, display_name=self.config["display_name"])
        self.lxmf_destination.set_default_app_data(self.get_display_name_bytes)

        self.rns_dir = RNS.Reticulum.configdir

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


    def send_message(self, content, destination_hash, propagation):
        try:
            if content == "":
                raise ValueError("Message content cannot be empty")

            dest_identity = RNS.Identity.recall(destination_hash)
            dest = RNS.Destination(dest_identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery")
            source = self.lxmf_destination
            
            # TODO: Add setting
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

    def lxm_ingest(self, message, originator = False):
        if originator:
            context_dest = message.destination_hash
        else:
            context_dest = message.source_hash

        if self._db_message(message.hash):
            RNS.log("Message exists, setting state to: "+str(message.state), RNS.LOG_DEBUG)
            self._db_message_set_state(message.hash, message.state)
        else:
            RNS.log("Message does not exist, saving", RNS.LOG_DEBUG)
            self._db_save_lxm(message, context_dest)

        if self._db_conversation(context_dest) == None:
            self._db_create_conversation(context_dest)
            self.owner_app.flag_new_conversations = True

        if self.owner_app.root.ids.screen_manager.current == "messages_screen":
            if self.owner_app.root.ids.messages_scrollview.active_conversation != context_dest:
                self.unread_conversation(context_dest)
                self.owner_app.flag_unread_conversations = True
        else:
            self.unread_conversation(context_dest)
            self.owner_app.flag_unread_conversations = True

        try:
            self.owner_app.conversation_update(context_dest)
        except Exception as e:
            RNS.log("Error in conversation update callback: "+str(e))


    def start(self):
        self._db_clean_messages()
        self.__start_jobs_immediate()

        thread = threading.Thread(target=self.__start_jobs_deferred)
        thread.setDaemon(True)
        thread.start()
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

rns_config = """
[reticulum]
enable_transport = False
share_instance = Yes
shared_instance_port = 37428
instance_control_port = 37429
panic_on_interface_error = No

[logging]
loglevel = 3

""".encode("utf-8")
