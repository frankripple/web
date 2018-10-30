from django.contrib import admin
from .models import Person

# Register your models here.
class PersonAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')

admin.site.register(Person,PersonAdmin)
