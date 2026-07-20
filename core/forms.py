from django import forms
from .models import Cycle, Participent, ParticipentCycle


class CycleForm(forms.ModelForm):
    class Meta:
        model = Cycle
        fields = ['cycle_no', 'controller_no']


class ParticipentForm(forms.ModelForm):
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Participent
        fields = ['name', 'profile', 'dob']


class AllocateForm(forms.ModelForm):
    class Meta:
        model = ParticipentCycle
        fields = ['participent', 'cycle', 'power', 'voltage', 'amperage']
