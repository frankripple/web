from django.contrib import admin
from .models import Person, Device, Interface

# Register your models here.
class PersonAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id', 'name')

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'version', 'device_type', 'Mgt_IP')

class InterfaceAdmin(admin.ModelAdmin):
    list_display = ('iDevice', 'iName', 'remote_device_name', 'remote_interface_name', 'description','iIP','iVlan')
    list_per_page = 40


#admin.site.register(Person,PersonAdmin)

admin.site.register(Device, DeviceAdmin)

admin.site.register(Interface, InterfaceAdmin)
