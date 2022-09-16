'''
Reference
Methods, Structures and Documentation adapted from.
https://msdn.microsoft.com/en-us/library/windows/desktop \
/ms705945%28v=vs.85%29.aspx
'''

from ctypes import (
    POINTER,
    FormatError,
    Structure,
    addressof,
    byref,
    c_bool,
    c_char,
    c_ubyte,
    c_uint,
    c_ulong,
    c_ushort,
    c_void_p,
    c_wchar,
    pointer,
    windll,
)
from ctypes.wintypes import DWORD, HANDLE, LPCWSTR, ULONG
from sys import exit as sys_exit


def customresize(array, new_size):
    return (
        array._type_ * new_size
    ).from_address(
        addressof(array)
    )


wlanapi = windll.LoadLibrary('wlanapi.dll')


class GUID(Structure):
    _fields_ = [
        ('Data1', c_ulong),
        ('Data2', c_ushort),
        ('Data3', c_ushort),
        ('Data4', c_ubyte * 8),
    ]


# The WLAN_INTERFACE_STATE enumerated type indicates the state of an interface.
WLAN_INTERFACE_STATE = c_uint
(wlan_interface_state_not_ready,
 wlan_interface_state_connected,
 wlan_interface_state_ad_hoc_network_formed,
 wlan_interface_state_disconnecting,
 wlan_interface_state_disconnected,
 wlan_interface_state_associating,
 wlan_interface_state_discovering,
 wlan_interface_state_authenticating) = map(WLAN_INTERFACE_STATE,
                                            range(0, 8))


class WLAN_INTERFACE_INFO(Structure):
    '''
    The WLAN_INTERFACE_STATE enumerated type indicates the state of an
    interface.
    '''
    _fields_ = [
        ("InterfaceGuid", GUID),
        ("strInterfaceDescription", c_wchar * 256),
        ("isState", WLAN_INTERFACE_STATE)
    ]


class WLAN_INTERFACE_INFO_LIST(Structure):
    '''
    The WLAN_INTERFACE_INFO_LIST structure contains an array of NIC interface
    information.
    '''
    _fields_ = [
        ("NumberOfItems", DWORD),
        ("Index", DWORD),
        ("InterfaceInfo", WLAN_INTERFACE_INFO * 1)
    ]


DOT11_MAC_ADDRESS = c_ubyte * 6
WLAN_MAX_PHY_TYPE_NUMBER = 0x8
DOT11_SSID_MAX_LENGTH = 32
WLAN_REASON_CODE = DWORD

DOT11_BSS_TYPE = c_uint
(dot11_BSS_type_infrastructure,
 dot11_BSS_type_independent,
 dot11_BSS_type_any) = map(DOT11_BSS_TYPE, range(1, 4))

# The DOT11_PHY_TYPE enumeration defines an 802.11 PHY and media type.
DOT11_PHY_TYPE = c_uint
dot11_phy_type_unknown = 0
dot11_phy_type_any = 0
dot11_phy_type_fhss = 1
dot11_phy_type_dsss = 2
dot11_phy_type_irbaseband = 3
dot11_phy_type_ofdm = 4
dot11_phy_type_hrdsss = 5
dot11_phy_type_erp = 6
dot11_phy_type_ht = 7
dot11_phy_type_IHV_start = 0x80000000
dot11_phy_type_IHV_end = 0xffffffff

# The DOT11_AUTH_ALGORITHM enumerated type defines a wireless
# LAN authentication algorithm.
DOT11_AUTH_ALGORITHM = c_uint
DOT11_AUTH_ALGO_80211_OPEN = 1
DOT11_AUTH_ALGO_80211_SHARED_KEY = 2
DOT11_AUTH_ALGO_WPA = 3
DOT11_AUTH_ALGO_WPA_PSK = 4
DOT11_AUTH_ALGO_WPA_NONE = 5
DOT11_AUTH_ALGO_RSNA = 6
DOT11_AUTH_ALGO_RSNA_PSK = 7
DOT11_AUTH_ALGO_IHV_START = 0x80000000
DOT11_AUTH_ALGO_IHV_END = 0xffffffff

# The DOT11_CIPHER_ALGORITHM enumerated type defines a cipher
# algorithm for data encryption and decryption.
DOT11_CIPHER_ALGORITHM = c_uint
DOT11_CIPHER_ALGO_NONE = 0x00
DOT11_CIPHER_ALGO_WEP40 = 0x01
DOT11_CIPHER_ALGO_TKIP = 0x02
DOT11_CIPHER_ALGO_CCMP = 0x04
DOT11_CIPHER_ALGO_WEP104 = 0x05
DOT11_CIPHER_ALGO_WPA_USE_GROUP = 0x100
DOT11_CIPHER_ALGO_RSN_USE_GROUP = 0x100
DOT11_CIPHER_ALGO_WEP = 0x101
DOT11_CIPHER_ALGO_IHV_START = 0x80000000
DOT11_CIPHER_ALGO_IHV_END = 0xffffffff


