### Installazione

1.  **Clona il repository:** https://github.com/edotammaro/webapp-database-exam

2.  **Installa le dipendenze presenti nel file requirements.txt:**
   
3.  **Applica le migrazioni del database**

### Utilizzo

Questa web app nasce per il mondo dell’atletica leggera, con l’obiettivo gestire: 
le gare, i componenti delle squadre e le iscrizioni in base allo stato degli atleti. 
Ci sono diversi ruoli nella piattaforma. Ogni utente deve prima registrarsi con le proprie credenziali e il proprio ruolo. 

**Il presidente della regione**: ne esiste uno e solo uno per ogni regione. 
Ogni presidente della regione può creare delle gare: stabilisce luogo e giorno, le specialità della competizione e il sesso. 
Può eventualmente eliminare delle gare dal calenadrio dall’apposito tasto.
Per ogni gara, il presidente della regione può vedere gli iscritti cliccando sull’apposito tasto. 
Credenziali per testare: 
- Username: PresidenteSquadra1, PresidenteSquadra2, PresidenteSquadra3, residenteSquadra4. 
- Password: admin123@@

**Il presidente della squadra**: ne esite uno e solo uno per ogni squadra. 
Gestisce i componenti della squadra: può aggiungere atleti e allenatori registrati alla piattaforma che non appartengono ancora ad una squadra.
Nella sua dashboard ha accesso al calendario delle prossime gare e quelle già svolte. 
Credenziali per testare: 
- Username: PresidenteCampania, PresidenteLazio, PresidenteLiguria, PresidenteEmiliaromagna, PresidenteFriuli, PresidenteCalabria. 
- Password: admin123@@