import json
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

POOLS = {
    "kardinge": {"name": "Sportcentrum Kardinge", "city": "Groningen", "type": "25m / 50m", "lat": 53.2381, "lng": 6.6025},
    "parrel": {"name": "Zwembad De Parrel", "city": "Groningen", "type": "25m", "lat": 53.2345, "lng": 6.5512},
    "helperbad": {"name": "Helperbad", "city": "Groningen", "type": "25m", "lat": 53.1978, "lng": 6.5791},
    "haren": {"name": "Scharlakenhof", "city": "Haren", "type": "25m", "lat": 53.1712, "lng": 6.6120},
    "drachten": {"name": "De Welle", "city": "Drachten", "type": "50m Wedstrijdbad", "lat": 53.1090, "lng": 6.0940}
}

# Ruimere trefwoorden om meer sessies op te vangen
ALLOW_KEYWORDS = ["banen", "borstcrawl", "sportief", "vroege vogel", "openstelling", "zwemmen"]
EXCLUDE_KEYWORDS = ["baby", "peuter", "aquajogging", "aquafit", "therapie", "leszwemmen", "discowemmen", "feest"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7"
}

def is_triathlon_suitable(title):
    t = title.lower()
    if any(ex in t for ex in EXCLUDE_KEYWORDS):
        return False
    return any(inc in t for inc in ALLOW_KEYWORDS)

def fetch_sport050_sessions():
    sessions = []
    urls = {
        "kardinge": "https://www.sport050.nl/zwembaden/kardinge/openingstijden/",
        "parrel": "https://www.sport050.nl/zwembaden/de-parrel/openingstijden/",
        "helperbad": "https://www.sport050.nl/zwembaden/helperbad/openingstijden/"
    }
    
    for pool_id, url in urls.items():
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Zoek in alle tekstblokken en tabellen
                elements = soup.find_all(['tr', 'li', 'p', 'div', 'td'])
                for elem in elements:
                    text = elem.get_text(separator=' ').strip()
                    if is_triathlon_suitable(text):
                        times = re.findall(r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})', text)
                        if times:
                            for start, end in times:
                                sessions.append({
                                    "poolId": pool_id,
                                    "date": datetime.today().strftime('%Y-%m-%d'),
                                    "day": datetime.today().weekday() + 1,
                                    "start": start,
                                    "end": end,
                                    "title": "Banenzwemmen"
                                })
        except Exception as e:
            print(f"Fout bij ophalen Sport050 ({pool_id}): {e}")
    return sessions

def main():
    print("Scrapen gestart...")
    sessions = []
    
    try:
        sessions.extend(fetch_sport050_sessions())
    except Exception as e:
        print(f"Algemene scrape fout: {e}")

    print(f"Aantal gevonden sessies: {len(sessions)}")

    output_data = {
        "updated_at": datetime.now().isoformat(),
        "pools": POOLS,
        "sessions": sessions
    }

    with open('schedule.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("schedule.json succesvol bijgewerkt.")

if __name__ == "__main__":
    main()