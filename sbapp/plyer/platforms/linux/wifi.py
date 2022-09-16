'''
.. note::
   This facade depends on `nmcli` (Network Manager command line tool).
   It's found in most of the popular GNU/Linux distributions. Support for other
   backends is not provided yet.
'''

from subprocess import Popen, PIPE, call
from plyer.facades import Wifi
from plyer.utils import whereis_exe, deprecated

try:
    import wifi
except ModuleNotFoundError as err:
    raise ModuleNotFoundError(
            "python-wifi not installed. try:" +
            "`pip install --user wifi`.") from err


class NMCLIWifi(Wifi):
    '''
    .. versionadded:: 1.4.0
    '''

    def __init__(self, *args, **kwargs):
        '''
        .. versionadded:: 1.4.0
        '''

        super().__init__(*args, **kwargs)
        self.names = {}

    @property
    def interfaces(self):
        '''
        Get all the available interfaces for WiFi.

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        if not self._is_enabled():
            self._enable()

        # fetch the devices
        proc = Popen([
            'nmcli', '--terse',
            '--fields', 'DEVICE,TYPE',
            'device'
        ], stdout=PIPE)
        lines = proc.communicate()[0].decode('utf-8').splitlines()

        # filter devices by type
        interfaces = []
        for line in lines:
            # bad escape from nmcli's side :<
            line = line.replace('\\:', '$$')
            device, dtype = line.split(':')
            if dtype != 'wifi':
                continue
            interfaces.append(device.replace('$$', ':'))

        # return wifi interfaces
        return interfaces

    def _is_enabled(self):
        '''
        Return the status of WiFi device.

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        output = Popen(
            ["nmcli", "radio", "wifi"],
            stdout=PIPE
        ).communicate()[0].decode('utf-8')

        if output.split()[0] == 'enabled':
            return True
        return False

    def _is_connected(self, interface=None):
        '''
        Return whether a specified interface is connected to a WiFi network.

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        if not self._is_enabled():
            self._enable()
        if not interface:
            interface = self.interfaces[0]

        # fetch all devices
        proc = Popen([
            'nmcli', '--terse',
            '--fields', 'DEVICE,TYPE,STATE',
            'device'
        ], stdout=PIPE)
        lines = proc.communicate()[0].decode('utf-8').splitlines()

        # filter by wifi type and interface
        connected = False
        for line in lines:
            line = line.replace('\\:', '$$')
            device, dtype, state = line.split(':')
            device = device.replace('$$', ':')
            if dtype != 'wifi':
                continue

            if device != interface:
                continue

            if state == 'connected':
                connected = True

        return connected

    def _start_scanning(self, interface=None):
        '''
        Start scanning for available Wi-Fi networks
        for the specified interface.

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        if not self._is_enabled():
            self._enable()
        if not interface:
            interface = self.interfaces[0]

        # force rescan for fresh data
        call(['nmcli', 'device', 'wifi', 'rescan', 'ifname', interface])

        # get properties
        fields = [
            'SSID', 'BSSID', 'MODE', 'CHAN', 'FREQ',
            'BARS', 'RATE', 'SIGNAL', 'SECURITY'
        ]

        # fetch all networks for interface
        output = Popen([
            'nmcli', '--terse',
            '--fields', ','.join(fields),
            'device', 'wifi', 'list', 'ifname', interface
        ], stdout=PIPE).communicate()[0].decode('utf-8')

        # parse output
        for line in output.splitlines():
            line = line.replace('\\:', '$$')
            row = {
                field: value
                for field, value in zip(fields, line.split(':'))
            }

            row['BSSID'] = row['BSSID'].replace('$$', ':')
            self.names[row['SSID']] = row

    def _get_network_info(self, name):
        '''
        Get all the network information by network's name (SSID).

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        if not self.names:
            self._start_scanning()

        ret_list = {}
        ret_list['ssid'] = self.names[name]['SSID']
        ret_list['signal'] = self.names[name]['SIGNAL']

        bars = len(self.names[name]['BARS'])
        ret_list['quality'] = '{}/100'.format(bars / 5.0 * 100)
        ret_list['frequency'] = self.names[name]['FREQ']
        ret_list['bitrates'] = self.names[name]['RATE']

        # wpa1, wpa2, wpa1 wpa2, wep, (none), perhaps something else
        security = self.names[name]['SECURITY'].lower()
        ret_list['encrypted'] = True
        if 'wpa2' in security:
            # wpa2, wpa2+wpa1
            ret_list['encryption_type'] = 'wpa2'
        elif 'wpa' in security:
            ret_list['encryption_type'] = 'wpa'
        elif 'wep' in security:
            ret_list['encryption_type'] = 'wep'
        elif 'none' in security:
            ret_list['encrypted'] = False
            ret_list['encryption_type'] = 'none'
        else:
            ret_list['encryption_type'] = security

        ret_list['channel'] = int(self.names[name]['CHAN'])
        ret_list['address'] = self.names[name]['BSSID']
        ret_list['mode'] = self.names[name]['MODE']
        return ret_list

    def _get_available_wifi(self):
        '''
        Return the names of all found networks.

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        if not self.names:
            self._start_scanning()
        return list(self.names.keys())

    def _connect(self, network, parameters, interface=None):
        '''
        Connect a specific interface to a WiFi network.

        Expects 2 parameters:
            - SSID of the network
            - parameters: dict
                - password: string or None

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        self._enable()
        if not interface:
            interface = self.interfaces[0]

        password = parameters.get('password')
        command = [
            'nmcli', 'device', 'wifi', 'connect', network,
            'ifname', interface
        ]
        if password:
            command += ['password', password]
        call(command)

    def _disconnect(self, interface=None):
        '''
        Disconnect a specific interface from a WiFi network.

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        if not self._is_enabled():
            return

        if not interface:
            interface = self.interfaces[0]

        if self._nmcli_version() >= (1, 2, 6):
            call(['nmcli', 'device', 'disconnect', interface])
        else:
            call(['nmcli', 'nm', 'enable', 'false'])

    def _enable(self):
        '''
        Turn WiFi device on.

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        call(['nmcli', 'radio', 'wifi', 'on'])

    def _disable(self):
        '''
        Turn WiFi device off.

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        call(['nmcli', 'radio', 'wifi', 'off'])

    def _nmcli_version(self):
        '''
        Get nmcli version to prevent executing deprecated commands.

        .. versionadded:: 1.4.0
           Tested with nmcli 1.2.6.
        '''
        version = Popen(['nmcli', '-v'], stdout=PIPE)
        version = version.communicate()[0].decode('utf-8')
        while version and not version[0].isdigit():
            version = version[1:]
        return tuple(map(int, (version.split('.'))))


