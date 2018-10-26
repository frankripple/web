from django.shortcuts import render
from django.views import generic

import os,re
from . import models
# Create your views here.


class IndexView(generic.ListView):
    template_name = 'network/index.html'
    context_object_name = 'interface_list'

    def get_queryset(self):
        return models.Interface.objects.all()


def findaddfilesbyCondition(rootdir,Condition):
    '''
    rootdir is the root path for the file search.
    Condition is a function for match the file. And Condtion must accept a parameter file_path and return True or False
    return value is the list of all the fullname of files.
    '''
    result = list()
    for parent, dirnames, filenames in os.walk(rootdir,followlinks=True):
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            if Condition(file_path):
                result.append(file_path)
    return result

def findrun(filename):
    if re.search(r'show run.txt',filename):
        return True
    elif re.search(r'show running-config.txt',filename):
        return True
    else:
        return False

r = findaddfilesbyCondition('D:\\Python\\Tools\\log',findrun)

def insert_all(request):
    for p in r:
        f = open(p,'r')
        lines  = f.readlines()
        f.close()
        hostname = ''
        interface = None
        for l in lines:
            if hostname == '':
                t = re.search('hostname (\S+)',l)
                if t:
                    device = models.Device(hostname = t.groups()[0])
                    device.save()


            t = re.search('^interface (\S+)',l)
            if t:
                if interface is not None:
                    interface.save()
                    interface = models.Interface()
                else:
                    interface = models.Interface()
                interface.iName = t.groups()[0]
                interface.iDevice = device

            if interface is not None:
                t = re.search('^\s+description (.*)\n',l)
                if t:
                    interface.description = t.groups()[0]
                
                t = re.search('ip address (\d+\.\d+\.\d+\.\d+)',l)
                if t:
                    interface.iIP = t.groups()[0]
                    interface.iType = 1
                
                t = re.search('switchport trunk allowed vlan (.*)',l)
                if t:
                    interface.iVlan = t.groups()[0]
                    interface.iType = 2

                t = re.search('switchport access vlan (\d+)',l)
                if t:
                    interface.iVlan = t.groups()[0]
                    interface.iType = 2

        if interface is not None:
            interface.save()

    context ={}
    context['header'] = '第一个模版！'
    return render(request,'index.html',context)



