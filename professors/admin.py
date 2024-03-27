from django.contrib import admin
from .models import *       


# Register your models here.
admin.site.register(UserCreate)
class UnvonAdmin(admin.ModelAdmin):
    list_display = ('id',)
admin.site.register(IlmiyUnvon,UnvonAdmin)

class VoteAdmin(admin.ModelAdmin):
    list_display = ('id',)
admin.site.register(Vote,VoteAdmin)