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

# 1. LwAtlas'ın orijinal Fetch kodundan alınan maske (Çerezsiz)
def get_anon_headers():
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "referrer": "https://lwatlas.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
    }

# 2. Orijinal Fetch kodu + Senin Cookie'n (credentials: include mantığı)
def get_auth_headers():
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "referrer": "https://lwatlas.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
        "cookie": "jwt=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2OTkiLCJpYXQiOjE3ODUyNDI1ODUsImV4cCI6MTc4NTI0NjE4NX0.rycUou_CBXL7goO8sTOZBg0IEuWA6zQkJUKk5EraNKU; refreshToken=4ff387c8-0929-4209-b16e-3d267a84a741; cf_clearance=YdxX5mL1lmiKd4l9iuJvdFJrFVyzoV_Mk0opdJTQBAY-1785242807-1.2.1.1-RPcUQBUx8SmExCAfDTz3gS8EhbjKL.2eYuPPwlGqmeOGmF0Nd94imAIjiicb0uv7vm9Ab8rVANsgjCVGXdTZzU3eoTDFjTA3KKzWFF1eJdGTXI_bNUeY3NoDBHA80rR4oP4BxYC83V_0Z5RARV265PpjZonYN1wkD_neLB92Yv.1GzB7rkj_RFljRodg2IB3acA30n3cvUpSMhMXhtXwv8C5NCKiK.cOeocneu31dB7ehdXqVmj26WAfwWBMKm2jl764xJcCsRTvn4WQAolkSGDU.AOE_PGnOl3hL0XnAkksAMsNwdA2ZIgtpbd.LzcQO3Ja9EFZKz1PH95sfACKDrLSNfADV2SwtWZlFGXRdbrVB8CuYsXlSDI3SgifmzXlw8njnDnl6Gr7EIZaIIN3W_JEfYWgtC.O7IilvWE_GlBOpxN8qMboSH8hBedjfCelu_Amb7M9caq2g6SQyGKyvQ"
    }

def main():
    print("GÖLGE İŞÇİ GITHUB'A DÖNDÜ! (Orijinal İstek Maskesi Aktif)")
    
    try:
        fb_res = requests.get(FIREBASE_URL, timeout=10)
        history_map = fb_res.json() if fb_res.status_code == 200 and fb_res.json() else {}
    except Exception:
        history_map = {}

    members_url = f"https://api.lwatlas.com/v1/alliances/{ALLIANCE_ID}/members"
    try:
        res = requests.get(members_url, headers=get_anon_headers(), timeout=15)
        if res.status_code != 200:
            print(f"HATA: Liste çekilemedi! Kod: {res.status_code}")
            sys.exit(1)
        raw_members = res.json().get("members", [])
    except Exception as e:
        print(f"Ana listeye erişilemedi: {e}")
        sys.exit(1)

    if not raw_members:
        print("HATA: Liste bomboş geldi!")
        sys.exit(1)
        
    ata8_check = any("MADHEX" in m.get("playerName", "") or "K4LENDERBEY" in m.get("playerName", "") for m in raw_members)
    if not ata8_check:
        print(f"KRİTİK HATA! Çekilen ilk oyuncu: {raw_members[0].get('playerName', '')}")
        print("LwAtlas anonim isteğe rağmen eski ittifakı dayatıyor! Cookie yenilenmeli.")
        sys.exit(1)

    print(f"SÜPER! ATA8 Aslanları ({len(raw_members)} kişi) bulundu. Ordular taranıyor...")

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
                # Ban yememek için 3.5 ile 5 saniye arası rastgele bekleme
                time.sleep(random.uniform(3.5, 5.0)) 
                try:
                    sq_res = requests.get(squad_url, headers=get_auth_headers(), timeout=10)
                    if sq_res.status_code == 200:
                        data = sq_res.json()
                        sources = data.get("sources", [])
                        main_squad = None
                        
                        for src in sources:
                            squads = src.get("squads", [])
                            for s in squads:
                                raw_cp = s.get("squadPower")
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
                        print(f"[{name}] Takım okunamadı. Kod: {sq_res.status_code}")
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
