from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Utente, Atleta, Allenatore, PresidenteSquadra, PresidenteRegione, Gara, Partecipazione, Squadra, \
    Regione, Specialita, GaraSpecialita


class RegistrazioneForm(UserCreationForm):
    tipo = forms.ChoiceField(
        choices=Utente.TIPO_UTENTE_SCELTE,
        label="Scegli il tuo ruolo",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_tipo'})
    )
    regione = forms.ModelChoiceField(
        queryset=Regione.objects.all(),
        required=False,
        label="Regione di appartenenza (solo per Presidente di Regione)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nome_squadra = forms.CharField(
        max_length=100,
        required=False,
        label="Nome della squadra (solo per Presidente di Squadra)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = Utente
        fields = UserCreationForm.Meta.fields + ('tipo', 'email', 'regione', 'nome_squadra',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = self.cleaned_data["tipo"]
        user.email = self.cleaned_data["email"]

        password_plain = self.cleaned_data.get("password")
        if password_plain:
            user.set_password(password_plain)

        if commit:
            user.save()

            if user.tipo == 'PRES_SQUADRA':
                nome_squadra = self.cleaned_data.get("nome_squadra")
                if nome_squadra:
                    squadra_obj, created = Squadra.objects.get_or_create(nome=nome_squadra)
                    PresidenteSquadra.objects.create(utente=user, squadra=squadra_obj)
                else:
                    raise forms.ValidationError("Il Presidente di Squadra deve creare una squadra.")
            elif user.tipo == 'PRES_REGIONE':
                regione = self.cleaned_data.get("regione")
                if regione:
                    PresidenteRegione.objects.create(utente=user, regione=regione)
                else:
                    raise forms.ValidationError("Il Presidente di Regione deve avere una regione assegnata.")

        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class StatoAtletaForm(forms.ModelForm):
    class Meta:
        model = Atleta
        fields = ['stato']


class AddAtletaForm(forms.ModelForm):
    utente = forms.ModelChoiceField(
        queryset=Utente.objects.filter(tipo='ATLETA', atleta__isnull=True),
        label="Seleziona un atleta",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Atleta
        fields = ['utente', 'squadra']
        widgets = {
            'squadra': forms.HiddenInput(),
        }


class AddAllenatoreForm(forms.ModelForm):
    utente = forms.ModelChoiceField(
        queryset=Utente.objects.filter(tipo='ALLENATORE', allenatore__isnull=True),
        label="Seleziona un allenatore",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Allenatore
        fields = ['utente', 'squadra']
        widgets = {
            'utente': forms.Select(attrs={'class': 'form-control'}),
            'squadra': forms.HiddenInput(),
        }

class GaraForm(forms.ModelForm):
    specialita = forms.ModelMultipleChoiceField(
        queryset=Specialita.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Seleziona le specialità",
    )
    sesso = forms.ChoiceField(
        choices=GaraSpecialita.sesso_scelte,
        widget=forms.RadioSelect,
        label="Seleziona il sesso"
    )

    class Meta:
        model = Gara
        fields = ['luogo', 'data_inizio']
        widgets = {
            'luogo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_inizio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }