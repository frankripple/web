''' An py for data export based on Django modules'''
import os
import csv
import django

from MyTools import tools

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learning.settings")
django.setup()
from network.models import Device

def export_devices_to_csv(file_name):
    '''
    Export devices information from database to some files.
    Args:
        file_name: the name of the result file.
    Returns:
        The device number which was exported successfully
    Raise:
        OSerror:
            if the file_name can not be read.
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
    #print(device_list)
    try:
        with open(file_name, 'w', newline='') as csvfile:
            header = ['hostname', 'Mgt_IP', 'description', 'device_type', 'version']
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(device_list)
    except IOError as _e:
        tools.LOGS.add_error(_e)
        return -1
    return device_number

if __name__ == "__main__":
    LOG_ROOT = r'D:\Python\log\20181102220753\txt'
    """
    DEVICE_NUMBER = import_devices(LOG_ROOT)
    print('%d devices were added or updated' % (DEVICE_NUMBER,))
    print(LOGS.infos)
    for _error_log in LOGS.error_logs:
        print(_error_log)
    """

    print(export_devices_to_csv('result.csv'))
    print(tools.LOGS.errors)
