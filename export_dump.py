import sqlite3

# Nome del file del tuo database Django
db_filename = "db.sqlite3"
dump_filename = "dump.sql"

# Connessione al database
conn = sqlite3.connect(db_filename)

# Creazione del dump
with open(dump_filename, "w", encoding="utf-8") as f:
    for line in conn.iterdump():
        f.write("%s\n" % line)

conn.close()
print(f"✅ Dump creato con successo in '{dump_filename}'")
