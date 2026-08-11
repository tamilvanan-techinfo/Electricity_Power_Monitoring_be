from django.contrib import admin
from .models import Cycle, Grouping, Participent, ParticipentCycle,ActiveParticipent,AppTheme
from screen_controller.models import *

@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('cycle_no', 'controller_no')


@admin.register(Participent)
class ParticipentAdmin(admin.ModelAdmin):
    list_display = ('name', 'dob', 'registered_on')


@admin.register(ParticipentCycle)
class ParticipentCycleAdmin(admin.ModelAdmin):
    list_display = ('participent', 'cycle', 'voltage', 'amperage')

@admin.register(Grouping)
class GroupingAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_grouping')

admin.site.register(Screen)
admin.site.register(ActiveParticipent)
admin.site.register(AppTheme)