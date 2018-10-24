# -*- coding: utf-8 -*-  
from django.shortcuts import render
def hello(request):
    #return HttpResponse('Hello world!')
    context ={}
    context['header'] = '第一个模版！'
    return render(request,'index.html',context)
