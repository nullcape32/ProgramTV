import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Channel URLs with their corresponding IDs from your previous list
CHANNEL_URLS = {
    "DIGI24 HD": {"url": "https://programtv.ro/canal-tv/digi-24", "id": 1},
    "ANTENA3": {"url": "https://programtv.ro/canal-tv/antena-3-cnn", "id": 2},
    "B1": {"url": "https://programtv.ro/canal-tv/b1-tv", "id": 3},
    "PROTV": {"url": "https://programtv.ro/canal-tv/pro-tv", "id": 7},
    "ANTENA1": {"url": "https://programtv.ro/canal-tv/antena-1", "id": 8},
    "TVR1": {"url": "https://programtv.ro/canal-tv/tvr-1", "id": 4},
    "TVR2": {"url": "https://programtv.ro/canal-tv/tvr-2", "id": 5},
    "Kanal D": {"url": "https://programtv.ro/canal-tv/kanal-d-hd", "id": 9},
    "Prima TV": {"url": "https://programtv.ro/canal-tv/prima-tv", "id": 10},
    "TVR3": {"url": "https://programtv.ro/canal-tv/tvr-3", "id": 11},
    "TVR International": {"url": "https://programtv.ro/canal-tv/tvr-international", "id": 12},
    "Digi 24": {"url": "https://programtv.ro/canal-tv/digi-24", "id": 13},
    "PROCINEMA": {"url": "https://programtv.ro/canal-tv/pro-cinema", "id": 14},
    "ANTENA STARS": {"url": "https://programtv.ro/canal-tv/antena-stars-", "id": 15},
    "National Geographic": {"url": "https://programtv.ro/canal-tv/national-geographic", "id": 16},
    "TVR Cultural": {"url": "https://programtv.ro/canal-tv/tvr-cultural", "id": 17},
    "HBO": {"url": "https://programtv.ro/canal-tv/hbo", "id": 20},
    "HBO_2": {"url": "https://programtv.ro/canal-tv/hbo-2", "id": 21},
    "FilmNow": {"url": "https://programtv.ro/canal-tv/film-now", "id": 25},
    "Atomic-TV": {"url": "https://programtv.ro/canal-tv/atomic-tv", "id": 26},
    "ZU-TV": {"url": "https://programtv.ro/canal-tv/zu-tv", "id": 27},
    "MUSIC-CHANNEL": {"url": "https://programtv.ro/canal-tv/music-channel", "id": 28},
    "KISS-TV": {"url": "https://programtv.ro/canal-tv/kiss-tv", "id": 29},
    "TVR Folclor": {"url": "https://programtv.ro/canal-tv/tvr-folclor", "id": 30},
    "ETNO TV": {"url": "https://programtv.ro/canal-tv/etno-tv", "id": 80},
    "REALITATEA": {"url": "https://programtv.ro/canal-tv/realitatea-plus", "id": 31},
    "PRIMA-NEWS": {"url": "https://programtv.ro/canal-tv/prima-news", "id": 32},
    "EURO-NEWS": {"url": "https://programtv.ro/canal-tv/euronews", "id": 33},
    "CNN-LIVE": {"url": "https://programtv.ro/canal-tv/cnn", "id": 34},
    "BBC-NEWS": {"url": "https://programtv.ro/canal-tv/bbc-news", "id": 35},
    "CBS-REALITY": {"url": "https://programtv.ro/canal-tv/cbs-reality", "id": 36},
    "PRS-1": {"url": "https://programtv.ro/canal-tv/prima-sport-1", "id": 38},
    "PRS-2": {"url": "https://programtv.ro/canal-tv/prima-sport-2", "id": 39},
    "ER1": {"url": "https://programtv.ro/canal-tv/eurosport-1", "id": 40},
    "ER2": {"url": "https://programtv.ro/canal-tv/eurosport-2", "id": 41},
    "CARTOON": {"url": "https://programtv.ro/canal-tv/cartoon-network", "id": 42},
    "DISCOVERY-CHANNEL": {"url": "https://programtv.ro/canal-tv/discovery-channel", "id": 44},
    "VIA-HIS": {"url": "https://programtv.ro/canal-tv/viasat-history", "id": 44},
    "VIA-EXPLORER": {"url": "https://programtv.ro/canal-tv/viasat-explorer", "id": 46},
    "BBC-EARTH": {"url": "https://programtv.ro/canal-tv/bbc-earth", "id": 47},
    "Rock TV": {"url": "https://programtv.ro/canal-tv/rock-tv", "id": 50},
    "Canal32": {"url": "https://programtv.ro/canal-tv/canal-32", "id": 51},
    "Magic TV": {"url": "https://programtv.ro/canal-tv/magic-tv", "id": 52},
    "CBS News": {"url": "https://programtv.ro/canal-tv/cbs-news", "id": 55},
    "DigiSport 1": {"url": "https://programtv.ro/canal-tv/digi-sport-1", "id": 56},
    "France24": {"url": "https://programtv.ro/canal-tv/france-24", "id": 74},
    "TVR Sport": {"url": "https://programtv.ro/canal-tv/tvr-sport", "id": 77},
    "Romania TV": {"url": "https://programtv.ro/canal-tv/romania-tv", "id": 78},
    "AMC": {"url": "https://programtv.ro/canal-tv/amc", "id": 23}
}


