import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

CHANNEL_URLS = {
    "HBO": "https://programtv.ro/canal-tv/hbo",
    "HBO2": "https://programtv.ro/canal-tv/hbo-2",
    "PROTV": "https://programtv.ro/canal-tv/pro-tv",
    "ANTENA1": "https://programtv.ro/canal-tv/antena-1",
    "Digi24 HD": "https://programtv.ro/canal-tv/digi-24",
    "FilmNow": "https://programtv.ro/canal-tv/film-now",
    "TVR3": "https://programtv.ro/canal-tv/tvr-3",
    "BBC Earth": "https://programtv.ro/canal-tv/bbc-earth",
    "Cartoon Network": "https://programtv.ro/canal-tv/cartoon-network",
    "Kanal D" : "https://programtv.ro/canal-tv/kanal-d- ",
    "Antena Stars": "https://programtv.ro/canal-tv/antena-stars- ",
    "Antena 3": "https://programtv.ro/canal-tv/antena-3-cnn",
    "EuroNews" : "https://programtv.ro/canal-tv/euronews",
    "Prima Sport1": "https://programtv.ro/canal-tv/prima-sport-ppv1",
    "RomaniaTV": "https://programtv.ro/canal-tv/romania-tv- ",
    "TVR1": "https://programtv.ro/canal-tv/tvr-1",
    "National Geographic": "https://programtv.ro/canal-tv/national-geographic",
    "Euro Sport 1":"https://programtv.ro/canal-tv/eurosport-1",
    "PROCINEMA": "https://programtv.ro/canal-tv/pro-cinema",
    "DigiSport 1": "https://programtv.ro/canal-tv/digi-sport-1",
    "Prima TV": "https://programtv.ro/canal-tv/prima-tv",
    "TVR2": "https://programtv.ro/canal-tv/tvr-2",
    "HBO2": "https://programtv.ro/canal-tv/hbo-2",
    "History": "https://programtv.ro/canal-tv/history",
    "BBC Earth": "https://programtv.ro/canal-tv/bbc-earth",
    "Discovery Channel": "https://programtv.ro/canal-tv/discovery-channel",
    "Antena 3 CNN": "https://programtv.ro/canal-tv/antena-3-cnn",
    "Realitatea Plus": "https://programtv.ro/canal-tv/realitatea-plus",
    "Viasat History  ": "https://programtv.ro/canal-tv/viasat-history- ",
    "Prima Sport PPV2": "https://programtv.ro/canal-tv/prima-sport-ppv2",
    "TVR Folclor": "https://programtv.ro/canal-tv/tvr-folclor",
    "Music Channel": "https://programtv.ro/canal-tv/music-channel",
    "BBC News": "https://programtv.ro/canal-tv/bbc-news",
    "TVR Sport": "https://programtv.ro/canal-tv/tvr-sport",
    "Romania TV  ": "https://programtv.ro/canal-tv/romania-tv- ",
    "Rock TV  ": "https://programtv.ro/canal-tv/rock-tv- ",
    "France 24": "https://programtv.ro/canal-tv/france-24",
    "Prima News": "https://programtv.ro/canal-tv/prima-news",
    "Eurosport 2": "https://programtv.ro/canal-tv/eurosport-2-",
    "Eurosport 1": "https://programtv.ro/canal-tv/eurosport-1- ",
    "Pro Cinema  ": "https://programtv.ro/canal-tv/pro-cinema- ",
    "Prima Sport 1": "https://programtv.ro/canal-tv/prima-sport-1",
    "Moldova TV": "https://programtv.ro/canal-tv/moldova-tv",
    "ZU TV": "https://programtv.ro/canal-tv/zu-tv",
    "Etno TV": "https://programtv.ro/canal-tv/etno-tv",
    "TVR Cultural": "https://programtv.ro/canal-tv/tvr-cultural",
    "CNN": "https://programtv.ro/canal-tv/cnn",
    "TVR International": "https://programtv.ro/canal-tv/tvr-international",
    "MTV Europe": "https://programtv.ro/canal-tv/mtv-europe",
    "TVR Info": "https://programtv.ro/canal-tv/tvr-info",
    "Kiss TV": "https://programtv.ro/canal-tv/kiss-tv",
    "B1": "https://programtv.ro/canal-tv/b1-tv"
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

            # Remove unwanted text fragments
            full_text = re.sub(r"👉 Vezi detalii", "", full_text, flags=re.IGNORECASE)
            full_text = re.sub(r"\(ACUM\)", "", full_text, flags=re.IGNORECASE)
            full_text = re.sub(r"\bACUM\b", "", full_text, flags=re.IGNORECASE)

            # Clean up extra spaces
            full_text = re.sub(r"\s{2,}", " ", full_text).strip()

            program_list.append(full_text)

    return program_list


def scrape_all_channels(channel_urls):
    """Scrape all channels and format output for JSON"""
    all_channels = []

    for i, (name, url) in enumerate(channel_urls.items(), start=1):
        print(f"🔎 Scraping {name}...")
        program = scrape_programtv(name, url)
        all_channels.append({
            "id": f"{i:02}",
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
