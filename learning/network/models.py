from django.db import models

# Cuijunshi Note 2018-10-29 define 2 models for device and interface
class Device(models.Model):
    hostname = models.CharField(max_length=64)
    Mgt_IP = models.GenericIPAddressField(null=True)
    description = models.CharField(max_length=200,null=True)

class Interface(models.Model):
    iName = models.CharField(max_length=64)
    iType = models.IntegerField(null=True)
    iIP = models.GenericIPAddressField(null=True)
    description = models.CharField(max_length=200,null=True)
    iVlan = models.CharField(max_length=64,null=True)
    iDevice = models.ForeignKey(Device,on_delete=models.CASCADE,default ='')   #Cuijunshi Note 2018-10-29 test a function of a foreignKey
    iUsed = models.BooleanField(null=True)

