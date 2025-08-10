from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection, IntegrityError
from django.contrib import messages
from .forms import RegistrazioneForm, LoginForm, AddAtletaForm, AddAllenatoreForm
from .models import Utente, Atleta, Allenatore, PresidenteSquadra, PresidenteRegione, Squadra
import time

FALLISMENTI_LOGIN = {}


def is_atleta(user):
    return user.is_authenticated and user.tipo == 'ATLETA'


def is_allenatore(user):
    return user.is_authenticated and user.tipo == 'ALLENATORE'


def is_pres_squadra(user):
    return user.is_authenticated and user.tipo == 'PRES_SQUADRA'


def is_pres_regione(user):
    return user.is_authenticated and user.tipo == 'PRES_REGIONE'


def home_view(request):
    return render(request, 'DBProject/home.html')


def register_view(request):
    if request.method == "POST":
        form = RegistrazioneForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Utente '{user.username}' registrato con successo!")
            return redirect('login')
        else:
            messages.error(request, "Errore nella registrazione. Controlla i dati inseriti.")
    else:
        form = RegistrazioneForm()
    return render(request, 'DBProject/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        username = request.POST.get('username')
        MAX_FALLIMENTI = 5
        LOCKOUT_TIME = 60 # Secondi

        if username in FALLISMENTI_LOGIN and FALLISMENTI_LOGIN[username]['count'] >= MAX_FALLIMENTI:
            # Controlla se il tempo di blocco è scaduto
            if time.time() - FALLISMENTI_LOGIN[username]['time'] < LOCKOUT_TIME:
                remaining_time = int(LOCKOUT_TIME - (time.time() - FALLISMENTI_LOGIN[username]['time']))
                messages.error(request, f"Troppi tentativi di accesso falliti. Riprova tra {remaining_time} secondi.")
                return render(request, 'DBProject/login.html', {'form': form})
            else:
                # Resetta il contatore se il tempo di blocco è scaduto
                FALLISMENTI_LOGIN.pop(username)

        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                if username in FALLISMENTI_LOGIN:
                    FALLISMENTI_LOGIN.pop(username)
                return redirect('dashboard')
            else:
                # Incrementa il contatore dei fallimenti
                if username not in FALLISMENTI_LOGIN:
                    FALLISMENTI_LOGIN[username] = {'count': 1, 'time': time.time()}
                else:
                    FALLISMENTI_LOGIN[username]['count'] += 1
                    FALLISMENTI_LOGIN[username]['time'] = time.time()

                messages.error(request, "Credenziali non valide. Riprova.")
        else:
            messages.error(request, "Credenziali non valide. Riprova.")
    else:
        form = LoginForm()

    return render(request, 'DBProject/login.html', {'form': form})


@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='/login/')
def dashboard_view(request):
    if is_atleta(request.user):
        try:
            atleta_obj = Atleta.objects.get(utente=request.user)
            context = {
                'atleta': atleta_obj,
                'tipo_utente': 'ATLETA',
            }
            return render(request, 'DBProject/dashboard_atleta.html', context)
        except Atleta.DoesNotExist:
            messages.info(request, "Sei registrato come atleta ma non sei ancora stato assegnato a una squadra. Attendi che il presidente di una squadra ti aggiunga.")
            return render(request, 'DBProject/dashboard.html', {'tipo_utente': 'ATLETA'})
    elif is_allenatore(request.user):
        try:
            allenatore_obj = Allenatore.objects.get(utente=request.user)
            context = {
                'allenatore': allenatore_obj,
                'tipo_utente': 'ALLENATORE',
            }
            return render(request, 'DBProject/dashboard_allenatore.html', context)
        except Allenatore.DoesNotExist:
            messages.info(request, "Sei registrato come allenatore ma non sei ancora stato assegnato a una squadra. Attendi che il presidente di una squadra ti aggiunga.")
            return render(request, 'DBProject/dashboard.html', {'tipo_utente': 'ALLENATORE'})
    elif is_pres_squadra(request.user):
        return redirect('dashboard_pres_squadra')
    elif is_pres_regione(request.user):
        return render(request, 'DBProject/dashboard_pres_regione.html', {'tipo_utente': 'PRES_REGIONE'})
    return render(request, 'DBProject/dashboard.html')


@login_required(login_url='/login/')
@user_passes_test(is_pres_squadra)
def dashboard_pres_squadra(request):
    presidente = get_object_or_404(PresidenteSquadra, utente=request.user)
    squadra = presidente.squadra
    allenatori = squadra.allenatori.all()
    atleti = squadra.atleti.all()

    add_atleta_form = AddAtletaForm(initial={'squadra': squadra.pk})
    add_allenatore_form = AddAllenatoreForm(initial={'squadra': squadra.pk})

    if request.method == 'POST':
        if 'add_atleta' in request.POST:
            add_atleta_form = AddAtletaForm(request.POST)
            if add_atleta_form.is_valid():
                try:
                    atleta = add_atleta_form.save(commit=False)
                    atleta.squadra = squadra
                    atleta.save()
                    messages.success(request, f"Atleta '{atleta.utente.username}' aggiunto con successo.")
                except IntegrityError:
                    messages.error(request, "Questo utente è già un atleta e non può essere aggiunto nuovamente.")
                return redirect('dashboard_pres_squadra')

        if 'add_allenatore' in request.POST:
            add_allenatore_form = AddAllenatoreForm(request.POST)
            if add_allenatore_form.is_valid():
                try:
                    allenatore = add_allenatore_form.save(commit=False)
                    allenatore.squadra = squadra
                    allenatore.save()
                    messages.success(request, f"Allenatore '{allenatore.utente.username}' aggiunto con successo.")
                except IntegrityError:
                    messages.error(request, "Questo utente è già un allenatore e non può essere aggiunto nuovamente.")
                return redirect('dashboard_pres_squadra')

    context = {
        'presidente': presidente,
        'squadra': squadra,
        'allenatori': allenatori,
        'atleti': atleti,
        'add_atleta_form': add_atleta_form,
        'add_allenatore_form': add_allenatore_form,
        'tipo_utente': 'PRES_SQUADRA',
    }
    return render(request, 'DBProject/dashboard_pres_squadra.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_allenatore)
def dashboard_allenatore(request):
    allenatore = get_object_or_404(Allenatore, utente=request.user)
    squadra = allenatore.squadra
    atleti_squadra = Atleta.objects.filter(squadra=squadra)

    context = {
        'allenatore': allenatore,
        'squadra': squadra,
        'atleti_squadra': atleti_squadra,
        'tipo_utente': 'ALLENATORE',
    }
    return render(request, 'DBProject/dashboard_allenatore.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_pres_squadra)
def rimuovi_membro(request, membro_id, tipo_membro):
    squadra_utente = request.user.presidentesquadra.squadra

    if tipo_membro == 'atleta':
        membro = get_object_or_404(Atleta, id=membro_id, squadra=squadra_utente)
        membro.delete()
        messages.success(request, f"L'atleta '{membro.utente.username}' è stato rimosso dalla squadra.")
    elif tipo_membro == 'allenatore':
        membro = get_object_or_404(Allenatore, id=membro_id, squadra=squadra_utente)
        membro.delete()
        messages.success(request, f"L'allenatore '{membro.utente.username}' è stato rimosso dalla squadra.")
    else:
        messages.error(request, "Tipo di membro non valido.")

    return redirect('dashboard_pres_squadra')