''' An py for data import based on Django modules'''
import os
import re
import django
from MyTools import tools

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learning.settings")
django.setup()
from network.models import Device, Interface



def get_device_type_version(path):
    '''
    Get device version and  from version files with REG

    Args:
        path: the file path of the version file

    Returns:
        empty str '': if there is no version file or multiple files, return '';
        (device_type, version): a 2-tuple with
    '''
    _device_type_patterns = [
        r'Hardware\s+cisco (\S+ \S+)',
        r'cisco (\S+ \S+) processor',
        r'Hardware:\s+(\S+),'
    ]
    _version_patterns = [
        r'System version: (.*?)\n',
        r', Version (\S+)\(',
        r'ROM: (\d+\.\d+)\(',
        r'Software Version (.*?)\n'
    ]

    _r = tools.findallfilesbyname(path, 'show version')
    device_type = ''
    version = ''
    if len(_r) == 1:
        _f = open(_r[0], 'r')
        content = _f.read()
        _f.close()
        try:
            device_type = tools.get_keywords(_device_type_patterns, content)
            version = tools.get_keywords(_version_patterns, content)
        except re.error as _e:
            tools.LOGS.add_error(_e)
    return (device_type, version)

def get_device_name(whole_str):
    '''
        Search the string and find device name.
        Returns:
            If there is a match, return a device name
            If there is no match, return None
    '''
    _t = re.search(r'hostname (\S+)', whole_str)
    if _t:
        return _t.groups()[0]
    return None

def get_running_config(path):
    '''
        Search the whole configuration in the path.
        Returns:
            If there is a match, return whole content of the file
            If there is no match and multiple matches, return None
        Raises:
            NotADirectoryError: if the path is not a folder.
    '''
    _r = tools.findallfilesbycondition(path, findrun)
    if len(_r) == 1:
        _f = open(_r[0], 'r')
        content = _f.read()
        _f.close()
        return content
    return None

def get_device_mngip(path):
    '''
    input is a path.
    output is the IP of the device. If can not find the IP, return None
    '''
    _t = re.search(r'(\d+\.\d+\.\d+\.\d+)', path)
    if _t:
        return _t.groups()[0]
    return None

def findrun(filename):
    ''' the condition to match configuraiton file    '''
    if re.search(r'show run.txt', filename) or \
       re.search(r'show running-config.txt', filename):
        return True
    return False

def get_cdp_information(path):
    '''
        Get cdp interface in a dict. Key is interface name and value is a tulpe
            {
                'local_interface_name': ('peer_device_name', 'peer_interface_name')
                if source is 'show cdp neighbor.txt', key is the number of the interface
                '8/11': ('XXXXXXX_002', Ethernet5/5)
                if source is 'show cdp neighbor detail.txt', key is the fullname of the interface
                'Ethernet8/11': ('XXXXXXX_002', Ethernet5/5)
            }
        Args:
            path: fullpath of cdp file
        Return:
            cdp_information in a dict
    '''
    result = dict()
    content = ''
    informations = None
    try:
        with open(os.path.join(path, 'show cdp neighbor detail.txt'), 'r') as cdp_file:
            content = cdp_file.read()
            informations = re.findall( \
                r'Device ID:\s?(\S+?)\..*?Interface: (\S+),\s+Port ID \(outgoing port\): (\S+)',
                content, re.S)
                #r'Device ID:\s?(\S+).*?Interface: (\S+), Port ID \(outgoing port\): (\S+)',
                #Change the pattern to get only interface number not name.
                #To keep same between interface fullname and short name  (Ethernet3/37 and Eth3/37)
                #Errors for this RE:
                #    1. \S to match non space characters
                #    2. There is space afte \n
                #    3. \( and \) to match ()
                #    4. re.S to let dot to match \n, \t etc
    except IOError as _e:
        try:
            with open(os.path.join(path, 'show cdp neighbor.txt'), 'r') as cdp_file:
                content = cdp_file.read()
        except IOError as _e:
            try:
                with open(os.path.join(path, 'show cdp nei.txt'), 'r') as cdp_file:
                    content = cdp_file.read()
                #  history versions: r'(\S+?)\..*?\n.*?(\d+/\d+).*?(\S{3}\s?\d+/\d+)\s+\n',
            except IOError as _e:
                tools.LOGS.add_error('Can not find neighbor files in folder %s'% path)
                return result

        informations = re.findall( \
            r'(\S+?)\.[^\n]*?\n[^\n]*?(\d+/\d+)[^\n]*?(\S{3}\s?\d+/\d+)\s+\n',
            content, re.S)


    if informations:
        for device_name, local_interface, remote_interface in informations:
            result[local_interface] = (device_name, remote_interface)
    else:
        if len(content) > 100:
            tools.LOGS.add_info('There is information in files. Maybe the pattarn is error!')
    return result

def get_information_from_cdp(interface_name, cdp_information):
    '''
        Get remote_device_name and interface name from cdp information.
        Args:
            cdp_information:
                It is a dict like this
                    {
                        'local_interface_name': ('peer_device_name', 'peer_interface_name')
                        if source is 'show cdp neighbor.txt', key is the number of the interface
                        '8/11': ('XXXXXXX_002', Ethernet5/5)
                        if source is 'show cdp neighbor detail.txt', key is the fullname
                        'Ethernet8/11': ('XXXXXXX_002', Ethernet5/5)
                    }
        Returns:
            A tuple include ('peer_device_name', 'peer_interface_name')
    '''

    if cdp_information:
        if interface_name in cdp_information:
            return cdp_information[interface_name]

        _r = re.search(r'\d+/\d+', interface_name)
        if _r:
            interface_number = _r.group()
            return cdp_information.get(interface_number, (None, None))
    return (None, None)