@deprecated
class LinuxWifi(Wifi):
    '''
    .. versionadded:: 1.2.5
    '''

    def __init__(self, *args, **kwargs):
        '''
        .. versionadded:: 1.4.0
        '''

        super().__init__(*args, **kwargs)
        self.names = {}

    @property
    def interfaces(self):
        '''
        .. versionadded:: 1.4.0
        '''

        proc = Popen([
            'nmcli', '--terse',
            '--fields', 'DEVICE,TYPE',
            'device'
        ], stdout=PIPE)
        lines = proc.communicate()[0].decode('utf-8').splitlines()

        interfaces = []
        for line in lines:
            device, dtype = line.split(':')
            if dtype != 'wifi':
                continue
            interfaces.append(device)

        return interfaces

    def _is_enabled(self):
        '''
        Returns `True` if wifi is enabled else `False`.

        .. versionadded:: 1.2.5
        .. versionchanged:: 1.3.2
            nmcli output is properly decoded to unicode
        '''
        enbl = Popen(["nmcli", "radio", "wifi"], stdout=PIPE, stderr=PIPE)
        if enbl.communicate()[0].split()[0].decode('utf-8') == "enabled":
            return True
        return False

    def _is_connected(self, interface=None):
        '''
        .. versionadded:: 1.4.0
        '''

        if not interface:
            interface = self.interfaces[0]

        proc = Popen([
            'nmcli', '--terse',
            '--fields', 'DEVICE,TYPE,STATE',
            'device'
        ], stdout=PIPE)
        lines = proc.communicate()[0].decode('utf-8').splitlines()

        connected = False
        for line in lines:
            device, dtype, state = line.split(':')
            if dtype != 'wifi':
                continue

            if device != interface:
                continue

            if state == 'connected':
                connected = True

        return connected

    def _start_scanning(self, interface=None):
        '''
        Returns all the network information.

        .. versionadded:: 1.2.5
        .. versionchanged:: 1.3.0
            scan only if wifi is enabled
        '''

        if not interface:
            interface = self.interfaces[0]

        if self._is_enabled():
            list_ = list(wifi.Cell.all(interface))
            for i in range(len(list_)):
                self.names[list_[i].ssid] = list_[i]
        else:
            raise Exception('Wifi not enabled.')

    def _get_network_info(self, name):
        '''
        Starts scanning for available Wi-Fi networks and returns the available,
        devices.

        .. versionadded:: 1.2.5
        '''
        ret_list = {}
        ret_list['ssid'] = self.names[name].ssid
        ret_list['signal'] = self.names[name].signal
        ret_list['quality'] = self.names[name].quality
        ret_list['frequency'] = self.names[name].frequency
        ret_list['bitrates'] = self.names[name].bitrates
        ret_list['encrypted'] = self.names[name].encrypted
        ret_list['channel'] = self.names[name].channel
        ret_list['address'] = self.names[name].address
        ret_list['mode'] = self.names[name].mode
        if not ret_list['encrypted']:
            return ret_list
        else:
            ret_list['encryption_type'] = self.names[name].encryption_type
            return ret_list

    def _get_available_wifi(self):
        '''
        Returns the name of available networks.

        .. versionadded:: 1.2.5
        .. versionchanged:: 1.4.0
            return a proper list of elements instead of dict_keys
        '''
        return list(self.names.keys())

    def _connect(self, network, parameters, interface=None):
        '''
        Expects 2 parameters:
            - name/ssid of the network.
            - parameters: dict type
                - password: string or None

        .. versionadded:: 1.2.5
        '''
        if not interface:
            interface = self.interfaces[0]

        result = None
        try:
            self._enable()
        finally:
            password = parameters['password']
            cell = self.names[network]
            result = wifi.Scheme.for_cell(
                interface, network, cell, password
            )
        return result

    def _disconnect(self, interface=None):
        '''
        Disconnect all the networks managed by Network manager.

        .. versionadded:: 1.2.5
        '''
        if not interface:
            interface = self.interfaces[0]

        if self._nmcli_version() >= (1, 2, 6):
            call(['nmcli', 'dev', 'disconnect', interface])
        else:
            call(['nmcli', 'nm', 'enable', 'false'])

    def _enable(self):
        '''
        Wifi interface power state is set to "ON".

        .. versionadded:: 1.3.2
        '''
        return call(['nmcli', 'radio', 'wifi', 'on'])

    def _disable(self):
        '''
        Wifi interface power state is set to "OFF".

        .. versionadded:: 1.3.2
        '''
        return call(['nmcli', 'radio', 'wifi', 'off'])

    def _nmcli_version(self):
        '''
        .. versionadded:: 1.3.2
        '''
        version = Popen(['nmcli', '-v'], stdout=PIPE)
        version = version.communicate()[0].decode('utf-8')
        while version and not version[0].isdigit():
            version = version[1:]
        return tuple(map(int, (version.split('.'))))


def instance():
    if whereis_exe('nmcli'):
        return NMCLIWifi()

    return LinuxWifi()
