from django.contrib import admin
from .models import Cycle, Participent, ParticipentCycle


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
	list_display = ('cycle_no', 'controller_no')


@admin.register(Participent)
class ParticipentAdmin(admin.ModelAdmin):
	list_display = ('name', 'dob', 'registered_on')


@admin.register(ParticipentCycle)
class ParticipentCycleAdmin(admin.ModelAdmin):
	list_display = ('participent', 'cycle', 'voltage', 'amperage')
