from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.contrib import messages
from .forms import RegistrazioneForm, LoginForm, AddAtletaForm, AddAllenatoreForm, GaraForm, IscrizioneGaraForm, \
    StatoAtletaForm
from .models import Utente, Atleta, Allenatore, PresidenteSquadra, PresidenteRegione, Squadra, Gara, GaraSpecialita, \
    Specialita, Partecipazione
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
            user = form.save(commit=False)
            user.nome = form.cleaned_data['nome']
            user.cognome = form.cleaned_data['cognome']
            user.data_nascita = form.cleaned_data['data_nascita']
            user.save()
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
        LOCKOUT_TIME = 60  # Secondi

        if username in FALLISMENTI_LOGIN and FALLISMENTI_LOGIN[username]['count'] >= MAX_FALLIMENTI:
            if time.time() - FALLISMENTI_LOGIN[username]['time'] < LOCKOUT_TIME:
                remaining_time = int(LOCKOUT_TIME - (time.time() - FALLISMENTI_LOGIN[username]['time']))
                messages.error(request, f"Troppi tentativi di accesso falliti. Riprova tra {remaining_time} secondi.")
                return render(request, 'DBProject/login.html', {'form': form})
            else:
                FALLISMENTI_LOGIN.pop(username)

        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                if username in FALLISMENTI_LOGIN:
                    FALLISMENTI_LOGIN.pop(username)
                return redirect('dashboard')
            else:
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
            form_stato = StatoAtletaForm(instance=atleta_obj)

            # Funzionalità 1: Calendario Gare completo con stato di iscrizione
            gare_specialita = GaraSpecialita.objects.all().order_by('id_gara__data_inizio')
            partecipazioni_atleta = Partecipazione.objects.filter(id_atleta=atleta_obj).values_list('id_gara',
                                                                                                    'id_specialita')
            gare_iscritte_ids = {f"{p[0]}-{p[1]}" for p in partecipazioni_atleta}

            # Funzionalità 2, 3 e 4: Visualizzazione delle iscrizioni attuali e dei risultati
            # Recuperiamo tutte le partecipazioni dell'atleta, pre-caricando i dati di Gara e Specialita
            iscrizioni_atleta = Partecipazione.objects.filter(id_atleta=atleta_obj).select_related(
                'id_gara', 'id_specialita'
            ).order_by('-id_gara__data_inizio')

            context = {
                'atleta': atleta_obj,
                'tipo_utente': 'ATLETA',
                'form_stato': form_stato,
                'gare_specialita': gare_specialita,
                'gare_iscritte_ids': gare_iscritte_ids,
                'iscrizioni_atleta': iscrizioni_atleta,  # Aggiunto il nuovo contesto
            }
            return render(request, 'DBProject/dashboard_atleta.html', context)
        except Atleta.DoesNotExist:
            messages.info(request,
                          "Sei registrato come atleta ma non sei ancora stato assegnato a una squadra. Attendi che il presidente di una squadra ti aggiunga.")
            return render(request, 'DBProject/dashboard.html', {'tipo_utente': 'ATLETA'})
    elif is_allenatore(request.user):
        return redirect('dashboard_allenatore')
    elif is_pres_squadra(request.user):
        return redirect('dashboard_pres_squadra')
    elif is_pres_regione(request.user):
        return redirect('dashboard_pres_regione')
    return render(request, 'DBProject/dashboard.html')


