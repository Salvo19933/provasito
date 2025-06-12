import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# List of Serie A teams
TEAMS = [
    "Juventus", "Inter", "Milan", "Napoli", "Roma", "Lazio", "Atalanta",
    "Fiorentina", "Bologna", "Torino", "Verona", "Monza", "Udinese", "Empoli",
    "Salernitana", "Lecce", "Sassuolo", "Genoa", "Spezia", "Frosinone" # Nota: La lista delle squadre dovrebbe essere aggiornata se ci sono promozioni/retrocessioni in Serie A.
]

SCRAPED_DATA = [] # Lista per memorizzare i dati delle formazioni

print("Inizio scraping delle formazioni da Fantacalcio.it...")

# --- Fonte di Scraping Primaria: Fantacalcio.it ---
# Questo ciclo recupera le formazioni per ogni squadra dalla pagina dedicata su Fantacalcio.it
for team in TEAMS:
    try:
        # Costruisce l'URL per la pagina delle probabili formazioni della squadra su Fantacalcio.it
        # Sostituisce gli spazi con i trattini e converte in minuscolo per l'URL
        url_team_name = team.lower().replace(' ', '-')
        url = f"https://www.fantacalcio.it/giocatori/probabili-formazioni/serie-a/{url_team_name}"
        print(f"Tentativo di scraping per: {team} da URL: {url}")

        r = requests.get(url)
        r.raise_for_status() # Genera un'eccezione per errori HTTP (es. 404, 500)
        soup = BeautifulSoup(r.text, "html.parser")

        # Estrae il modulo della formazione (es. 4-3-3)
        mod_element = soup.select_one(".formazioneHeader .modulo")
        modulo = mod_element.text.strip() if mod_element else "Modulo non disponibile"

        # Estrae i giocatori titolari
        players_elements = soup.select(".formazione__lista li.titolare")
        players = [p.text.strip() for p in players_elements]

        SCRAPED_DATA.append({"team": team, "modulo": modulo, "players": players, "source": "Fantacalcio.it"})
        print(f"Dati per {team} raccolti con successo da Fantacalcio.it.")
    except requests.exceptions.RequestException as e:
        print(f"Errore HTTP/di connessione durante lo scraping per {team} da Fantacalcio.it: {e}")
        SCRAPED_DATA.append({"team": team, "modulo": "Errore", "players": ["Dati non disponibili"], "source": "Fantacalcio.it (Errore)"})
    except Exception as e:
        print(f"Si è verificato un errore inatteso durante lo scraping per {team} da Fantacalcio.it: {e}")
        SCRAPED_DATA.append({"team": team, "modulo": "Errore", "players": ["Dati non disponibili"], "source": "Fantacalcio.it (Errore)"})

print("Scraping da Fantacalcio.it completato.")


# --- Generazione HTML ---
print("Generazione HTML...")

# Ottiene la data e l'ora corrente per il timestamp di aggiornamento
current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M") # Formato: GG/MM/AAAA HH:MM

# Inizia il contenuto HTML con Tailwind CSS e il font Inter
html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Probabili Formazioni Serie A</title>
    <!-- CDN di Tailwind CSS per uno styling semplice -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts per il font Inter -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f5; /* Sfondo grigio chiaro per un look pulito */
        }}
    </style>
</head>
<body class="p-4 bg-gray-100 flex flex-col items-center min-h-screen">
    <div class="container mx-auto max-w-4xl">
        <h1 class="text-4xl font-bold text-center text-gray-800 mb-4 rounded-lg p-4 bg-white shadow-md">
            Probabili Formazioni Serie A
        </h1>
        <p class="text-center text-gray-600 text-sm mb-8">Ultimo aggiornamento: {current_datetime}</p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
"""

# Itera sui dati recuperati per generare la card HTML di ogni squadra
for d in SCRAPED_DATA:
    # IMPORTANTE: Sostituisci questo segnaposto con i percorsi reali dei tuoi loghi
    # Una volta che avrai la cartella 'logos' con i tuoi PNG delle squadre, usa:
    # logo_path = f"logos/{d['team'].lower().replace(' ', '-')}.png"
    # Per ora, usiamo un'immagine segnaposto da placehold.co
    logo_path = f"https://placehold.co/40x40/cbd5e1/4b5563?text={d['team'][0].upper()}" # Segnaposto con la prima lettera della squadra

    # Crea una card per ogni squadra con le classi Tailwind CSS per lo styling
    html += f"""
            <div class="team bg-white shadow-lg rounded-lg p-6 mb-4 transform transition-transform duration-300 hover:scale-105 hover:shadow-xl">
                <div class="flex items-center mb-4">
                    <img src="{logo_path}" alt="{d['team']} logo" class="w-10 h-10 rounded-full mr-4 border-2 border-gray-200 object-contain">
                    <h2 class="text-2xl font-semibold text-gray-700">{d['team']} — {d['modulo']}</h2>
                </div>
                <ul class="list-disc list-inside text-gray-600 space-y-2">
    """
    # Aggiunge i giocatori alla lista all'interno della card della squadra
    if d['players']:
        for p in d["players"]:
            html += f"""
                        <li class="flex items-center">
                            <svg class="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                            </svg>
                            {p}
                        </li>
            """
    else:
        html += """
                    <li class="text-red-500">Nessun giocatore titolare trovato o errore nello scraping.</li>
        """
    html += f"""
                </ul>
                <p class="text-xs text-gray-500 mt-4 text-right">Fonte: {d['source']}</p>
            </div>
    """

html += """
        </div>
    </div>
    <footer class="mt-8 text-center text-gray-500 text-sm">
        Dati forniti da Fantacalcio.it
    </footer>
</body>
</html>
"""

# Scrive l'HTML generato nel file index.html nella directory principale
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html generato con successo!")
