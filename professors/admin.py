# professors/admin.py

from django.contrib import admin
from .models import *

# --- Ma'lumotnomalar va Profil ---
@admin.register(Kafedra)
class KafedraAdmin(admin.ModelAdmin):
    list_display = ('name',); search_fields = ('name',)

@admin.register(Lavozim)
class LavozimAdmin(admin.ModelAdmin):
    list_display = ('name',); search_fields = ('name',)

@admin.register(Kengash)
class KengashAdmin(admin.ModelAdmin):
    list_display = ('name',); search_fields = ('name',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'kafedra', 'position')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)

# --- Saylov Tizimi ---
class TanlovInline(admin.TabularInline):
    """Nomzodlarni Saylov ichida boshqarish uchun."""
    model = Tanlov
    extra = 1
    verbose_name = "Nomzod"
    verbose_name_plural = "Nomzodlar"

@admin.register(Saylov)
class SaylovAdmin(admin.ModelAdmin):
    list_display = ('title', 'lavozim')
    list_filter = ('lavozim',)
    search_fields = ('title', 'lavozim__name')
    inlines = [TanlovInline]

@admin.register(SaylovVote)
class SaylovVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'saylov', 'chosen_candidate')
    search_fields = ('user__username', 'saylov__title', 'chosen_candidate__candidate_name')
    list_filter = ('saylov',)
    autocomplete_fields = ['user', 'saylov', 'chosen_candidate']

# --- Standart Ovoz Berish ---
@admin.register(IlmiyUnvon)
class IlmiyUnvonAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'title')
    search_fields = ('candidate_name', 'title')

@admin.register(BoshqaMasala)
class BoshqaMasalaAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_object', 'ovoz')
    search_fields = ('user__username',)
    list_filter = ('content_type', 'ovoz')
    autocomplete_fields = ['user']

# --- Markaziy Byulleten ---
@admin.register(Byulleten)
class ByulletenAdmin(admin.ModelAdmin):
    list_display = ('title', 'kengash', 'is_active', 'created_at')
    list_filter = ('is_active', 'kengash')
    search_fields = ('title', 'kengash__name')
    date_hierarchy = 'created_at'
    filter_horizontal = ('saylovlar', 'unvonlar', 'boshqa_masalalar')

@admin.register(Tanlov)
class TanlovAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'saylov')
    search_fields = ('candidate_name', 'saylov__title')
    list_filter = ('saylov',)