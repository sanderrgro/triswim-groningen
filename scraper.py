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

# Terugvalrooster voor het geval dat de live scraping geen resultaten oplevert
DEFAULT_SCHEDULE = [
    {"pool_id": "kardinge", "activity": "Banenzwemmen 50m", "day_of_week": "Maandag", "start_time": "07:00", "end_time": "08:30", "pool_type": "50m"},
    {"pool_id": "kardinge", "activity": "Banenzwemmen", "day_of_week": "Dinsdag", "start_time": "07:00", "end_time": "08:30", "pool_type": "25m"},
    {"pool_id": "helperbad", "activity": "Ochtendzwemmen", "day_of_week": "Woensdag", "start_time": "07:00", "end_time": "08:30", "pool_type": "25m"},
    {"pool_id": "parrel", "activity": "Banenzwemmen", "day_of_week": "Donderdag", "start_time": "07:00", "end_time": "08:30", "pool_type": "25m"},
    {"pool_id": "kardinge", "activity": "Banenzwemmen 50m", "day_of_week": "Vrijdag", "start_time": "07:00", "end_time": "08:30", "pool_type": "50m"},
    {"pool_id": "haren", "activity": "Banenzwemmen", "day_of_week": "Zaterdag", "start_time": "08:00", "end_time": "10:00", "pool_type": "25m"},
    {"pool_id": "drachten", "activity": "50m Borstcrawl Training", "day_of_week": "Zondag", "start_time": "09:00", "end_time": "11:00", "pool_type": "50m"}
]

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
                elements = soup.find_all(['tr', 'li', 'p', 'div', 'td'])
                for elem in elements:
                    text = elem.get_text(separator=' ').strip()
                    if is_triathlon_suitable(text):
                        times = re.findall(r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})', text)
                        if times:
                            for start, end in times:
                                sessions.append({
                                    "pool_id": pool_id,
                                    "date": datetime.today().strftime('%Y-%m-%d'),
                                    "day": datetime.today().weekday() + 1,
                                    "start_time": start,
                                    "end_time": end,
                                    "activity": "Banenzwemmen"
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

    # Fallback als er live niks is opgehaald
    if not sessions:
        print("Geen live sessies gevonden. Fallback rooster wordt geladen...")
        sessions = DEFAULT_SCHEDULE

    print(f"Aantal sessies in uitvoer: {len(sessions)}")

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