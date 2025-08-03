from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Utente, Atleta, Allenatore, PresidenteSquadra, PresidenteRegione


class RegistrazioneForm(UserCreationForm):
    # La scelta del ruolo (tipo)
    tipo = forms.ChoiceField(
        choices=Utente.TIPO_UTENTE_SCELTE,
        label="Scegli il tuo ruolo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = Utente
        fields = UserCreationForm.Meta.fields + ('tipo', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = self.cleaned_data["tipo"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            if user.tipo == 'ATLETA':
                pass
            elif user.tipo == 'ALLENATORE':
                pass
            elif user.tipo == 'PRES_SQUADRA':
                pass
            elif user.tipo == 'PRES_REGIONE':
                pass
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))