class DOT11_SSID(Structure):
    '''
    A DOT11_SSID structure contains the SSID of an interface
    '''
    _fields_ = [
        ("SSIDLength", c_ulong),
        ("SSID", c_char * DOT11_SSID_MAX_LENGTH)
    ]


# Enumerated type to define the code of connection.
WLAN_CONNECTION_MODE = c_uint
(wlan_connection_mode_profile,
 wlan_connection_mode_temporary_profile,
 wlan_connection_mode_discovery_secure,
 wlan_connection_mode_discovery_unsecure,
 wlan_connection_mode_auto,
 wlan_connection_mode_invalid) = map(WLAN_CONNECTION_MODE, range(0, 6))


class NDIS_OBJECT_HEADER(Structure):
    '''
    This Structure packages the object type, version, and size information
    that is required in many NDIS (Netword Driver interface Specification)
    Structures.
    '''
    _fields_ = [
        ("Type", c_char),
        ("Revision", c_char),
        ("Size", c_ushort)]


class DOT11_BSSID_LIST(Structure):
    '''
    The DOT11_BSSID_LIST structure contains a list of basic service set (BSS)
    identifiers.
    '''
    _fields_ = [
        ("Header", NDIS_OBJECT_HEADER),
        ("uNumOfEntries", ULONG),
        ("uTotalNumOfEntries", ULONG),
        ("BSSIDs", DOT11_MAC_ADDRESS * 1)
    ]


class WLAN_CONNECTION_PARAMETERS(Structure):
    '''
    The WLAN_CONNECTION_PARAMETERS structure specifies the parameters used when
    using the WlanConnect function.
    '''
    _fields_ = [
        ("wlanConnectionMode", WLAN_CONNECTION_MODE),
        ("strProfile", LPCWSTR),
        ("pDot11Ssid", POINTER(DOT11_SSID)),
        ("pDesiredBssidList", POINTER(DOT11_BSSID_LIST)),
        ("dot11BssType", DOT11_BSS_TYPE),
        ("dwFlags", DWORD)]


# The `WlanConnect` attempts to connect to a specific network.
WlanConnect = wlanapi.WlanConnect
WlanConnect.argtypes = (HANDLE,
                        POINTER(GUID),
                        POINTER(WLAN_CONNECTION_PARAMETERS),
                        c_void_p)
WlanConnect.restype = DWORD

# The `WlanDisconnect` method disconnects an interface from its
# current network.
WlanDisconnect = wlanapi.WlanDisconnect
WlanDisconnect.argtypes = (HANDLE,
                           POINTER(GUID),
                           c_void_p)
WlanDisconnect.restype = DWORD

# Opens a connection to the server.
WlanOpenHandle = wlanapi.WlanOpenHandle
WlanOpenHandle.argtypes = (DWORD, c_void_p, POINTER(DWORD), POINTER(HANDLE))
WlanOpenHandle.restype = DWORD

# The WlanCloseHandle method closes the connection to the server.
WlanCloseHandle = wlanapi.WlanCloseHandle
WlanCloseHandle.argtypes = (HANDLE, c_void_p)
WlanCloseHandle.restype = DWORD


class WLAN_AVAILABLE_NETWORK(Structure):
    '''
    The WLAN_INTERFACE_INFO structure contains information about a wireless
    LAN interface.
    '''
    _fields_ = [
        ("ProfileName", c_wchar * 256),
        ("dot11Ssid", DOT11_SSID),
        ("dot11BssType", DOT11_BSS_TYPE),
        ("NumberOfBssids", c_ulong),
        ("NetworkConnectable", c_bool),
        ("wlanNotConnectableReason", WLAN_REASON_CODE),
        ("NumberOfPhyTypes", c_ulong),
        ("dot11PhyTypes", DOT11_PHY_TYPE * WLAN_MAX_PHY_TYPE_NUMBER),
        ("MorePhyTypes", c_bool),
        ("wlanSignalQuality", c_ulong),
        ("SecurityEnabled", c_bool),
        ("dot11DefaultAuthAlgorithm", DOT11_AUTH_ALGORITHM),
        ("dot11DefaultCipherAlgorithm", DOT11_CIPHER_ALGORITHM),
        ("Flags", DWORD),
        ("Reserved", DWORD)]


