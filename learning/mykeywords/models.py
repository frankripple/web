# -*- coding: utf-8 -*-  
from django.db import models

# Create your models here.

class MyKeyWords(models.Model):
    keyword = models.CharField(max_length=200)
    frequency = models.IntegerField()
    description = models.CharField(max_length=2000)
    remarks = models.TextField()