from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta


# Modello Utente personalizzato
class Utente(AbstractUser):
    TIPO_UTENTE_SCELTE = (
        ('PRES_REGIONE', 'Presidente di Regione'),
        ('PRES_SQUADRA', 'Presidente di Squadra'),
        ('ALLENATORE', 'Allenatore'),
        ('ATLETA', 'Atleta'),
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='utenti_custom',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='utenti_custom',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    tipo = models.CharField(max_length=20, choices=TIPO_UTENTE_SCELTE)
    email = models.EmailField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Utente'
        verbose_name_plural = 'Utenti'


# Entità indipendenti
class Regione(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Squadra(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Specialita(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


# Modelli per la specializzazione (uno-a-uno con Utente)
class PresidenteRegione(models.Model):
    utente = models.OneToOneField(Utente, on_delete=models.CASCADE, primary_key=True)
    regione = models.OneToOneField(Regione, on_delete=models.CASCADE)
    def __str__(self):
        return f"Presidente Regione: {self.utente.username}"


class Atleta(models.Model):
    utente = models.OneToOneField('Utente', on_delete=models.CASCADE)
    squadra = models.ForeignKey(
        'Squadra',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atleti' # Aggiunto related_name per un accesso più facile
    )
    STATO_SCELTE = [
        ('SANO', 'Sano'),
        ('INFORTUNATO', 'Infortunato'),
    ]
    stato = models.CharField(max_length=15, choices=STATO_SCELTE, default='SANO')

    def __str__(self):
        return f"Atleta: {self.utente.username}"


class Allenatore(models.Model):
    utente = models.OneToOneField('Utente', on_delete=models.CASCADE)
    squadra = models.ForeignKey(
        'Squadra',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='allenatori' # Aggiunto related_name
    )

    def __str__(self):
        return f"Allenatore: {self.utente.username}"


class PresidenteSquadra(models.Model):
    utente = models.OneToOneField('Utente', on_delete=models.CASCADE)
    squadra = models.OneToOneField(
        'Squadra',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='presidente' # Aggiunto related_name
    )

    def __str__(self):
        return f"Presidente Squadra: {self.utente.username}"


# Modello Gara
class Gara(models.Model):
    presidente_regione = models.ForeignKey(PresidenteRegione, on_delete=models.CASCADE)
    luogo = models.CharField(max_length=200)
    data_inizio = models.DateField()
    data_fine = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Set data_fine to one day after data_inizio if not provided
        if not self.data_fine:
            self.data_fine = self.data_inizio + timedelta(days=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Gara a {self.luogo} ({self.data_inizio})"


# Tabelle di associazione per le relazioni molti-a-molti
class GaraSpecialita(models.Model):
    sesso_scelte = (
        ('M', 'Maschile'),
        ('F', 'Femminile'),
    )

    id_gara = models.ForeignKey(Gara, on_delete=models.CASCADE)
    id_specialita = models.ForeignKey(Specialita, on_delete=models.CASCADE)
    sesso = models.CharField(max_length=1, choices=sesso_scelte)

    class Meta:
        unique_together = ('id_gara', 'id_specialita', 'sesso')
        verbose_name = 'Gara Specialità'
        verbose_name_plural = 'Gare Specialità'

    def __str__(self):
        return f"Gara {self.id_gara} - Specialità {self.id_specialita} ({self.sesso})"


class Partecipazione(models.Model):
    STATO_ISCRIZIONE_SCELTE = (
        ('ISCRITTO', 'Iscritto'),
        ('COMPLETATO', 'Completato'),
        ('SQUALIFICATO', 'Squalificato'),
    )

    id_atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE)
    id_gara = models.ForeignKey(Gara, on_delete=models.CASCADE)
    id_specialita = models.ForeignKey(Specialita, on_delete=models.CASCADE)
    risultato = models.CharField(max_length=100, null=True, blank=True)
    stato_iscrizione = models.CharField(max_length=20, choices=STATO_ISCRIZIONE_SCELTE, default='ISCRITTO')

    class Meta:
        unique_together = ('id_atleta', 'id_gara', 'id_specialita')
        verbose_name = 'Partecipazione'
        verbose_name_plural = 'Partecipazioni'

    def __str__(self):
        return f"{self.id_atleta} in {self.id_specialita} per {self.id_gara}"