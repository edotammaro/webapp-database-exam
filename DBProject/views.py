from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # Importa il modulo messages
from .forms import RegistrazioneForm, LoginForm # Importa anche LoginForm
from .models import Atleta, Allenatore, PresidenteSquadra, PresidenteRegione

def home_view(request):
    return render(request, 'DBProject/home.html')

def register_view(request):
    if request.method == "POST":
        form = RegistrazioneForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistrazioneForm()
    return render(request, 'DBProject/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Credenziali non valide. Riprova.")
    else:
        form = LoginForm()
    return render(request, 'DBProject/login.html', {'form': form})


@login_required
def dashboard_view(request):
    ruolo_utente = request.user.tipo
    context = {'ruolo': ruolo_utente}
    return render(request, 'DBProject/dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')