def import_interfaces(device, cdp_information=None):
    '''
        import interface information from configuration of device
        Input:
            device:
                the instance of device which these interfaces belongs to.
            cdp_information:
                content of show cdp neighbor detail
        Returns:
            Number of interfaces which were added successfully
    '''
    _interface_name = re.compile(r'^interface (\S+)')
    _interface_description = re.compile(r'description (.*)\s+')
    _interface_ip = re.compile(r'ip address (\d+\.\d+\.\d+\.\d+)')
    _interface_trunk_vlan = re.compile(r'switchport trunk allowed vlan (.*)')
    _interface_access_vlan = re.compile(r'switchport access vlan (\d+)')
    interface = None
    for _l in device.running_configure.split('\n'):
        _t = _interface_name.search(_l)
        if _t:
            if interface is not None:
                interface.remote_device_name, interface.remote_interface_name = \
                get_information_from_cdp(interface.iName, cdp_information)
                interface.save()
                interface, _ = Interface.objects.get_or_create(iName=_t.group(1), iDevice=device)
            else:
                interface, _ = Interface.objects.get_or_create(iName=_t.group(1), iDevice=device)

        if interface is not None:
            _t = _interface_description.search(_l)
            if _t:
                interface.description = _t.group(1)

            _t = _interface_ip.search(_l)
            if _t:
                interface.iIP = _t.group(1)
                interface.iType = 1

            _t = _interface_trunk_vlan.search(_l)
            if _t:
                interface.iVlan = _t.group(1)
                interface.iType = 2

            _t = _interface_access_vlan.search(_l)
            if _t:
                interface.iVlan = _t.group(1)
                interface.iType = 2

    if interface is not None:
        interface.remote_device_name, interface.remote_interface_name = \
        get_information_from_cdp(interface.iName, cdp_information)
        interface.save()

def import_device_from_folder(folder_name):
    '''
        Import information from folder named by IPADDRESS_HOSTNAME, Like 176.1.1.222_A-XXX-CCC-CS01
        Args:
            folder_name:
        Returns:
            Model device: model device from Django. If add failed, return None
    '''
    _ip = get_device_mngip(folder_name)
    if _ip is None:
        tools.LOGS.add_error('Can not find device IP in this folder %s' % folder_name)
        return None

    try:
        _running_config = get_running_config(folder_name)
    except NotADirectoryError as _e:
        tools.LOGS.add_error(_e)
        return None

    if _running_config is None:
        tools.LOGS.add_error('Can not find configuration file in this folder %s' % folder_name)
        return None
    _device_name = get_device_name(_running_config)
    if _device_name is not None:
        try:
            _device, _ = Device.objects.get_or_create(hostname=_device_name)
            _device.Mgt_IP = _ip
            _device.running_configure = _running_config
        except django.db.utils.OperationalError as _e:
            tools.LOGS.add_error(str(_e))
            return None
    else:
        tools.LOGS.add_error('Can not find hostname in this folder %s' % folder_name)
        return None
    _device.description = _device_name
    _device.device_type, _device.version = get_device_type_version(folder_name)

    try:
        _device.save()
        tools.LOGS.add_info('%s has been added' % _device_name)
        return _device
    except django.db.utils.OperationalError as _e:
        tools.LOGS.add_error('Device %s Add error'% _device_name)
        tools.LOGS.add_error(str(_e))
        return None

def import_device_interface_from_file(path):
    '''
        Top level function
        Main function for import device information from txt files to databases
        Args:
            Path is a folder which content some folders named by device IP and name.
            In each folder, there are some txt files collected from devices.
    '''
    device_number = 0
    try:
        folders = os.listdir(path)
    except OSError as _e:
        raise _e

    for folder in folders:
        device = import_device_from_folder(os.path.join(path, folder))
        if device:
            device_number += 1
            import_interfaces(device, get_cdp_information(os.path.join(path, folder)))
            tools.LOGS.add_info('Device %s was updated or added successfully'% device.hostname)
    return device_number

def update_cdp_information(path):
    '''
        Top level function
        Main function for update information from txt files to databases
        Args:
            Path is a folder which content some folders named by device IP and name.
            In each folder, there are some txt files collected from devices.
    '''
    #TODO Need more test case for this function
    device_number = 0
    try:
        folders = os.listdir(path)
    except OSError as _e:
        print(_e)
        raise _e

    device_name_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+_(\S+)')
    for folder in folders:
        _r = device_name_pattern.search(folder)
        if _r:
            device = Device.objects.get(hostname=_r.group(1))
            if device:
                device_number += 1
                _t = get_cdp_information(os.path.join(path, folder))
                if _t:
                    for interface_number, remote in _t.items():
                        Interface.objects.filter(iName__endswith=interface_number)\
                        .update(remote_device_name=remote[0], remote_interface_name=remote[1])

def clear_all_interfaces():
    '''
        Top level function
        Main function for Clear all interfaces information in database
        Args:
            NONE
    '''
    Interface.objects.all().delete()

if __name__ == "__main__":
    #LOG_ROOT = r'D:\Python\log\result'

    LOG_ROOT = r'D:\Python\log\20181102220753\txt'
    #clear_all_interfaces()
    DEVICE_NUMBER = import_device_interface_from_file(LOG_ROOT)

    for _error_log in tools.LOGS.error_logs:
        print(_error_log)

    with open('logs.txt', 'w') as f:
        f.writelines(tools.LOGS.info_logs)
