import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# Lista delle squadre della Serie A 2025-2026
# Questa lista è basata sulle promozioni e retrocessioni per la prossima stagione.
TEAMS = [
    "Atalanta", "Bologna", "Cagliari", "Como", "Cremonese", "Fiorentina", "Genoa",
    "Inter", "Juventus", "Lazio", "Lecce", "Milan", "Napoli", "Parma", "Pisa",
    "Roma", "Sassuolo", "Torino", "Udinese", "Verona" # "Verona" si riferisce a Hellas Verona per gli URL
]

def scrape_fantacalcio_formations(team_name_full):
    """
    Scrapes probable formations for a single team from Fantacalcio.it.
    Returns a dictionary with team, module, players, and source.
    NOTE: Fantacalcio.it's 'probable formations' pages typically only provide
    player names and not detailed info like specific role, age, nationality.
    """
    try:
        # Prepara il nome della squadra per l'URL di Fantacalcio.it
        # Esempio: "Hellas Verona" diventa "verona" nell'URL
        url_team_segment = team_name_full.lower().replace(' ', '-').replace('hellas-', '')
        url = f"https://www.fantacalcio.it/giocatori/probabili-formazioni/serie-a/{url_team_segment}"
        print(f"Tentativo di scraping per: {team_name_full} da URL: {url} (Fantacalcio.it)")

        r = requests.get(url)
        r.raise_for_status() # Genera un'eccezione per errori HTTP (es. 404, 500)
        soup = BeautifulSoup(r.text, "html.parser")

        # Estrae il modulo della formazione
        mod_element = soup.select_one(".formazioneHeader .modulo")
        modulo = mod_element.text.strip() if mod_element else "Modulo non disponibile"

        # Estrae i giocatori titolari
        players_elements = soup.select(".formazione__lista li.titolare")
        players = [p.text.strip() for p in players_elements]

        print(f"  Debug: Modulo trovato per {team_name_full}: '{modulo}'")
        print(f"  Debug: Giocatori trovati per {team_name_full} ({len(players)}): {players}")

        return {"team": team_name_full, "modulo": modulo, "players": players, "source": "Fantacalcio.it"}
    except requests.exceptions.RequestException as e:
        print(f"Errore HTTP/di connessione per {team_name_full} (Fantacalcio.it): {e}")
        return {"team": team_name_full, "modulo": "Errore", "players": ["Dati non disponibili"], "source": "Fantacalcio.it (Errore)"}
    except Exception as e:
        print(f"Errore inatteso per {team_name_full} (Fantacalcio.it): {e}")
        return {"team": team_name_full, "modulo": "Errore", "players": ["Dati non disponibili"], "source": "Fantacalcio.it (Errore)"}

def scrape_tmw_serie_a_news():
    """
    Scrapes recent Serie A news headlines from TuttoMercatoWeb.com.
    Returns a list of dictionaries with 'title' and 'link'.
    """
    news_items = []
    url = "https://www.tuttomercatoweb.com/serie-a"
    print(f"Tentativo di scraping notizie da TuttoMercatoWeb.com da URL: {url}")
    try:
        r = requests.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Seleziona gli elementi delle notizie dalla lista principale di TMW
        news_elements = soup.select('.tmw-list article .h-item a') # Aggiornato per catturare i link negli articoli
        
        # Prende solo i primi 7-10 titoli per evitare una lista troppo lunga
        for i, news_item in enumerate(news_elements):
            if i >= 10: # Limita a 10 notizie
                break
            title = news_item.get_text(strip=True)
            link = news_item['href']
            # Assicurati che il link sia assoluto
            if not link.startswith('http'):
                link = f"https://www.tuttomercatoweb.com{link}"
            
            if title and link and "video" not in link: # Filtra i link che potrebbero essere video
                news_items.append({"title": title, "link": link})
        
        print(f"Notizie raccolte da TuttoMercatoWeb.com: {len(news_items)} articoli.")
        return news_items

    except requests.exceptions.RequestException as e:
        print(f"Errore HTTP/di connessione durante lo scraping delle notizie da TMW: {e}")
        return []
    except Exception as e:
        print(f"Errore inatteso durante lo scraping delle notizie da TMW: {e}")
        return []

# --- Esecuzione dello Scraping ---
SCRAPED_FORMATIONS = []
print("Inizio scraping delle formazioni probabili...")
for team in TEAMS:
    formation_data = scrape_fantacalcio_formations(team)
    SCRAPED_FORMATIONS.append(formation_data)
print("Scraping formazioni completato.")

