from django.db import models

# Create your models here.
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
    iDevice = models.ForeignKey(Device,on_delete=models.CASCADE,default ='')
    iUsed = models.BooleanField(null=True)

