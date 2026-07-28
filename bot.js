const API_KEY = process.env.LWATLAS_API_KEY;
const ALLIANCE_ID = "a3ceb9ca6dc249f88ecefceaf045eebc";
const FIREBASE_URL = "https://metsaradar-default-rtdb.europe-west1.firebasedatabase.app/radar.json";

const HERO_TYPES = {
  50006: "Tank", 50007: "Tank", 50008: "Tank", 50009: "Tank", 50010: "Tank",
  40006: "Tank", 40008: "Tank", 40009: "Tank", 40010: "Tank", 40012: "Tank", 40020: "Tank",
  30002: "Tank", 30005: "Tank",
  50017: "Uçak", 50018: "Uçak", 50019: "Uçak", 50020: "Uçak", 50021: "Uçak",
  40015: "Uçak", 40019: "Uçak", 30004: "Uçak",
  50013: "Füze", 50014: "Füze", 50015: "Füze", 50016: "Füze", 50022: "Füze",
  40007: "Füze", 40013: "Füze", 40018: "Füze"
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function runBot() {
  console.log("Resmi API ile MetsaRadar Bot çalışmaya başladı...");
  
  const options = {
    method: "GET",
    headers: {
      "X-Api-Key": API_KEY,
      "Accept": "application/json"
    }
  };

  // Resmi members endpoint'i tüm listeyi, gücü ve rütbeyi tek kalemde veriyor!
  const membersUrl = "https://api.lwatlas.com/v1/alliances/" + ALLIANCE_ID + "/members";
  const res = await fetch(membersUrl, options);
  
  if (!res.ok) {
    console.error("İttifak listesi çekilemedi. Hata Kodu:", res.status);
    return;
  }
  
  const data = await res.json();
  const rawMembers = data.members || [];
  const newData = {};

  for (let i = 0; i < rawMembers.length; i++) {
    const m = rawMembers[i];
    const name = (m.playerName || "").replace(/[\u200B-\u200D\uFEFF]/g, "").trim();
    const mapKey = name.toLowerCase().replace(/\s+/g, "");
    if (!mapKey) continue;
    
    const lvl = parseInt(m.level || 0);
    
    // KURAL: 27 Level Çöpte!
    if (lvl < 28) continue; 
    
    const rank = m.allianceRank || 1;
    const totalPower = parseInt(m.power || 0); // Resmi net güç
    const armyPower = parseInt(m.armyPower || 0);
    const nonArmyPower = totalPower - armyPower;
    
    // T10 Kuralı: Lvl 30, Power > 100M, Non-Army > 70M
    const isT10 = (lvl === 30 && totalPower >= 100000000 && nonArmyPower >= 70000000);
    
    let apiType = "?";
    
    // Eğer adam 9M üstü ise takım türünü (Uçak/Tank) öğrenmek için squads'a bakıyoruz
    if (totalPower >= 9000000) {
      await sleep(1000); // 1 saniye kibar bekleme
      
      const squadUrl = "https://api.lwatlas.com/v1/players/" + m.playerUid + "/squads";
      const sqRes = await fetch(squadUrl, options);
      
      if (sqRes.ok) {
        const sqData = await sqRes.json();
        const sources = sqData.sources || [];
        let mainTruck = null;
        
        for (let sIdx = 0; sIdx < sources.length; sIdx++) {
          const trucks = sources[sIdx].trucks || []; 
          for (let tIdx = 0; tIdx < trucks.length; tIdx++) {
            const trk = trucks[tIdx];
            const cp = parseInt(trk.squadPower || trk.power || trk.truckPower || 0);
            if (cp > 0) {
              mainTruck = trk;
              break;
            }
          }
          if (mainTruck) break;
        }
        
        if (mainTruck && mainTruck.heroes) {
          const counts = {"Tank": 0, "Uçak": 0, "Füze": 0, "Bilinmeyen": 0};
          for (let hIdx = 0; hIdx < mainTruck.heroes.length; hIdx++) {
            const hid = mainTruck.heroes[hIdx].heroCfgId;
            if (HERO_TYPES[hid]) counts[HERO_TYPES[hid]]++;
            else counts.Bilinmeyen++;
          }
          let maxC = 0, enYuksekTur = "";
          for (const t in counts) {
            if (t !== "Bilinmeyen" && counts[t] > maxC) {
              maxC = counts[t];
              enYuksekTur = t;
            }
          }
          if (maxC >= 3) apiType = enYuksekTur;
          else if (maxC === 2) apiType = enYuksekTur + " Hibrit";
          else apiType = "Hibrit";
        }
      }
    }
    
    let saveType = apiType;
    if (totalPower < 9000000) saveType = "?";
    
    newData[mapKey] = {
      originalName: name,
      level: lvl,
      rank: "R" + rank,
      type: saveType,
      power: totalPower, // Artık sıfır değil, resmi net güç yazılıyor!
      t10: isT10
    };
  }
  
  console.log("Resmi veriler işlendi. Firebase güncelleniyor...");
  
  const fbRes = await fetch(FIREBASE_URL, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(newData)
  });
  
  if (fbRes.ok) {
    console.log("Firebase tertemiz verilerle güncellendi!");
  } else {
    console.error("Firebase hatası:", fbRes.status);
  }
}

runBot();
