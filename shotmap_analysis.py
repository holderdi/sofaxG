import pandas as pd
import requests
print("\r\n")
print("Filename Pattern: xG_shots_players_per_team_csv/1_to_19_{TEAM-Id}_xG.csv")
filename = input("\r\nFilename: ")
team_id = input("\r\nTeam ID: ")
# CSV-Daten einlesen

try:
    # Datei lesen
    df = pd.read_csv(filename)

    # Prüfen, ob die Datei erfolgreich gelesen wurde und nicht leer ist
    if df.empty:
        print("Die Datei wurde gelesen, aber sie ist leer.")
    else:
        print("Die Datei wurde erfolgreich geöffnet.")
        print(df.head())  # Optionale Ausgabe der ersten Zeilen
except FileNotFoundError:
    print(f"Die Datei '{filename}' wurde nicht gefunden.")
except pd.errors.EmptyDataError:
    print(f"Die Datei '{filename}' ist leer oder enthält keine Daten.")
except pd.errors.ParserError:
    print(f"Die Datei '{filename}' konnte nicht korrekt geparst werden.")
except Exception as e:
    print(f"Ein unbekannter Fehler ist aufgetreten: {e}")

# Get Rounds ( some match datasets are missing )    
num_rounds = df['Round'].nunique()

# Mapping-Tabelle für die Positionen
position_mapping = {
    'F': 'Forward',
    'D': 'Defense',
    'M': 'Midfield',
    'G': 'Goalkeeper',
}

# Positionen umwandeln, bevor sie in das DataFrame übernommen werden
df['Position'] = df['Position'].replace(position_mapping)

# Extract unique Id and Player combinations
unique_players = df[['Id', 'Player']].drop_duplicates()
player_minutes = {}
player_appearances = {}
player_ratings = {}
for player_id in unique_players['Id']:
    url = f"https://www.sofascore.com/api/v1/player/{player_id}/unique-tournament/491/season/63786/statistics/overall"
    headers = {
        'accept': '*/*',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'baggage': 'sentry-environment=production,sentry-release=kMNOA57YkxQRF4Hf4Ooaf,sentry-public_key=d693747a6bb242d9bb9cf7069fb57988,sentry-trace_id=56017ed4ffd74ad0a1d9e0648571edc5',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'sec-ch-ua': '\'Chromium\';v=\'130\', \'Google Chrome\';v=\'130\', \'Not?A_Brand\';v=\'99\'',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '\'Windows\'',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sentry-trace': '56017ed4ffd74ad0a1d9e0648571edc5-b093258cc946887f',
        'x-requested-with': '54f943'
    }
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        try:
            minutes = response.json()['statistics']['minutesPlayed']
            player_minutes[player_id] = minutes
            appearances = response.json()['statistics']['appearances']
            player_appearances[player_id] = appearances
            rating = response.json()['statistics']['rating']
            player_ratings[player_id] = round(rating, 2)
        except KeyError:
            player_minutes[player_id] = 0
            player_appearances[player_id] = 0
            player_ratings[player_id] = 0
    else:
        player_minutes[player_id] = 0
        player_appearances[player_id] = 0
        player_ratings[player_id] = 0

# Add minutes played and appearances to the DataFrame
unique_players['MinutesPlayed'] = unique_players['Id'].map(player_minutes)
max_minutes = df['Round'].nunique() * 90
unique_players['Appearances'] = unique_players['Id'].map(player_appearances)
unique_players['Rating'] = unique_players['Id'].map(player_ratings)

# Zeilen mit 'penalty' ausschließen, bevor die xG kumuliert werden
df_no_penalty = df[df['GoalType'] != 'penalty'].copy()

# Spalte 'xGOT' fehlende Werte durch NaN ersetzen, um Berechnungen zu ermöglichen
df_no_penalty['xGOT'] = pd.to_numeric(df['xGOT'], errors='coerce')  # Konvertiert '-' zu NaN 
df_no_penalty['xG'] = pd.to_numeric(df['xG'], errors='coerce')  # Konvertiert '-' zu NaN

# Cumulative values all data sets
xg_cum_all = df_no_penalty['xG'].sum().round(2)
xgot_cum_all = df_no_penalty['xGOT'].sum().round(2)
shots_all = len(df_no_penalty)
# Count shots on target 
shots_on_target_all = int(df_no_penalty["xGOT"].notna().sum())

# xG kumuliert pro Spieler ohne Elfmeter (nur reguläre Tore und andere Schüsse)
xg_cumulative = df_no_penalty.groupby('Player')['xG'].sum().round(2)
# xGoT kumuliert pro Spieler ohne Elfmeter
xgot_cumulative = df_no_penalty.groupby('Player')['xGOT'].sum().round(2)

# Add xG per 90 minutes
unique_players['xG_per_90'] = unique_players.apply(
    lambda row: (xg_cumulative.get(row['Player'], 0) / row['MinutesPlayed'] * 90) if row['MinutesPlayed'] > 0 else 0,
    axis=1
).round(2)
# Add xGOT per 90 minutes
unique_players['xGOT_per_90'] = unique_players.apply(
    lambda row: (xgot_cumulative.get(row['Player'], 0) / row['MinutesPlayed'] * 90) if row['MinutesPlayed'] > 0 else 0,
    axis=1
).round(2)

