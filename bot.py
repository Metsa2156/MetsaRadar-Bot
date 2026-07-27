import requests
import time
import random

FIREBASE_URL = "https://metsaradar-default-rtdb.europe-west1.firebasedatabase.app/radar.json"
ALLIANCE_ID = "b12ec89de52444eb82ad74c36b96f521"

HERO_TYPES = {
    50006: "Tank", 50007: "Tank", 50008: "Tank", 50009: "Tank", 50010: "Tank",
    40006: "Tank", 40008: "Tank", 40009: "Tank", 40010: "Tank", 40012: "Tank", 40020: "Tank",
    30002: "Tank", 30005: "Tank",
    50017: "Uçak", 50018: "Uçak", 50019: "Uçak", 50020: "Uçak", 50021: "Uçak",
    40015: "Uçak", 40019: "Uçak", 30004: "Uçak",
    50013: "Füze", 50014: "Füze", 50015: "Füze", 50016: "Füze", 50022: "Füze",
    40007: "Füze", 40013: "Füze", 40018: "Füze"
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS), "Accept": "application/json"}

def main():
    print("Gölge İşçi Başladı ve Can Damarı Bağlandı!")
    
    try:
        fb_res = requests.get(FIREBASE_URL, timeout=10)
        history_map = fb_res.json() if fb_res.status_code == 200 and fb_res.json() else {}
        print("Firebase bağlantısı başarılı.")
    except Exception as e:
        print(f"Firebase bağlantı hatası: {e}")
        history_map = {}

    members_url = f"https://lwatlas.com/api/v1/alliances/{ALLIANCE_ID}/members"
    print(f"LwAtlas'a istek atılıyor: {members_url}")
    
    try:
        # 15 saniye içinde cevap gelmezse patlamasın, yakalasın diye timeout eklendi
        res = requests.get(members_url, headers=get_headers(), timeout=15)
        print(f"LwAtlas Yanıt Kodu: {res.status_code}")
        raw_members = res.json().get("members", [])
        print(f"Toplam üye bulundu: {len(raw_members)}")
    except Exception as e:
        print(f"LwAtlas ana listeye erişilemedi, hata: {e}")
        return

    random.shuffle(raw_members)
    new_data = {}

    for m in raw_members:
        name = m.get("playerName", "").replace("\u200B", "").replace("\u200D", "").replace("\uFEFF", "").strip()
        map_key = name.lower().replace(" ", "")
        
        if not map_key:
            continue

        lvl = int(m.get("level", 0))
        rank = m.get("allianceRank", 1)
        total_power = int(m.get("power", 0))
        army_power = int(m.get("armyPower", 0))
        non_army_power = total_power - army_power

        if lvl < 28:
            continue

        is_t10 = False
        if lvl == 30 and total_power >= 100000000 and non_army_power >= 70000000:
            is_t10 = True

        api_squad_power = 0
        api_type = "?"
        uid = m.get("playerUid")

        if total_power >= 9000000:
            squad_url = f"https://api.lwatlas.com/v1/players/{uid}/squads"
            
            for attempt in range(2):
                time.sleep(random.uniform(1.5, 3.0)) 
                try:
                    sq_res = requests.get(squad_url, headers=get_headers(), timeout=10)
                    if sq_res.status_code == 200:
                        squads = sq_res.json().get("squads", [])
                        main_squad = None
                        for s in squads:
                            cp = int(s.get("squadPower", 0))
                            if cp > api_squad_power:
                                api_squad_power = cp
                                main_squad = s
                        
                        if main_squad and "heroes" in main_squad:
                            counts = {"Tank": 0, "Uçak": 0, "Füze": 0, "Bilinmeyen": 0}
                            for h in main_squad["heroes"]:
                                hid = h.get("heroCfgId")
                                if hid in HERO_TYPES:
                                    counts[HERO_TYPES[hid]] += 1
                                else:
                                    counts["Bilinmeyen"] += 1
                            
                            max_c = 0
                            en_yuksek_tur = ""
                            for t, c in counts.items():
                                if t != "Bilinmeyen" and c > max_c:
                                    max_c = c
                                    en_yuksek_tur = t
                            
                            if max_c >= 3:
                                api_type = en_yuksek_tur 
                            elif max_c == 2:
                                api_type = f"{en_yuksek_tur} Hibrit" 
                            else:
                                api_type = "Hibrit" 
                        break 
                    elif sq_res.status_code in [403, 429]:
                        time.sleep(3) 
                except:
                    time.sleep(2)

        old_data = history_map.get(map_key, {})
        final_power = api_squad_power
        final_type = api_type
        
        old_power = old_data.get("power", 0)
        if old_power > 50000000: 
            old_power = 0
            
        if final_power == 0 or old_power > final_power:
            final_power = old_power
        
        if final_type == "?" and old_data.get("type", "?") != "?":
            final_type = old_data.get("type")
        
        save_type = final_type
        if final_power < 9000000:
            save_type = "?"

        new_data[map_key] = {
            "originalName": name,
            "level": lvl,
            "rank": f"R{rank}",
            "type": save_type,
            "power": final_power,
            "t10": is_t10
        }
        print(f"Tarandı: {name} | Güç: {final_power} | Tür: {save_type}")

    try:
        requests.put(FIREBASE_URL, json=new_data, timeout=15)
        print("Tüm veriler Firebase'e başarıyla yazıldı!")
    except Exception as e:
        print(f"Firebase yazma hatası: {e}")

if __name__ == "__main__":
    main()
