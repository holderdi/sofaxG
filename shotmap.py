import requests
import csv

class ShotmapExtractor:
    def __init__(self, team_id, start_round, end_round):
        self.team_id = team_id
        self.start_round = start_round
        self.end_round = end_round
        self.csv_filename = f"{start_round}_to_{end_round}_{team_id}_xG.csv"
        self.file_created = False

    def fetch_matches(self, round):
        url = f"https://www.sofascore.com/api/v1/unique-tournament/491/season/63786/events/round/{round}"
        headers = {
            'accept': '*/*',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.sofascore.com/de/turnier/fussball/germany/3-liga/491',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('events', [])

    def fetch_shotmap(self, match_id):
        url = f"https://www.sofascore.com/api/v1/event/{match_id}/shotmap"
        headers = {
            'accept': '*/*',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.sofascore.com/de/turnier/fussball/germany/3-liga/491',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('shotmap', [])

    def process_matches(self):
        with open(self.csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)

            for round in range(self.start_round, self.end_round + 1):
                matches = self.fetch_matches(round)

                for event in matches:
                    if event["homeTeam"]["nameCode"] == self.team_id or event["awayTeam"]["nameCode"] == self.team_id:
                        is_home = event["homeTeam"]["nameCode"] == self.team_id

                        team_event = {
                            "homeTeam": is_home,
                            "id": event["id"],
                            "match": f"{event['homeTeam']['name']} : {event['awayTeam']['name']}",
                            "result": f"{event['homeScore']['current']} : {event['awayScore']['current']}",
                        }

                        shotmap = self.fetch_shotmap(team_event["id"])

                        for index, entry in enumerate(shotmap):
                            if index == 0 and not self.file_created:
                                csv_writer.writerow([
                                    "Round", "Match", "Result", "Player", "Id", "Position", "Jersey No", "xG", "xGOT", "ShotType", 
                                    "GoalType", "Situation", "BodyPart", "goalMouthLocation", "Time", "Overtime"
                                ])
                                self.file_created = True

                            if entry["isHome"] == team_event["homeTeam"]:
                                data_row = [
                                    round,
                                    team_event["match"],
                                    team_event["result"],
                                    entry["player"]["shortName"],
                                    entry["player"]["id"],
                                    entry["player"].get("position", "-"),
                                    entry["player"].get("jerseyNumber", "-"),
                                    entry["xg"],
                                    entry.get("xgot", "-"),
                                    entry["shotType"],
                                    entry.get("goalType", "-"),
                                    entry["situation"],
                                    entry["bodyPart"],
                                    entry["goalMouthLocation"],
                                    entry["time"],
                                    entry.get("addedTime", "0"),
                                ]
                                csv_writer.writerow(data_row)

        if self.file_created:
            print(f"CSV file '{self.csv_filename}' has been successfully created!")

if __name__ == "__main__":
    print()
    team_id = "ARM"
    start_round = int(input("\r\nSpieltag von: "))
    end_round = int(input("\r\nSpieltag bis: "))

    extractor = ShotmapExtractor(team_id, start_round, end_round)
    extractor.process_matches()