if unique_players['Player'].duplicated().any():
    unique_players.drop_duplicates(subset='Player')

# Anzahl der Schüsse pro Spieler ermitteln
shots_per_player = df_no_penalty.groupby('Player').size()

# Tore pro Spieler ermitteln, basierend auf ShotType == 'goal'
goals_cumulative = df_no_penalty[df_no_penalty['ShotType'] == 'goal'].groupby('Player').size()
# Erstelle einen vollständigen Index der Spieler
all_players = df_no_penalty['Player'].unique()

# Reindexiere die Tore-Serie, sodass auch Spieler ohne Tore erfasst werden (und mit 0 aufgefüllt werden)
goals_cumulative = goals_cumulative.reindex(all_players).fillna(0)
goals_cumulative = goals_cumulative.astype('Int64')

goals_sum = goals_cumulative.sum()


xg_per_shot = df_no_penalty.groupby('Player')['xG'].mean().round(2)

# Filtern der Zeilen, bei denen 'xGOT' ein gültiger Zahlenwert ist

shots_on_target_per_player = df_no_penalty[df_no_penalty['xGOT'].notna()].groupby('Player').size()
shots_on_target_per_player = shots_on_target_per_player.reindex(all_players).fillna(0)
shots_on_target_per_player = shots_on_target_per_player.astype('Int64')

# Position des Spielers hinzufügen
positions = df_no_penalty.groupby('Player')['Position'].first()

# Ergebnisse in einem neuen DataFrame zusammenfassen
results = pd.DataFrame({
   # 'Player': df_no_penalty['Player'],
    'Position': positions,
    'xG_cum': xg_cumulative,
    'xG_per_90': unique_players.set_index('Player')['xG_per_90'],
    'xG_per_Shot': xg_per_shot,
    'xGOT_cum': xgot_cumulative,
    'xGOT_per_90': unique_players.set_index('Player')['xGOT_per_90'],
    'Shots': shots_per_player,
    'Shots_oT': shots_on_target_per_player,
    '%_oT': (shots_on_target_per_player / shots_per_player * 100).round(0),
    'Goals': goals_cumulative,
    'Minutes': unique_players.set_index('Player')['MinutesPlayed'],
    'Appearances': unique_players.set_index('Player')['Appearances'],
    'Rating': unique_players.set_index('Player')['Rating']
})
# Add percentage of minutes played
results['Minutes_%'] = (results['Minutes'] / max_minutes * 100).round(0)
results['xGOT_per_Shot'] = results.apply(
    lambda row: round(row['xGOT_cum'] / row['Shots_oT'], 2)
    if row['Shots_oT'] > 0 else 0,
    axis=1
)

# Reihenfolge der Positionen festlegen
position_order = ['Defense', 'Midfield', 'Forward']
results['Position'] = pd.Categorical(results['Position'], categories=position_order, ordered=True)

desired_order = ['Position', 'xG_cum', 'xG_per_90', 'xG_per_Shot', 'xGOT_cum','xGOT_per_90', 
                 'xGOT_per_Shot','Shots', 'Shots_oT', '%_oT', 'Goals', 'Minutes', 'Minutes_%', 'Appearances', 'Rating']

results = results[desired_order]

# Nach xG_kumuliert absteigend sortieren
results_sorted = results.sort_values(by=['Position','xG_cum'], ascending=[True,False])
# Overall values
results_all = pd.Series({
    'Rounds': num_rounds,
    'xG_cum': xg_cum_all,
    'xG per Game': pd.Series(xg_cum_all / num_rounds).round(2).iloc[0],
    'xGOT_cum': xgot_cum_all,
    'xGOT per Game': (xgot_cum_all / num_rounds).round(2),
    'Shots': shots_all,
    'Shots per Game': pd.Series(shots_all / num_rounds).round(2).iloc[0],
    'Shots_on_target': shots_on_target_all,
    'SoT per game': pd.Series(shots_on_target_all / num_rounds).round(2).iloc[0],
    'Goals': goals_sum,
    'Goals per Game': pd.Series(goals_sum / num_rounds).round(2).iloc[0]
},dtype=object)
# Ausgabe
print("\nOverall:")
print(results_all.to_string())

# Als CSV speichern
results_all.to_csv(f"xG_team_results/{team_id}_xG_overall.csv", header=False, sep=',')
# Ergebnisse in HTML speichern
results_sorted.to_html(f"xG_team_results/{team_id}_xG_overall.html", index=True, border=1)


# Ausgabe
print("\nResults per Player:")
print(results_sorted)

# Als CSV speichern
results_sorted.to_csv(f"xG_players_per_team_results/{team_id}_players_shots.csv", index=True, sep=',')
# Als TXT speichern
results_sorted.to_csv(f"xG_players_per_team_results/{team_id}_players_shots.txt", index=True, sep='\t')
# HTML-Tabelle
# Ergebnisse in HTML speichern
results_sorted.to_html(f"xG_players_per_team_results/{team_id}_players_shots.html", index=True, border=1)




