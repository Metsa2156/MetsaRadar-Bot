import requests
import time
import random
import sys

FIREBASE_URL = "https://metsaradar-default-rtdb.europe-west1.firebasedatabase.app/radar.json"
ALLIANCE_ID = "a3ceb9ca6dc249f88ecefceaf045eebc"

HERO_TYPES = {
    50006: "Tank", 50007: "Tank", 50008: "Tank", 50009: "Tank", 50010: "Tank",
    40006: "Tank", 40008: "Tank", 40009: "Tank", 40010: "Tank", 40012: "Tank", 40020: "Tank",
    30002: "Tank", 30005: "Tank",
    50017: "Uçak", 50018: "Uçak", 50019: "Uçak", 50020: "Uçak", 50021: "Uçak",
    40015: "Uçak", 40019: "Uçak", 30004: "Uçak",
    50013: "Füze", 50014: "Füze", 50015: "Füze", 50016: "Füze", 50022: "Füze",
    40007: "Füze", 40013: "Füze", 40018: "Füze"
}

def get_headers():
    return {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "cookie": "_ga=GA1.1.1447011317.1782809932; _ga_FNLN1GJZEH=GS2.1.s1783682669$o5$g0$t1783682669$j60$l0$h0; jwt=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyOTgiLCJpYXQiOjE3ODUxODgwNzMsImV4cCI6MTc4NTE5MTY3M30.jfQMMgZWLvibUVNK34Ry-GPXHcnydxtMif6jj-GEt74; refreshToken=fe3916ad-74f4-4a6c-86b2-531bca59af30; cf_clearance=Wj8e8TQ60U4yErutqwtnldWezjMc.3tYefYCXf0nUtA-1785188086-1.2.1.1-rTBsnooeEjajSKC_iShu_VQgMLfQMqrw7W3Lm0nS8DUD.bexJBFTIvyg6bDg7vTHgqpJS2m1h2OnVCevts8zD5Ij_maiIBDiLlguE93wask.hY9C58Q4WXzGAglLYZCQc0DT9olZaKwajZQzCEcLbDUiY_AdSVuP_6eTzelhNOQRkRLQL3rdsotDKL9t0C7aXDcsBgNOjTFkSI7ORVkbPIc1TvkwyYmG_QwmRRJE.TloD6uxmQMs.7O573ctrvQEUiQ5eh2hs31IcYrv8m0JxzOFT2r30kjS5r89fsXOko2yDZhKLfHaZ8z1jz.mgNo7rFj8E5aGnPqiXcjEcHJjii4VuAHJDbqWh2jZopK.OjXK4p4ruIE8uvXgUeXsd4MZmJQCRt3c_okf9T0icoExyxt8a5xcnyPNpF9ZZS67gd733K19HijMdrcVk60hlh4Z5bEenB1oLc1C4ehSRGACKA",
        "origin": "https://lwatlas.com",
        "referer": "https://lwatlas.com/",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Brave";v="150"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
    }

def main():
    print("Gölge İşçi Başladı! (Maksimum Güç Algoritması Aktif)")
    
    try:
        fb_res = requests.get(FIREBASE_URL, timeout=10)
        history_map = fb_res.json() if fb_res.status_code == 200 and fb_res.json() else {}
    except Exception:
        history_map = {}

    members_url = f"https://api.lwatlas.com/v1/alliances/{ALLIANCE_ID}/members"
    
    try:
        res = requests.get(members_url, headers=get_headers(), timeout=15)
        if res.status_code != 200:
            print(f"HATA: LwAtlas kapıyı açmadı! Kod: {res.status_code}")
            sys.exit(1)
            
        raw_members = res.json().get("members", [])
    except Exception as e:
        print(f"Ana listeye erişilemedi: {e}")
        sys.exit(1)

    random.shuffle(raw_members)
    new_data = {}

    for m in raw_members:
        name = m.get("playerName", "").replace("\u200B", "").replace("\u200D", "").replace("\uFEFF", "").strip()
        map_key = name.lower().replace(" ", "")
        
        if not map_key: continue

        lvl = int(m.get("level", 0))
        rank = m.get("allianceRank", 1)
        total_power = int(m.get("power", 0))
        army_power = int(m.get("armyPower", 0))
        non_army_power = total_power - army_power

        if lvl < 28: continue

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
                        data = sq_res.json()
                        sources = data.get("sources", [])
                        main_squad = None
                        
                        # BÜTÜN KAYNAKLARI TARA, EN YÜKSEK GÜCÜ BUL! (Kamyon dahil, null korumalı)
                        for src in sources:
                            squads = src.get("squads", [])
                            for s in squads:
                                raw_cp = s.get("squadPower")
                                # Eğer güç null (None) gelirse es geç, sayıysa karşılaştır
                                if raw_cp is not None:
                                    cp = int(raw_cp)
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
                    else:
                        print(f"[{name}] Birlikler Çekilemedi! Hata Kodu: {sq_res.status_code}")
                        time.sleep(3) 
                except:
                    time.sleep(2)

        old_data = history_map.get(map_key, {})
        final_power = api_squad_power
        final_type = api_type
        
        old_power = old_data.get("power", 0)
        if old_power > 50000000: old_power = 0
            
        if final_power == 0 or old_power > final_power:
            final_power = old_power
        
        if final_type == "?" and old_data.get("type", "?") != "?":
            final_type = old_data.get("type")
        
        save_type = final_type
        if final_power < 9000000: save_type = "?"

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
