import os
import sys
sys.path.append('D:\\Python\\MyTools')
import tools
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learning.settings")
import django
django.setup()
from network.models import Device

device_type_pattern = ['Hardware\s+cisco (\S+ \S+)','cisco (\S+ \S+) processor','Hardware:\s+(\S+),']
version_pattern = ['System version: (.*?)\n',', Version (\S+)\(','ROM: (\d+\.\d+)\(','Software Version (.*?)\n']

def get_device_type_version(path):
    r = tools.findallfilesbyname(path,'show version')
    device_type = ''
    version = ''
    if len(r) == 1:
        f = open(r[0],'r')
        content = f.read()
        f.close()
        device_type = tools.get_keywords(device_type_pattern,content)
        version = tools.get_keywords(version_pattern,content)
        return (device_type,version)
    else:
        return ''

def get_device_name(whole_str):
    t = re.search('hostname (\S+)',whole_str)
    if t:
        return t.groups()[0]
    else:
        return ''

def get_running_config(path):
    r = tools.findallfilesbyCondition(path,findrun)
    if len(r) == 1:
        f = open(r[0],'r')
        content = f.read()
        f.close()
        return content
    else:
        return ''
        
def get_device_mngIP(path):
    '''
    input is a path.
    output is the IP of the device. If can not find the IP, return ''
    '''
    t = re.search('(\d+\.\d+\.\d+\.\d+)',path)
    if t:
        return t.groups()[0]
    else:
        return ''

def findrun(filename):
    if re.search(r'show run.txt',filename):
        return True
    elif re.search(r'show running-config.txt',filename):
        return True
    else:
        return False

def import_devices(path,error_log):
    device_number = 0
    try:
        folders = os.listdir(path)
    except OSError as e:
        print (e)
        raise e

    for folder in folders:
        file_path = os.path.join(path,folder)
        IP = get_device_mngIP(file_path)
        if len(IP) == 0:
            error_log.add_error('Can not find device IP in this folder %s' % folder)
            continue

        running_config = get_running_config(file_path)
        if len(running_config) == 0:
            error_log.add_error('Can not find configuration file in this folder %s' % folder)
            continue

        device_name = get_device_name(running_config)
        if len(device_name) > 0:
            try:
                d,isNew = Device.objects.get_or_create(hostname = device_name)
                d.Mgt_IP = IP
                d.running_configure = running_config
            except Exception as e:
                error_log.add_error(str(e))
        else:
            error_log.add_error('Can not find hostname in this folder %s' % folder)
            del d
            continue
        
        d.description = device_name
        d.device_type,d.version = get_device_type_version(file_path)

        try:
            d.save()
            error_log.add_info('%s has been added' % device_name)
            device_number +=1
        except Exception as e:
            error_log.add_error('Device %s Add error'% device_name)
            error_log.add_error(str(e))

    return device_number


if __name__ == "__main__":
    log_root = r'D:\Python\log\20181102220753\txt'
    error = tools.log_tools()
    r = import_devices(log_root,error)
    print ('%d devices were added or updated' % (r,))
    print (error.infos)
    for e in error.error_logs:
        print(e)

#   folders = os.listdir(log_root)
#    for l in folders:
#        (device_type,version) = get_device_type_version(os.path.join(log_root,l))
#        print (l)
#        print (device_type,version)





    