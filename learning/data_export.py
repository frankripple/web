''' An py for data export based on Django modules'''
import os
import csv
import django

from MyTools import tools

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learning.settings")
django.setup()
from network.models import Device, Interface

def list_write_to_csv(file_name, content, header=None):
    '''
        Output all content to a csv file.
        Args:
            file_name:
                Full name of the CSV file
            content:
                List which need to be written.
            header:
                if there is header, add it.
        Returns:
        Raises:
            IOError: If can not open or write the file.
    '''
    try:
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(content)
    except IOError as _e:
        tools.LOGS.add_error(_e)
        return False
    return True

def export_devices_to_csv(file_name):
    '''
    Export devices information from database to some files.
    Args:
        file_name: the name of the result file.
    Returns:
        The device number which was exported successfully
    Raise:
        Connectionerror:
            if the database can not be connected.
    '''
    device_number = 0
    try:
        device_number = Device.objects.count()
    except django.db.utils.OperationalError as _e:
        tools.LOGS.add_error('Can not connect the database.')
        return -1

    device_list = Device.objects.all().values_list(
        'hostname', 'Mgt_IP', 'description', 'device_type', 'version'
        )
    header = ['hostname', 'Mgt_IP', 'description', 'device_type', 'version']

    if not list_write_to_csv(file_name, device_list, header):
        return -1
    return device_number

def export_interface_ip_to_csv(file_name):
    '''
    Export interface ip information from database to some files.
    Args:
        file_name: the name of the result file.
    Returns:
        The interface number which was exported successfully
    Raise:
        Connectionerror:
            if the database can not be connected.
    '''
    interface_number = -1
    try:
        interface_number = Interface.objects.filter(iIP__isnull=False).count()
    except django.db.utils.OperationalError as _e:
        tools.LOGS.add_error('Can not connect the database.')
        return -1

    interface_list = Interface.objects.filter(iIP__isnull=False)
    result = list()
    for _i in interface_list:
        result.append(
            (_i.iDevice.hostname, _i.iName, _i.description, _i.iIP)
        )
    # Did not know if there is better solution for foreignkey values
    header = ['iDevice', 'iName', 'description', 'iIP']

    if not list_write_to_csv(file_name, result, header):
        return -1

    return interface_number

if __name__ == "__main__":
    LOG_ROOT = r'D:\Python\log\result'
    '''
    DEVICE_NUMBER = import_devices(LOG_ROOT)
    print('%d devices were added or updated' % (DEVICE_NUMBER,))
    print(LOGS.infos)
    for _error_log in LOGS.error_logs:
        print(_error_log)
    '''
    print(export_interface_ip_to_csv('interface_ip.csv'))
    print(tools.LOGS.errors)