class WLAN_AVAILABLE_NETWORK_LIST(Structure):
    '''
    The WLAN_INTERFACE_INFO_LIST structure contains an array of NIC
    interface information.
    '''
    _fields_ = [
        ("NumberOfItems", DWORD),
        ("Index", DWORD),
        ("Network", WLAN_AVAILABLE_NETWORK * 1)]


# The WlanEnumInterfaces function enumerates all of the wireless LAN interfaces
# currently enabled on the local computer.
WlanEnumInterfaces = wlanapi.WlanEnumInterfaces
WlanEnumInterfaces.argtypes = (HANDLE,
                               c_void_p,
                               POINTER(POINTER(WLAN_INTERFACE_INFO_LIST)))
WlanEnumInterfaces.restype = DWORD

# The WlanGetAvailableNetworkList function retrieves the list of available
# networks on a wireless LAN interface.
WlanGetAvailableNetworkList = wlanapi.WlanGetAvailableNetworkList
WlanGetAvailableNetworkList.argtypes = (HANDLE,
                                        POINTER(GUID),
                                        DWORD,
                                        c_void_p,
                                        POINTER(POINTER(
                                            WLAN_AVAILABLE_NETWORK_LIST)))
WlanGetAvailableNetworkList.restype = DWORD

# The WlanFreeMemory function frees memory. Any memory returned from Native
# Wifi functions must be freed.
WlanFreeMemory = wlanapi.WlanFreeMemory
WlanFreeMemory.argtypes = [c_void_p]

wireless_interfaces = None
available = None
_dict = {}

# Private methods.


def _connect(network, parameters):
    '''
    Attempts to connect to a specific network.
    '''
    global _dict
    wireless_interface = _dict[network]

    wcp = WLAN_CONNECTION_PARAMETERS()
    connection_mode = parameters['connection_mode']
    wcp.wlanConnectionMode = WLAN_CONNECTION_MODE(connection_mode)

    if connection_mode == 0 or connection_mode == 1:
        wcp.strProfile = LPCWSTR(parameters["profile"])
    else:
        wcp.strProfile = None

    dot11Ssid = DOT11_SSID()
    try:
        dot11Ssid.SSID = parameters["ssid"]
        dot11Ssid.SSIDLength = len(parameters["ssid"])
    except KeyError:
        dot11Ssid.SSID = network
        dot11Ssid.SSIDLength = len(network)
    wcp.pDot11Ssid = pointer(dot11Ssid)

    dot11bssid = DOT11_BSSID_LIST()
    bssid = parameters["bssidList"]
    dot11bssid.Header = bssid['Header']
    dot11bssid.uNumOfEntries = bssid['uNumOfEntries']
    dot11bssid.uTotalNumOfEntries = bssid['uTotalNumOfEntries']
    dot11bssid.BSSIDs = bssid['BSSIDs']

    wcp.pDesiredBssidList = pointer(dot11bssid)

    bssType = parameters["bssType"]
    wcp.dot11BssType = DOT11_BSS_TYPE(bssType)

    wcp.dwFlags = DWORD(parameters["flags"])

    NegotiatedVersion = DWORD()
    ClientHandle = HANDLE()

    wlan = WlanOpenHandle(1,
                          None,
                          byref(NegotiatedVersion),
                          byref(ClientHandle))
    if wlan:
        sys_exit(FormatError(wlan))
    pInterfaceList = pointer(WLAN_INTERFACE_INFO_LIST())
    wlan = WlanEnumInterfaces(ClientHandle, None, byref(pInterfaceList))
    if wlan:
        sys_exit(FormatError(wlan))

    try:
        wlan = WlanConnect(ClientHandle,
                           wireless_interface,
                           wcp,
                           None)
        if wlan:
            sys_exit(FormatError(wlan))
        WlanCloseHandle(ClientHandle, None)
    finally:
        WlanFreeMemory(pInterfaceList)


def _disconnect():
    '''
    To disconnect an interface form the current network.
    '''
    NegotiatedVersion = DWORD()
    ClientHandle = HANDLE()

    wlan = WlanOpenHandle(
        1,
        None,
        byref(NegotiatedVersion),
        byref(ClientHandle)
    )
    if wlan:
        sys_exit(FormatError(wlan))

    pInterfaceList = pointer(WLAN_INTERFACE_INFO_LIST())

    wlan = WlanEnumInterfaces(ClientHandle, None, byref(pInterfaceList))
    if wlan:
        sys_exit(FormatError(wlan))

    result = None
    try:
        ifaces = customresize(
            pInterfaceList.contents.InterfaceInfo,
            pInterfaceList.contents.NumberOfItems
        )

        # find each available network for each interface
        for iface in ifaces:
            wlan = WlanDisconnect(
                ClientHandle,
                byref(iface.InterfaceGuid),
                None
            )
            if wlan:
                sys_exit(FormatError(wlan))
            WlanCloseHandle(ClientHandle, None)

    finally:
        WlanFreeMemory(pInterfaceList)
        result = get_available_wifi()

    return result


