from django.contrib import admin
from .models import Person,Device

# Register your models here.
class PersonAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('hostname','version','device_type','Mgt_IP')

#admin.site.register(Person,PersonAdmin)

admin.site.register(Device,DeviceAdmin)