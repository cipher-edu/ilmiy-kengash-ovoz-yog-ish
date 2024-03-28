from django.contrib import admin
from .models import *       


# Register your models here.
admin.site.register(UserCreate)
class UnvonAdmin(admin.ModelAdmin):
    list_display = ('name','unvon', 'unvon_shifr', 'kaf',)
    list_filter = ('name','unvon', 'unvon_shifr', 'kaf',)
    list_per_page = 15
admin.site.register(IlmiyUnvon,UnvonAdmin)

class VoteAdmin(admin.ModelAdmin):
    list_display = ('unvon','user', 'scientific_title')
    list_filter = ('unvon','user', 'scientific_title')
    list_per_page = 25
admin.site.register(Vote,VoteAdmin)