def scrape_programtv(channel_name, url):
    """Scrape program list from programtv.ro channel page"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching {channel_name}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    program_list = []

    # Find the main container
    main_container = soup.find("div", class_="background-white")
    if not main_container:
        print(f"⚠️ Could not find schedule container for {channel_name}")
        return []

    entries = main_container.find_all("div", class_="d-flex justify-content-start")

    for entry in entries:
        time_tag = entry.find("p", class_="px-3 pt-2 fw-bold")
        title_tag = entry.find("h2")
        live_tag = entry.find("span", class_="tv-show-live")

        time = time_tag.get_text(strip=True) if time_tag else ""
        title = title_tag.get_text(" ", strip=True) if title_tag else ""
        live = f" ({live_tag.get_text(strip=True)})" if live_tag else ""

        if title:
            full_text = f"{time} - {title}{live}".strip()

            # Remove unwanted fragments
            full_text = re.sub(r"👉 Vezi detalii", "", full_text, flags=re.IGNORECASE)
            full_text = re.sub(r"\(ACUM\)", "", full_text, flags=re.IGNORECASE)
            full_text = re.sub(r"\bACUM\b", "", full_text, flags=re.IGNORECASE)

            # Remove duplicated titles like "Pasagerii - Pasagerii"
            full_text = re.sub(
                r"^(.*? - )(.+?)\s*-\s*\2(\b|$)",  # regex pattern for repeated title
                r"\1\2",
                full_text,
                flags=re.IGNORECASE
            )

            # Clean up extra spaces
            full_text = re.sub(r"\s{2,}", " ", full_text).strip()

            program_list.append(full_text)

    return program_list


def scrape_all_channels(channel_urls):
    """Scrape all channels and format output for JSON"""
    all_channels = []

    for name, channel_data in channel_urls.items():
        print(f"🔎 Scraping {name}...")
        program = scrape_programtv(name, channel_data["url"])
        all_channels.append({
            "id": channel_data["id"],
            "tv_channel": name,
            "tv_program": program
        })

    return all_channels


def save_to_json(data, filename="programtv_schedule.json"):
    """Save results to JSON"""
    if not data:
        print("⚠️ No data to save.")
        return

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Saved schedule for {len(data)} channels to {filename}")


if __name__ == "__main__":
    print("🎬 Scraping programtv.ro (current day)...")
    results = scrape_all_channels(CHANNEL_URLS)
    save_to_json(results)
    print("🏁 Done at", datetime.now().strftime("%H:%M:%S"))
