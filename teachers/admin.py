from django.contrib import admin
from .models import *
# Register your models here.
class Teacheradmin(admin.ModelAdmin):
    list_display = ('name')
admin.site.register(Teacher)