SCRAPED_NEWS = []
print("Inizio scraping delle ultime notizie dalla Serie A (TMW)...")
SCRAPED_NEWS = scrape_tmw_serie_a_news()
print("Scraping notizie completato.")


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
    <title>Probabili Formazioni Serie A 2025-2026</title>
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
            Probabili Formazioni Serie A 2025-2026
        </h1>
        <p class="text-center text-gray-600 text-sm mb-8">Ultimo aggiornamento: {current_datetime}</p>
        
        <!-- Sezione per le Formazioni delle Squadre -->
        <h2 class="text-3xl font-bold text-gray-800 mb-6 mt-10 text-center">
            Formazioni Probabili (Fonte: Fantacalcio.it)
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
"""

# Itera sui dati delle formazioni recuperati per generare la card HTML di ogni squadra
for d in SCRAPED_FORMATIONS:
    # IMPORTANTE: Sostituisci questo segnaposto con i percorsi reali dei tuoi loghi
    # Una volta che avrai la cartella 'logos' con i tuoi PNG delle squadre, usa:
    # Per esempio, per Juventus.png, il percorso sarebbe 'logos/juventus.png'
    logo_path = f"https://placehold.co/40x40/cbd5e1/4b5563?text={d['team'][0].upper()}" # Segnaposto con la prima lettera della squadra

    # Prepara il nome della squadra per il percorso del logo (gestendo casi come "Hellas Verona" -> "verona")
    team_for_logo_filename = d['team'].lower().replace(' ', '-').replace('hellas-', '')
    # Se hai i tuoi loghi, decommenta la riga seguente e commenta quella sopra
    # logo_path = f"logos/{team_for_logo_filename}.png"

    # Crea una card per ogni squadra con le classi Tailwind CSS per lo styling
    html += f"""
            <div class="team bg-white shadow-lg rounded-lg p-6 mb-4 transform transition-transform duration-300 hover:scale-105 hover:shadow-xl">
                <div class="flex items-center mb-4">
                    <img src="{logo_path}" alt="{d['team']} logo" class="w-10 h-10 rounded-full mr-4 border-2 border-gray-200 object-contain">
                    <h2 class="text-2xl font-semibold text-gray-700">{d['team']} — {d['modulo']}</h2>
                </div>
                <ul class="list-none space-y-2"> {/* Changed to list-none for custom styling */}
    """
    # Aggiunge i giocatori alla lista all'interno della card della squadra
    if d['players']:
        for p in d["players"]:
            # Visualizzazione migliorata per ogni giocatore (stile mini-card)
            html += f"""
                        <li class="flex items-center p-2 bg-gray-50 rounded-md shadow-sm border border-gray-200">
                            <img src="https://placehold.co/30x30/d1d5db/374151?text=⚽" alt="Player icon" class="w-8 h-8 rounded-full mr-3 border border-gray-300 object-contain">
                            <div>
                                <p class="font-semibold text-gray-800 text-base">{p}</p>
                                {/* Placeholder per Ruolo, Età, Nazionalità. Questi dati NON sono scrapati da Fantacalcio.it. */}
                                <p class="text-xs text-gray-500">Ruolo (es. Attaccante) | Età (N/D) | Nazionalità (N/D)</p>
                                {/* <a href="#" class="text-blue-500 hover:underline text-xs">Vedi profilo</a> {/* Placeholder link */}
                            </div>
                        </li>
            """
    else:
        html += """
                    <li class="text-red-500 p-2 bg-gray-50 rounded-md shadow-sm border border-gray-200">Nessun giocatore titolare trovato o errore nello scraping. Le formazioni saranno aggiornate con l'avvicinarsi della stagione e del calciomercato.</li>
        """
    html += """
                </ul>
            </div>
    """

html += """
        </div>

        <!-- Sezione per le Ultime Notizie (Fonte: TuttoMercatoWeb.com) -->
        <h2 class="text-3xl font-bold text-gray-800 mb-6 mt-10 text-center">
            Ultime Notizie Serie A (Fonte: TuttoMercatoWeb.com)
        </h2>
        <div class="bg-white shadow-lg rounded-lg p-6 mb-4">
            <ul class="list-none space-y-3">
    """

# Aggiunge le notizie recuperate da TuttoMercatoWeb.com
if SCRAPED_NEWS:
    for news in SCRAPED_NEWS:
        html += f"""
                <li class="flex items-start">
                    <svg class="w-5 h-5 text-blue-500 mr-2 flex-shrink-0 mt-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1.172a3.001 3.001 0 01-1.341-2.698zM12 16h.01" clip-rule="evenodd"></path>
                    </svg>
                    <a href="{news['link']}" target="_blank" rel="noopener noreferrer" class="text-blue-700 hover:underline text-lg font-medium">
                        {news['title']}
                    </a>
                </li>
        """
else:
    html += """
                <li class="text-red-500">Nessuna notizia trovata o errore nello scraping da TuttoMercatoWeb.com.</li>
    """

html += """
            </ul>
        </div>
    </div>
    <footer class="mt-8 text-center text-gray-500 text-sm">
        Dati forniti da Fantacalcio.it e TuttoMercatoWeb.com
    </footer>
</body>
</html>
"""

# Scrive l'HTML generato nel file index.html nella directory principale
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html generato con successo!")