def _start_scanning():
    '''
    Private method for scanning and returns the available devices.
    '''
    global available
    global wireless_interfaces
    NegotiatedVersion = DWORD()
    ClientHandle = HANDLE()

    wlan = WlanOpenHandle(
        1,
        None,
        byref(NegotiatedVersion),
        byref(ClientHandle)
    )

    if wlan:
        sys_exit(FormatError(wlan))

    # find all wireless network interfaces
    pInterfaceList = pointer(WLAN_INTERFACE_INFO_LIST())
    wlan = WlanEnumInterfaces(ClientHandle, None, byref(pInterfaceList))
    if wlan:
        sys_exit(FormatError(wlan))

    result = None
    try:
        ifaces = customresize(
            pInterfaceList.contents.InterfaceInfo,
            pInterfaceList.contents.NumberOfItems
        )

        # find each available network for each interface
        wireless_interfaces = ifaces
        for iface in ifaces:
            pAvailableNetworkList = pointer(WLAN_AVAILABLE_NETWORK_LIST())
            wlan = WlanGetAvailableNetworkList(
                ClientHandle,
                byref(iface.InterfaceGuid),
                0,
                None,
                byref(pAvailableNetworkList)
            )

            if wlan:
                sys_exit(FormatError(wlan))

            try:
                avail_net_list = pAvailableNetworkList.contents
                networks = customresize(
                    avail_net_list.Network,
                    avail_net_list.NumberOfItems
                )

                # Assigning the value of networks to the global variable
                # `available`, so it could be used in other methods.
                available = networks
                _make_dict()
                wlan = WlanDisconnect(
                    ClientHandle,
                    byref(iface.InterfaceGuid),
                    None
                )

                if wlan:
                    sys_exit(FormatError(wlan))
                WlanCloseHandle(ClientHandle, None)

            finally:
                WlanFreeMemory(pAvailableNetworkList)

    finally:
        WlanFreeMemory(pInterfaceList)
        result = get_available_wifi()

    return result


def _get_network_info(name):
    '''
    returns the list of the network selected in a dict.
    '''
    global available
    global _dict

    net = _dict[name]
    dot11BssType = net.dot11BssType
    dot11DefaultAuthAlgorithm = net.dot11DefaultAuthAlgorithm
    dot11DefaultCipherAlgorithm = net.dot11DefaultCipherAlgorithm
    dot11PhyTypes = net.dot11PhyTypes[0]
    dot11Ssid = net.dot11Ssid
    wlanNotConnectableReason = net.wlanNotConnectableReason
    wlanSignalQuality = net.wlanSignalQuality
    return {"dot11BssType": dot11BssType,
            "dot11DefaultAuthAlgorithm": dot11DefaultAuthAlgorithm,
            "dot11DefaultCipherAlgorithm": dot11DefaultCipherAlgorithm,
            "dot11PhyTypes": dot11PhyTypes,
            "SSID": dot11Ssid.SSID,
            "SSIDLength": dot11Ssid.SSIDLength,
            "wlanNotConnectableReason": wlanNotConnectableReason,
            "wlanSignalQuality": wlanSignalQuality}


def _make_dict():
    '''
    Prepares a dict so it could store network information.
    '''
    global available
    global _dict
    _dict = {}
    for network in available:
        _dict[network.dot11Ssid.SSID.decode('utf-8')] = network


def _get_available_wifi():
    '''
    returns the available wifi networks.
    '''
    global _dict
    return _dict


def _is_enabled():
    '''
    Reason for returning true is explained in widi facade.
    /plyer/facades/wifi.py
    '''
    return True

# public methods.


def is_enabled():
    '''
    calls private method `_is_enabled` and returns the result.
    '''
    return _is_enabled()


def connect(network, parameters):
    '''
    Connect to a network with following parameters.
    '''
    _connect(network=network, parameters=parameters)


def disconnect():
    '''
    Disconnect from a network.
    '''
    _disconnect()


def start_scanning():
    '''
    Start scanning for available wifi networks available.
    '''
    return _start_scanning()


def get_network_info(name):
    '''
    return the wifi network info.
    '''
    return _get_network_info(name=name)


def get_available_wifi():
    '''
    return the available wifi networks available
    '''
    return _get_available_wifi()
