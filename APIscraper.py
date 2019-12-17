import os
import requests
import json
from collections import defaultdict

from tqdm import tqdm

header = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": "RGAPI-b5adc3dd-79a6-492b-9192-f441deff1c80",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}
summoner_url = 'https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}'
match_ids_url = 'https://{}.api.riotgames.com/lol/match/v4/matchlists/by-account/{}'
match_url = 'https://{}.api.riotgames.com/lol/match/v4/matches/{}'

if not os.path.isfile('data/accountIDs.json'):
    with open('data/players.json', 'r') as fp:
        players = json.load(fp)

    accountIDs = defaultdict(list)
    for region in players:
        for player in tqdm(players[region]):
            dat = requests.get(summoner_url.format(region, player), headers=header)
            accountIDs[region].append(dat.json()['accountId'])

    with open('data/accountIDs.json', 'w') as fp:
        json.dump(accountIDs, fp, sort_keys=True, indent=4)


if not os.path.isfile('data/matchIDs.json'):
    matches = {}
    with open('data/accountIDs.json', 'r') as fp:
        ids = json.load(fp)

    for region in ids:
        for id_ in tqdm(ids[region]):
            matchlist = requests.get(match_ids_url.format(region, id_), headers=header)
            matches[id_] = [m['gameId'] for m in matchlist.json()['matches']]

    with open('data/matchIDs.json', 'w') as fp:
        json.dump(matches, fp, sort_keys=True, indent=4)


with open('data/region_map.json', 'r') as fp:
    region_map = json.load(fp)
with open('data/matchIDs.json', 'r') as fp:
    match_ids = json.load(fp)

seen_matches = {}

for acc_id in match_ids:
    for match_id in tqdm(match_ids[acc_id]):
        if match_id not in seen_matches:
            match_data = requests.get(match_url.format(region_map[acc_id], match_id), headers=header).json()
            if 'participants' in match_data:
                seen_matches[match_id] = match_data['participants']


with open('data/match_data.json', 'w') as fp:
    json.dump(seen_matches, fp, sort_keys=True, indent=4)
