import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# Lista delle squadre della Serie A 2025-2026 (mantenuta per contesto generale, non per scraping formazioni individuali)
TEAMS = [
    "Atalanta", "Bologna", "Cagliari", "Como", "Cremonese", "Fiorentina", "Genoa",
    "Inter", "Juventus", "Lazio", "Lecce", "Milan", "Napoli", "Parma", "Pisa",
    "Roma", "Sassuolo", "Torino", "Udinese", "Verona"
]

def scrape_sky_sport_serie_a_news():
    """
    Scrapes recent Serie A news headlines from sport.sky.it/calcio/serie-a.
    Returns a list of dictionaries with 'title' and 'link'.
    """
    news_items = []
    url = "https://sport.sky.it/calcio/serie-a"
    print(f"Tentativo di scraping notizie Serie A da Sky Sport da URL: {url}")
    try:
        r = requests.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Selettori per le notizie principali su Sky Sport.
        # Questi selettori sono basati sull'analisi della struttura attuale del sito
        # e potrebbero richiedere aggiustamenti in futuro se Sky Sport modifica il layout.
        # Cerchiamo i link all'interno delle "cards" di notizie.
        news_elements = soup.select('.c-card__body a.c-link')

        # Fallback per selettori più generici se il primo non trova nulla
        if not news_elements:
             news_elements = soup.select('a[href*="/calcio/serie-a/"]') # Link che contengono /calcio/serie-a/

        if not news_elements:
            print("  Avviso: Nessun elemento notizia trovato con i selettori predefiniti su Sky Sport.")
            return []

        for i, news_item in enumerate(news_elements):
            if i >= 10: # Limita a 10 notizie per mantenere il sito conciso
                break
            title = news_item.get_text(strip=True)
            link = news_item['href']
            
            # I link di Sky Sport sono spesso relativi, li rendiamo assoluti
            if not link.startswith('http'):
                link = f"https://sport.sky.it{link}"
            
            # Filtro base per titoli e link validi (esclude video o live che potrebbero avere formati diversi)
            if title and link and "video" not in link.lower() and "live" not in link.lower():
                news_items.append({"title": title, "link": link})
        
        print(f"Notizie raccolte da Sky Sport: {len(news_items)} articoli.")
        return news_items

    except requests.exceptions.RequestException as e:
        print(f"Errore HTTP/di connessione durante lo scraping delle notizie da Sky Sport: {e}")
        return []
    except Exception as e:
        print(f"Errore inatteso durante lo scraping delle notizie da Sky Sport: {e}")
        return []

# --- Esecuzione dello Scraping ---
SCRAPED_NEWS = []
print("Inizio scraping delle ultime notizie dalla Serie A (Sky Sport)...")
SCRAPED_NEWS = scrape_sky_sport_serie_a_news()
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
    <title>Notizie Serie A 2025-2026 (Sky Sport)</title>
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
            Ultime Notizie Serie A 2025-2026
        </h1>
        <p class="text-center text-gray-600 text-sm mb-8">Ultimo aggiornamento: {current_datetime}</p>
        
        <!-- Sezione per le Ultime Notizie (Fonte: Sky Sport) -->
        <h2 class="text-3xl font-bold text-gray-800 mb-6 mt-10 text-center">
            Ultime Notizie Serie A (Fonte: Sky Sport)
        </h2>
        <div class="bg-white shadow-lg rounded-lg p-6 mb-4">
            <ul class="list-none space-y-3">
"""

# Aggiunge le notizie recuperate da Sky Sport
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
                <li class="text-red-500">Nessuna notizia trovata o errore nello scraping da Sky Sport. Questo potrebbe essere dovuto a modifiche nella struttura del sito o alla mancanza di notizie pertinenti al momento.</li>
    """

html += """
            </ul>
        </div>
    </div>
    <footer class="mt-8 text-center text-gray-500 text-sm">
        Dati forniti da Sky Sport
    </footer>
</body>
</html>
"""

# Scrive l'HTML generato nel file index.html nella directory principale
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html generato con successo!")
