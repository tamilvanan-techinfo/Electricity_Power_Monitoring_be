from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .forms import CycleForm, ParticipentForm, AllocateForm
from .models import Cycle, Participent, ParticipentCycle


def home(request):
    return render(request, 'home.html', {'title': 'Electricity Monitoring'})


def login_view(request):
    return auth_views.LoginView.as_view(template_name='registration/login.html')(request)


@login_required
def dashboard(request):
    cycles = Cycle.objects.all()
    participants = Participent.objects.all()
    allocations = ParticipentCycle.objects.all()
    return render(request, 'dashboard.html', {
        'cycles': cycles,
        'participants': participants,
        'allocations': allocations,
    })


@login_required
def register_cycle(request):
    if request.method == 'POST':
        form = CycleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CycleForm()
    return render(request, 'cycle_form.html', {'form': form})


@login_required
def register_participent(request):
    if request.method == 'POST':
        form = ParticipentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ParticipentForm()
    return render(request, 'participent_form.html', {'form': form})


@login_required
def allocate_cycle(request):
    if request.method == 'POST':
        form = AllocateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AllocateForm()
    return render(request, 'allocate_form.html', {'form': form})


