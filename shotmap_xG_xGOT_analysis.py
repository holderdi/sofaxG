import pandas as pd
import sys
print("\r\n")
print("Filename Pattern: xG_shots_players_per_team_csv/1_to_19_{TEAM-Id}_xG.csv")
filename = input("\r\nFilename: ")
team_id = input("\r\nTeam ID: ")
# Read CSV data

try:
    # Read the file
    df = pd.read_csv(filename)
    # Check if the file was successfully read and is not empty
    if df.empty:
        print("The file was read, but it is empty.")
    else:
        print("The file was successfully opened.")
        print(df.head())  # Optional output of the first rows
except FileNotFoundError:
    print(f"The file '{filename}' was not found.")
    sys.exit(1) 
except pd.errors.EmptyDataError:
    print(f"The file '{filename}' is empty or contains no data.")
    sys.exit(2) 
except pd.errors.ParserError:
    print(f"The file '{filename}' could not be parsed correctly.")
    sys.exit(3) 
except Exception as e:
    print(f"An unknown error occurred: {e}")
    sys.exit(4)

# Mapping table for positions
position_mapping = {
    'F': 'Forward',
    'D': 'Defense',
    'M': 'Midfield',
    'G': 'Goalkeeper'  # Example for goalkeeper
}

# Convert positions before incorporating them into the DataFrame
df['Position'] = df['Position'].replace(position_mapping)

unique_players = df[['Id']].drop_duplicates()

# Exclude rows with 'penalty' before accumulating xG
df_no_penalty = df[df['GoalType'] != 'penalty'].copy()
# Count shots per player
shots_per_player_all = df_no_penalty.groupby('Id').size()

# Replace missing values in the 'xGOT' column with NaN to enable calculations
df_no_penalty['xGOT'] = pd.to_numeric(df['xGOT'], errors='coerce')  # Converts '-' to NaN 
df_no_penalty['xG'] = pd.to_numeric(df['xG'], errors='coerce')  # Converts '-' to NaN
df_no_penalty = df_no_penalty.dropna(subset=['xGOT'])  # Removes NaN values

# Cumulative xG per player without penalties (only regular goals and other shots)
xg_cumulative = df_no_penalty.groupby('Id')['xG'].sum().round(2)
# Cumulative xGOT per player without penalties
xgot_cumulative = df_no_penalty.groupby('Id')['xGOT'].sum().round(2)

# Determine goals per player based on ShotType == 'goal'
goals_cumulative = df_no_penalty[df_no_penalty['ShotType'] == 'goal'].groupby('Id').size()
# Create a complete index of players
all_players_nopen = df_no_penalty['Id'].unique()

# Reindex the goals series so that players without goals are included (and filled with 0)
goals_cumulative = goals_cumulative.reindex(all_players_nopen).fillna(0)
goals_cumulative = goals_cumulative.astype('Int64')

# Determine the number of shots per player
shots_per_player = df_no_penalty.groupby('Id').size()
shots_per_player = shots_per_player.reindex(all_players_nopen).fillna(0)
shots_per_player = shots_per_player.astype('Int64')

# Add player positions
positions = df_no_penalty.groupby('Id')['Position'].first()

# Summarize results in a new DataFrame
results = pd.DataFrame({
    'Player': df_no_penalty.groupby('Id')['Player'].first(),
    'Position': df_no_penalty.groupby('Id')['Position'].first(),
    'xG sum': xg_cumulative,
    'xG per shot': (xg_cumulative / shots_per_player).round(2),
    'xGOT sum': xgot_cumulative, 
    'xGOT per shot': (xgot_cumulative / shots_per_player).round(2),
    'Added Value': xgot_cumulative - xg_cumulative,
    'AdV per Shot': ((xgot_cumulative - xg_cumulative) / shots_per_player).round(2),
    'Shots': (shots_per_player),
    '% oT': (shots_per_player / shots_per_player_all * 100).round(0),
    'Goals': goals_cumulative,   
})

# Fill NaN values in '% oT' with 0 before converting to integer
results['% oT'] = results['% oT'].fillna(0).astype(int)

# Drop rows with NaN values
results = results.dropna()

# Define the order of positions
position_order = ['Defense', 'Midfield', 'Forward']
results['Position'] = pd.Categorical(results['Position'], categories=position_order, ordered=True)
# Sort by cumulative xG in descending order
results_sorted = results.sort_values(by=['Position', 'AdV per Shot'], ascending=[False, False])
# Output
print("\nResults per Player:")
print(results_sorted)

# Als CSV speichern
results_sorted.to_csv(f"xG_xGOT_players_per_team_results/{team_id}_players_shots.csv", index=True, sep=',')
# Als TXT speichern
results_sorted.to_csv(f"xG_xGOT_players_per_team_results/{team_id}_players_shots.txt", index=True, sep='\t')
# HTML-Tabelle
# Ergebnisse in HTML speichern
results_sorted.to_html(f"xG_xGOT_players_per_team_results/{team_id}_players_shots.html", index=True, border=1)



