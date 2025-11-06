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
    "HBO": {"url": "https://programtv.ro/canal-tv/hbo", "id": 20},
    "HBO2": {"url": "https://programtv.ro/canal-tv/hbo-2", "id": 21},
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
