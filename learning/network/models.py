from django.db import models

# Cuijunshi Note 2018-10-29 define 2 models for device and interface
class Device(models.Model):
    hostname = models.CharField(max_length=64)
    Mgt_IP = models.GenericIPAddressField(null=True)
    description = models.CharField(max_length=200,null=True)
    device_type = models.CharField(max_length=64,null=True)
    version = models.CharField(max_length=10,null=True)
    running_configure = models.TextField(null=True)

class Interface(models.Model):
    iName = models.CharField(max_length=64)
    iType = models.IntegerField(null=True)
    iIP = models.GenericIPAddressField(null=True)
    description = models.CharField(max_length=200,null=True)
    iVlan = models.CharField(max_length=64,null=True)
    iDevice = models.ForeignKey(Device,on_delete=models.CASCADE,default ='')   #Cuijunshi Note 2018-10-29 test a function of a foreignKey
    iUsed = models.BooleanField(null=True)


# Cuijunshi Note 2018-10-30 test a function for model forms begin
class Person(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name

class Label(models.Model):
    name = models.CharField(max_length=64)
    frequncy = models.IntegerField()
    person = models.ForeignKey(Person,on_delete=models.CASCADE,default ='')

class Activity(models.Model):
    description = models.CharField(max_length=255,null=True)
    person = models.ForeignKey(Person,on_delete=models.CASCADE,default ='')
    label = models.ForeignKey(Label,on_delete=models.CASCADE,default ='')

# Cuijunshi Note 2018-10-30 test a function for model forms end

