import os
import requests

API_KEY = os.getenv("RIOT_API_KEY", "xxx")
REGION = "americas"
PLATFORM = "br1"

def riot_headers():
    return {"X-Riot-Token": API_KEY}

# ===== Mapeamento de spells =====
SPELLS = {
    1: "SummonerBoost",
    3: "SummonerExhaust",
    4: "SummonerFlash",
    6: "SummonerHaste",
    7: "SummonerHeal",
    11: "SummonerSmite",
    12: "SummonerTeleport",
    13: "SummonerMana",
    14: "SummonerDot",
    21: "SummonerBarrier",
    30: "SummonerPoroThrow",
    32: "SummonerSnowball"
}

# ===== PUUID =====
def get_puuid(summoner_name, tag_line="BR1"):
    url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag_line}"
    r = requests.get(url, headers=riot_headers(), timeout=15)
    r.raise_for_status()
    return r.json()["puuid"]

# ===== Histórico de partidas =====
def get_match_history(puuid, count=5):
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}"
    r = requests.get(url, headers=riot_headers(), timeout=15)
    r.raise_for_status()
    match_ids = r.json()

    matches = []
    for match_id in match_ids:
        url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        r = requests.get(url, headers=riot_headers(), timeout=15)
        r.raise_for_status()
        data = r.json()

        participants = data["info"]["participants"]
        player = next(p for p in participants if p["puuid"] == puuid)

        match_data = {
            "win": player["win"],
            "champion": player["championName"],
            "kills": player["kills"],
            "deaths": player["deaths"],
            "assists": player["assists"],
            "duration": int(data["info"]["gameDuration"] / 60),
            "mode": data["info"]["gameMode"],
            "spell1": SPELLS.get(player["summoner1Id"], "SummonerFlash"),
            "spell2": SPELLS.get(player["summoner2Id"], "SummonerHeal"),
        }

        for i in range(7):
            match_data[f"item{i}"] = player.get(f"item{i}", 0)

        matches.append(match_data)

    return matches

# ===== Data Dragon helpers =====
def get_latest_ddragon_version():
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()[0]

def get_champions(locale="pt_BR"):
    version = get_latest_ddragon_version()
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/{locale}/champion.json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()["data"]

    champions = []
    for champ_id, champ in data.items():
        champions.append({
            "id": champ_id,
            "name": champ["name"],
            "splash": f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_id}_0.jpg"
        })
    champions.sort(key=lambda x: x["name"].lower())
    return champions

def get_champion_details(champion_name, locale="pt_BR"):
    version = get_latest_ddragon_version()
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/{locale}/champion/{champion_name}.json"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()["data"][champion_name]

    # Skins
    skins = [{"num": s["num"], "name": s["name"], "splash": f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion_name}_{s['num']}.jpg"} for s in data.get("skins", [])]

    # Spells
    spells = [{"id": sp.get("id"), "name": sp.get("name"), "description": sp.get("description"), "icon": f"https://ddragon.leagueoflegends.com/cdn/{version}/img/spell/{sp.get('id')}.png"} for sp in data.get("spells", [])]

    # Passiva
    passive = {
        "name": data["passive"]["name"],
        "description": data["passive"]["description"],
        "icon": f"https://ddragon.leagueoflegends.com/cdn/{version}/img/passive/{data['passive']['image']['full']}"
    }

    # Lore
    lore = data.get("lore", "")

    return {
        "id": data["id"],
        "name": data["name"],
        "title": data.get("title", ""),
        "skins": skins,
        "spells": spells,
        "passive": passive,
        "lore": lore
    }
