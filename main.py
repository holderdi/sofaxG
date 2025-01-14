import requests
import csv
print("\r\n")

# The team ID we are searching for
# ARM = Arminia 
# SGD = Dresden 
# M60 = 1860 München 
# FCS = Saarbrücken 
# BVB = Borussia Dortmund II
# UHA = Unterhachingen 
# ERZ = Aue  
# H96 = Hannover 96 II 
# RWE = Essen 
# AAC = Aachen
# SCV = Verl 
# WEH = Wiesbaden
# SVS = Sandhausen 
# OSN = Osnabrück 
# HAN = Rostock 
# VFB = Stuttgart II 
# VIK = Viktoria Köln 
# COT = Cottbus
# FCI = Ingolstadt 
# WAM = Mannheim

start = int(input("\r\nSpieltag von: "))
end = int(input("\r\nSpieltag bis: "))
team_id = str(input("\r\nTeam ID: "))
# CSV-Daten einlesen
csv_filename = f"xG_shots_players_per_team_csv/{start}_to_{end}_{team_id}_xG.csv"
file_created = False
with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)

    for round in range(start, end + 1): 

        url = f"https://www.sofascore.com/api/v1/unique-tournament/491/season/63786/events/round/{round}"
        payload = {}
        headers = {
            'accept': '*/*',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.sofascore.com/de/turnier/fussball/germany/3-liga/491',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'x-requested-with': 'f0ee70',
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        matches = response.json()['events']
        # List to store tournament IDs
        match_ids = []
        team_events = []
        team = {}

        # Iterate over each event
        for event in matches:
            # Check if the homeTeam or awayTeam id matches the specified team id
            if event["homeTeam"]["nameCode"] == team_id or event["awayTeam"]["nameCode"] == team_id:
                # Append the tournament id to the list
                match_ids.append(event["id"])
                if event["homeTeam"]["nameCode"] == team_id:
                    is_home = True
                else:
                    is_home = False
            
                team = {
                "homeTeam": is_home,
                "id": event["id"],
                "match": f"{event['homeTeam']['name']} : {event['awayTeam']['name']}",
                "result": f"{event['homeScore']['current']} : {event['awayScore']['current']}"    
                }
                team_events.append(team)       

        headers = {
            "accept": "*/*",
            "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "f3d7cd",
            "referrer": "https://www.sofascore.com/de/turnier/fussball/germany/3-liga/491",
            "referrerPolicy": "strict-origin-when-cross-origin",
            "method": "GET",
            "mode": "cors",
            "credentials": "include",
        }

        
        
        for game in team_events:
            response = requests.get('https://www.sofascore.com/api/v1/event/' +str(game['id'])+'/shotmap', headers = headers )
            for index, entry in enumerate(response.json().get("shotmap", [])):
                if index == 0 and file_created == False:
                    csv_writer.writerow(["Round", "Match", "Result", "Player", "Id","Position","Jersey No", "xG", "xGOT", "ShotType", "GoalType", "Situation",
                                         "BodyPart", "goalMouthLocation","Time", "Overtime"])  # Kopfzeile
                    file_created = True
                if entry["isHome"] == team["homeTeam"]:

                    data_row = [
                    round,
                    game["match"],
                    game["result"],
                    entry["player"]["shortName"],
                    entry["player"]["id"],
                    entry["player"]["position"],
                    entry["player"].get("jerseyNumber", "-"),
                    entry.get("xg", "-"),
                    entry.get("xgot", "-"),
                    entry["shotType"],
                    entry.get("goalType", "-"),
                    entry["situation"],
                    entry["bodyPart"],
                    entry["goalMouthLocation"],
                    entry["time"],
                    entry.get("addedTime", "0")
                    ]
                    csv_writer.writerow(data_row)

    if  file_created == True:
        print(f"CSV-Datei '{csv_filename}' wurde erfolgreich erstellt!")