@login_required(login_url='/login/')
@user_passes_test(is_pres_squadra)
def dashboard_pres_squadra(request):
    presidente = get_object_or_404(PresidenteSquadra, utente=request.user)
    squadra = presidente.squadra
    allenatori = squadra.allenatori.all()
    atleti = squadra.atleti.all()
    gare = Gara.objects.all().order_by('data_inizio')

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
        'gare': gare,
    }
    return render(request, 'DBProject/dashboard_pres_squadra.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_allenatore)
def dashboard_allenatore(request):
    allenatore = get_object_or_404(Allenatore, utente=request.user)
    squadra = allenatore.squadra
    atleti_squadra = Atleta.objects.filter(squadra=squadra)

    gare_specialita = GaraSpecialita.objects.all().order_by('id_gara__data_inizio')

    forms_iscrizione = {}
    iscritti_per_gara = {}

    for gs in gare_specialita:
        forms_iscrizione[gs.pk] = IscrizioneGaraForm(gara_specialita=gs, allenatore=allenatore)

        iscritti_per_gara[gs.pk] = Partecipazione.objects.filter(
            id_gara=gs.id_gara,
            id_specialita=gs.id_specialita
        ).select_related('id_atleta__utente').order_by('id_atleta__utente__username')

    context = {
        'allenatore': allenatore,
        'squadra': squadra,
        'atleti_squadra': atleti_squadra,
        'tipo_utente': 'ALLENATORE',
        'gare_specialita': gare_specialita,
        'forms_iscrizione': forms_iscrizione,
        'iscritti_per_gara': iscritti_per_gara,
    }
    return render(request, 'DBProject/dashboard_allenatore.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_pres_squadra)
def rimuovi_membro(request, membro_id, tipo_membro):
    squadra_utente = request.user.presidentesquadra.squadra

    if tipo_membro == 'atleta':
        membro = get_object_or_404(Atleta, pk=membro_id, squadra=squadra_utente)
        membro.delete()
        messages.success(request, f"L'atleta '{membro.utente.username}' è stato rimosso dalla squadra.")
    elif tipo_membro == 'allenatore':
        membro = get_object_or_404(Allenatore, pk=membro_id, squadra=squadra_utente)
        membro.delete()
        messages.success(request, f"L'allenatore '{membro.utente.username}' è stato rimosso dalla squadra.")
    else:
        messages.error(request, "Tipo di membro non valido.")

    return redirect('dashboard_pres_squadra')


@login_required(login_url='/login/')
@user_passes_test(is_pres_regione)
def crea_gara_view(request):
    if request.method == 'POST':
        form = GaraForm(request.POST)
        if form.is_valid():
            gara = form.save(commit=False)
            presidente_regione = get_object_or_404(PresidenteRegione, utente=request.user)
            gara.presidente_regione = presidente_regione
            gara.save()

            specialita_selezionate = form.cleaned_data['specialita']
            sesso_selezionato = form.cleaned_data['sesso']

            for specialita in specialita_selezionate:
                GaraSpecialita.objects.create(
                    id_gara=gara,
                    id_specialita=specialita,
                    sesso=sesso_selezionato
                )

            messages.success(request, f"Gara '{gara.luogo}' creata con successo!")
            return redirect('dashboard')
    else:
        form = GaraForm()

    context = {
        'form': form,
        'tipo_utente': 'PRES_REGIONE',
    }
    return render(request, 'DBProject/crea_gara.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_pres_regione)
def rimuovi_gara_view(request, gara_id):
    gara = get_object_or_404(Gara, pk=gara_id)
    if gara.presidente_regione.utente != request.user:
        messages.error(request, "Non hai il permesso di rimuovere questa gara.")
        return redirect('dashboard')

    if request.method == 'POST':
        gara.delete()
        messages.success(request, f"La gara a '{gara.luogo}' è stata rimossa con successo.")

    return redirect('dashboard')


@login_required(login_url='/login/')
@user_passes_test(is_allenatore)
def iscrivi_atleti_gara(request, gara_specialita_id):
    if request.method == 'POST':
        allenatore = get_object_or_404(Allenatore, utente=request.user)
        gara_specialita = get_object_or_404(GaraSpecialita, pk=gara_specialita_id)

        form = IscrizioneGaraForm(request.POST, gara_specialita=gara_specialita, allenatore=allenatore)

        if form.is_valid():
            atleti_selezionati = form.cleaned_data['atleti_selezionati']

            iscrizioni_create = 0
            for atleta in atleti_selezionati:
                try:
                    Partecipazione.objects.create(
                        id_atleta=atleta,
                        id_gara=gara_specialita.id_gara,
                        id_specialita=gara_specialita.id_specialita,
                        stato_iscrizione='ISCRITTO'
                    )
                    iscrizioni_create += 1
                except IntegrityError:
                    messages.warning(request, f"L'atleta '{atleta.utente.username}' era già iscritto alla gara.")

            if iscrizioni_create > 0:
                messages.success(request,
                                 f"Iscrizione di {iscrizioni_create} atleti alla gara completata con successo.")
        else:
            messages.error(request, "Errore durante l'iscrizione. Controlla i dati del form.")

    return redirect('dashboard_allenatore')


@login_required(login_url='/login/')
@user_passes_test(is_allenatore)
def rimuovi_iscrizione(request, partecipazione_id):
    iscrizione = get_object_or_404(Partecipazione, pk=partecipazione_id)

    if iscrizione.id_atleta.squadra.allenatori.filter(utente=request.user).exists():
        atleta_nome = iscrizione.id_atleta.utente.username
        iscrizione.delete()
        messages.success(request, f"L'atleta '{atleta_nome}' è stato rimosso dalla gara con successo.")
    else:
        messages.error(request, "Non hai i permessi per rimuovere questa iscrizione.")

    return redirect('dashboard_allenatore')


@login_required(login_url='/login/')
@user_passes_test(is_atleta)
def aggiorna_stato_atleta(request):
    if request.method == 'POST':
        atleta = get_object_or_404(Atleta, utente=request.user)
        form = StatoAtletaForm(request.POST, instance=atleta)
        if form.is_valid():
            nuovo_stato = form.cleaned_data['stato']
            if nuovo_stato == 'INFORTUNATO' and atleta.stato != 'INFORTUNATO':
                partecipazioni_rimosse = Partecipazione.objects.filter(id_atleta=atleta).delete()
                if partecipazioni_rimosse[0] > 0:
                    messages.warning(request,
                                     f"Sei stato dichiarato infortunato. Sono state rimosse {partecipazioni_rimosse[0]} iscrizioni a gare.")

            form.save()
            messages.success(request, f"Il tuo stato è stato aggiornato a '{atleta.get_stato_display()}'.")
        else:
            messages.error(request, "Errore durante l'aggiornamento del tuo stato.")

    return redirect('dashboard')


@login_required(login_url='/login/')
@user_passes_test(is_pres_regione)
def dashboard_pres_regione(request):
    presidente = get_object_or_404(PresidenteRegione, utente=request.user)
    gare_create = Gara.objects.filter(presidente_regione=presidente).order_by('data_inizio')
    context = {
        'tipo_utente': 'PRES_REGIONE',
        'gare': gare_create
    }
    return render(request, 'DBProject/dashboard_pres_regione.html', context)