import plyer.platforms.win.libs.wifi_defs as wifi_lib
from plyer.facades import Wifi


class WindowWifi(Wifi):

    names = {}

    def _is_enabled(self):
        '''
        TODO: Implement this in future
        Couldn't find a nice implementation for this although
        NetworkInformation class could be used but ctypes doesn't supports
        class yet. It should look something like this.

        for item in NetworkInformation.getConnectionProfiles():
            if item.IsWlanConnectionProfile:
                adapter_id = item.NetworkAdapter.NetworkAdapterId
        for item in NetworkInformation.GetLanIdentifiers():
            if item.NetworkAdapterId == adapter_id:
                is_wifi_enabled = True
        return True/False

        Returning True for now to make it work.
        '''
        return True

    def _get_network_info(self, name):
        '''
        Returns all the network information.
        '''
        return wifi_lib.get_network_info(name)

    def _start_scanning(self):
        '''
        Starts scanning for available Wi-Fi networks and returns the available,
        devices.
        '''
        if self._is_enabled():
            self.names = wifi_lib.start_scanning()
        else:
            raise Exception('Wifi not Enabled.')

    def _get_available_wifi(self):
        '''
        Returns the name of available networks.
        '''
        return wifi_lib.get_available_wifi()

    def _connect(self, network, parameters):
        '''
        Expects 2 parameters:
          - name/ssid of the network.
          - parameters: dict type
            - connection_mode:
              `https://msdn.microsoft.com/en-us/library/windows/desktop/
               ms706844(v=vs.85).aspx`

              :between range [0, 5]
              - wlan_connection_mode_profile,
                wlan_connection_mode_temporary_profile,
                wlan_connection_mode_discovery_secure,
                wlan_connection_mode_discovery_unsecure,
                wlan_connection_mode_auto,
                wlan_connection_mode_invalid.
            - profile:
                if wlanConnectionMode = wlan_connection_mode_profile
                then profile = ssid
                if wlanConnectionMode = wlan_connection_mode_temporary_profile
                then profile = XML representation of the profile used for the
                               connection
                if wlanConnectionMode = wlan_connection_mode_discovery_secure
                                        or
                                        wlan_connection_mode_discovery_unsecure
                then profile = None
            - ssid: optional (as network name and ssid are same)
            - bssidList
              `https://msdn.microsoft.com/en-us/library/windows/desktop/
              ms705996(v=vs.85).aspx`
              - Header
                structure that contains the type, version, and, size
                information
                of an NDIS structure.
                - Type: NDSI_OBJECT_TYPE_DEFAULT
                - Revision: DOT11_BSSID_LIST_REVISION_1
                - Size: sizeof(DOT11_BSSID_LIST)
              - uNumOfEntries
                The number of entries in this structure.
              - uTotalNumOfEntries
                The total number of entries supported.
              - BSSIDs
                `https://msdn.microsoft.com/en-us/library/windows/desktop/
                bb427397(v=vs.85).aspx`
                A list of BSS identifiers.
            - bssType
              `https://msdn.microsoft.com/en-us/library/windows/desktop/
              ms706001(v=vs.85).aspx`
              Constants:
              dot11_BSS_type_infrastructure  = 1,
              dot11_BSS_type_independent     = 2,
              dot11_BSS_type_any             = 3
            - flags
              Constant: WLAN_CONNECTION_HIDDEN_NETWORK  value: 0x00000001
              Constant: WLAN_CONNECTION_ADHOC_JOIN_ONLY value: 0x00000002
              Constant: WLAN_CONNECTION_IGNORE_PRIVACY_BIT value: 0x00000004
              Constant: WLAN_CONNECTION_EAPOL_PASSTHROUGH value: 0x00000008
            - password
        '''
        wifi_lib.connect(network, parameters)
        return

    def _disconnect(self):
        '''
        Disconnect from network.
        '''
        wifi_lib.disconnect()
        return


def instance():
    return WindowWifi()
