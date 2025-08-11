from django.contrib.auth import get_user_model
from DBProject.models import Regione, PresidenteRegione, Squadra, PresidenteSquadra, Allenatore, Atleta

User = get_user_model()

# Dati di base
regioni_nomi = ["Campania", "Basilicata", "Puglia", "Calabria", "Sicilia"]

def run():
    for nome_regione in regioni_nomi:
        regione, _ = Regione.objects.get_or_create(nome=nome_regione)

        # Presidente Regione
        username_pr = f"pres_reg_{nome_regione.lower()}"
        user_pr, _ = User.objects.get_or_create(
            username=username_pr,
            defaults={
                "tipo": "PRES_REGIONE",
                "email": f"{username_pr}@example.com"
            }
        )
        PresidenteRegione.objects.get_or_create(utente=user_pr, regione=regione)

        # Creazione Squadre + Presidenti + Allenatori + Atleti
        for i in range(1, 6):
            squadra_nome = f"{nome_regione}_Squadra_{i}"
            squadra, _ = Squadra.objects.get_or_create(nome=squadra_nome)

            # Presidente Squadra
            username_ps = f"pres_squadra_{nome_regione.lower()}_{i}"
            user_ps, _ = User.objects.get_or_create(
                username=username_ps,
                defaults={
                    "tipo": "PRES_SQUADRA",
                    "email": f"{username_ps}@example.com"
                }
            )
            PresidenteSquadra.objects.get_or_create(utente=user_ps, squadra=squadra)

            # Allenatori (3)
            for j in range(1, 4):
                username_all = f"allenatore_{nome_regione.lower()}_{i}_{j}"
                user_all, _ = User.objects.get_or_create(
                    username=username_all,
                    defaults={
                        "tipo": "ALLENATORE",
                        "email": f"{username_all}@example.com"
                    }
                )
                Allenatore.objects.get_or_create(utente=user_all, squadra=squadra)

            # Atleti (5 maschi + 5 femmine)
            for sesso, count in [("M", 5), ("F", 5)]:
                for k in range(1, count + 1):
                    username_atl = f"atleta_{sesso}_{nome_regione.lower()}_{i}_{k}"
                    user_atl, _ = User.objects.get_or_create(
                        username=username_atl,
                        defaults={
                            "tipo": "ATLETA",
                            "email": f"{username_atl}@example.com"
                        }
                    )
                    Atleta.objects.get_or_create(
                        utente=user_atl,
                        squadra=squadra
                    )

    print("✅ Popolamento completato con successo!")

# Avvio script quando eseguito direttamente
if __name__ == "__main__":
    run()
