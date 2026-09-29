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

ALLOW_KEYWORDS = ["banenzwemmen", "banen zwemmen", "borstcrawl", "sportief zwemmen", "vroege vogel"]
EXCLUDE_KEYWORDS = ["baby", "peuter", "aquajogging", "aquafit", "therapie", "leszwemmen", "discowemmen"]

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
    headers = {"User-Agent": "Mozilla/5.0"}
    for pool_id, url in urls.items():
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.find_all(['tr', 'div'], class_=re.compile(r'(rooster|openingstijd|activity)'))
                for row in rows:
                    text = row.get_text(separator=' ').strip()
                    if is_triathlon_suitable(text):
                        times = re.findall(r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})', text)
                        if times:
                            start, end = times[0]
                            sessions.append({
                                "poolId": pool_id,
                                "date": datetime.today().strftime('%Y-%m-%d'),
                                "day": datetime.today().weekday() + 1,
                                "start": start,
                                "end": end,
                                "title": "Banenzwemmen"
                            })
        except Exception as e:
            print(f"Fout bij ophalen {pool_id}: {e}")
    return sessions

def fetch_haren_sessions():
    sessions = []
    url = "https://www.scharlakenhof.nl/openingstijden/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for item in soup.find_all(['li', 'p', 'tr']):
                text = item.get_text()
                if is_triathlon_suitable(text):
                    times = re.findall(r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})', text)
                    if times:
                        start, end = times[0]
                        sessions.append({
                            "poolId": "haren",
                            "date": datetime.today().strftime('%Y-%m-%d'),
                            "day": datetime.today().weekday() + 1,
                            "start": start,
                            "end": end,
                            "title": "Banenzwemmen"
                        })
    except Exception as e:
        print(f"Fout bij ophalen Haren: {e}")
    return sessions

def main():
    print("Scrapen gestart...")
    sessions = []
    sessions.extend(fetch_sport050_sessions())
    sessions.extend(fetch_haren_sessions())

    output_data = {
        "updated_at": datetime.now().isoformat(),
        "pools": POOLS,
        "sessions": sessions
    }

    with open('schedule.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Klaar! {len(sessions)} sessies opgeslagen.")

if __name__ == "__main__":
    main()