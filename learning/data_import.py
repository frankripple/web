''' An py for data import based on Django modules'''
import os
import re
import django
from MyTools import tools

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learning.settings")
django.setup()
from network.models import Device



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

def import_devices(path):
    '''
        Main function for import device information from txt files to databases
        Args:
            Path is a folder which content some folders named by device IP and name.
            In each folder, there are some txt files collected from devices.
    '''
    device_number = 0
    try:
        folders = os.listdir(path)
    except OSError as _e:
        print(_e)
        raise _e

    for folder in folders:
        file_path = os.path.join(path, folder)
        _ip = get_device_mngip(file_path)
        if _ip is None:
            tools.LOGS.add_error('Can not find device IP in this folder %s' % folder)
            continue

        try:
            _running_config = get_running_config(file_path)
        except NotADirectoryError as _e:
            tools.LOGS.add_error(_e)
            continue

        if _running_config is None:
            tools.LOGS.add_error('Can not find configuration file in this folder %s' % folder)
            continue

        _device_name = get_device_name(_running_config)
        if _device_name is not None:
            try:
                _device, _ = Device.objects.get_or_create(hostname=_device_name)
                _device.Mgt_IP = _ip
                _device.running_configure = _running_config
            except django.db.utils.OperationalError as _e:
                tools.LOGS.add_error(str(_e))
        else:
            tools.LOGS.add_error('Can not find hostname in this folder %s' % folder)
            del _device
            continue
        _device.description = _device_name
        _device.device_type, _device.version = get_device_type_version(file_path)

        try:
            _device.save()
            tools.LOGS.add_info('%s has been added' % _device_name)
            device_number += 1
        except django.db.utils.OperationalError as _e:
            tools.LOGS.add_error('Device %s Add error'% _device_name)
            tools.LOGS.add_error(str(_e))

    return device_number



if __name__ == "__main__":
    LOG_ROOT = r'D:\Python\log\20181102220753\txt'
    """
    DEVICE_NUMBER = import_devices(LOG_ROOT)
    print('%d devices were added or updated' % (DEVICE_NUMBER,))
    print(tools.LOGS.infos)
    for _error_log in tools.LOGS.error_tools.LOGS:
        print(_error_log)
    """
