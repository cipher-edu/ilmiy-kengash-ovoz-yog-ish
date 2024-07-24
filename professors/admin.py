from django.contrib import admin
from .models import *       


@admin.register(IlmiyUnvon)
class IlmiyUnvonAdmin(admin.ModelAdmin):
    list_display = ('name', 'unvon', 'unvon_shifr', 'kaf')
    search_fields = ('name', 'unvon', 'unvon_shifr', 'kaf')

@admin.register(Tanlov)
class TanlovAdmin(admin.ModelAdmin):
    list_display = ('name', 'kaf', 'scientific_title')
    search_fields = ('name', 'kaf', 'scientific_title')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('tanlov',  'ovoz')
    search_fields = ('tanlov__name',  'ovoz')

@admin.register(Vote2)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('ilmiy',  'ovoz')
    search_fields = ('ilmiy__name',  'ovoz')