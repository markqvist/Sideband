from pyobjus import autoclass
from pyobjus.dylib_manager import load_framework, INCLUDE

from plyer.facades import Wifi

load_framework(INCLUDE.Foundation)
load_framework(INCLUDE.CoreWLAN)

CWInterface = autoclass('CWInterface')
CWNetwork = autoclass('CWNetwork')
CWWiFiClient = autoclass('CWWiFiClient')
NSArray = autoclass('NSArray')
NSDictionary = autoclass('NSDictionary')
NSString = autoclass('NSString')


class OSXWifi(Wifi):
    names = {}

    def _is_enabled(self):
        '''
        Returns `True` if the Wifi is enabled else  returns `False`.
        '''
        return CWWiFiClient.sharedWiFiClient().interface().powerOn()

    def _get_network_info(self, name):
        '''
        Returns all the network information.
        '''

        accessNetworkType = self.names[name].accessNetworkType
        aggregateRSSI = self.names[name].aggregateRSSI
        beaconInterval = self.names[name].beaconInterval
        bssid = self.names[name].bssid.UTF8String()
        countryCode = self.names[name].countryCode
        hasInternet = self.names[name].hasInternet
        hasInterworkingIE = self.names[name].hasInterworkingIE
        hessid = self.names[name].hessid
        ibss = self.names[name].ibss
        isAdditionalStepRequiredForAccess = \
            self.names[name].isAdditionalStepRequiredForAccess
        isCarPlayNetwork = self.names[name].isCarPlayNetwork
        isEmergencyServicesReachable = \
            self.names[name].isEmergencyServicesReachable
        isPasspoint = self.names[name].isPasspoint
        isPersonalHotspot = self.names[name].isPersonalHotspot
        isUnauthenticatedEmergencyServiceAccessible = \
            self.names[name].isUnauthenticatedEmergencyServiceAccessible
        noiseMeasurement = self.names[name].noiseMeasurement
        physicalLayerMode = self.names[name].physicalLayerMode
        rssiValue = self.names[name].rssiValue
        securityType = self.names[name].securityType
        ssid = self.names[name].ssid.UTF8String()
        supportsEasyConnect = self.names[name].supportsEasyConnect
        supportsWPS = self.names[name].supportsWPS
        venueGroup = self.names[name].venueGroup
        venueType = self.names[name].venueType

        return {'accessNetworkType': accessNetworkType,
                'aggregateRSSI': aggregateRSSI,
                'beaconInterval': beaconInterval,
                'bssid': bssid,
                'countryCode': countryCode,
                'hasInternet': hasInternet,
                'hasInterworkingIE': hasInterworkingIE,
                'hessid': hessid,
                'ibss': ibss,
                'isAdditionalStepRequiredForAccess':
                isAdditionalStepRequiredForAccess,
                'isCarPlayNetwork': isCarPlayNetwork,
                'isEmergencyServicesReachable': isEmergencyServicesReachable,
                'isPasspoint': isPasspoint,
                'isPersonalHotspot': isPersonalHotspot,
                'isUnauthenticatedEmergencyServiceAccessible':
                isUnauthenticatedEmergencyServiceAccessible,
                'noiseMeasurement': noiseMeasurement,
                'physicalLayerMode': physicalLayerMode,
                'rssiValue': rssiValue,
                'securityType': securityType,
                'ssid': ssid,
                'supportsEasyConnect': supportsEasyConnect,
                'supportsWPS': supportsWPS,
                'venueGroup': venueGroup,
                'venueType': venueType}

    def _start_scanning(self):
        '''
        Starts scanning for available Wi-Fi networks.
        '''
        if self._is_enabled():
            self.names = {}
            c = CWInterface.interface()
            scan = c.scanForNetworksWithName_error_(None, None)
            cnt = scan.allObjects().count()
            for i in range(cnt):
                self.names[
                    scan.allObjects().objectAtIndex_(i).ssid.UTF8String()
                ] = scan.allObjects().objectAtIndex_(i)
        else:
            raise Exception("Wifi not enabled.")

    def _get_available_wifi(self):
        '''
        Returns the name of available networks.
        '''
        return self.names.keys()

    def _connect(self, network, parameters):
        '''
        Expects 2 parameters:
            - name/ssid of the network.
            - password: dict type
        '''
        password = parameters['password']
        network_object = self.names[network]
        CWInterface.interface().associateToNetwork_password_error_(
            network_object,
            password,
            None)
        return

    def _disconnect(self):
        '''
        Disconnect from network.
        '''
        CWInterface.interface().disassociate()
        return

    def _disable(self):
        '''
        Wifi interface power state is set to "OFF".
        '''

        interface = CWWiFiClient.sharedWiFiClient().interface()
        interface.setPower_error_(False, None)

    def _enable(self):
        '''
        Wifi interface power state is set to "ON".
        '''

        interface = CWWiFiClient.sharedWiFiClient().interface()
        interface.setPower_error_(True, None)


def instance():
    return OSXWifi()
