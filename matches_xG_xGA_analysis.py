import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

print("\r\n")
print("Filename Pattern: xG_team_per_match_csv/xG_matches_{Team-Id}.csv")
filename = input("\r\nFilename: ")

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

# Differenzen berechnen
df["xG-Diff"] = df["xG"] - df["xGA"]
df["Goal-Diff"] = df["Goals"] - df["aGoals"]

# Loess-Glättung berechnen
xg_smooth = lowess(df["xG-Diff"], df["Matchday"], frac=0.3)[:, 1]
goal_smooth = lowess(df["Goal-Diff"], df["Matchday"], frac=0.3)[:, 1]

# Regressionsgerade für xG-Diff berechnen
z_xg_diff = np.polyfit(df["Matchday"], df["xG-Diff"], 1)
p_xg_diff = np.poly1d(z_xg_diff)

# Regressionsgerade für Goal-Diff berechnen
z_goal_diff = np.polyfit(df["Matchday"], df["Goal-Diff"], 1)
p_goal_diff = np.poly1d(z_goal_diff)

# Interaktives Diagramm erstellen
fig = go.Figure()

# Datenpunkte hinzufügen
fig.add_trace(go.Scatter(x=df["Matchday"], y=df["xG-Diff"], mode='lines+markers', name='xG-Diff', line=dict(color='red')))
fig.add_trace(go.Scatter(x=df["Matchday"], y=df["Goal-Diff"], mode='lines+markers', name='Goal-Diff', line=dict(color='blue')))

# Glättungslinien hinzufügen
fig.add_trace(go.Scatter(x=df["Matchday"], y=xg_smooth, mode='lines', name='xG-Diff Trend', line=dict(color='red', dash='dash')))
fig.add_trace(go.Scatter(x=df["Matchday"], y=goal_smooth, mode='lines', name='Goal-Diff Trend', line=dict(color='blue', dash='dash')))

# Regressionsgeraden hinzufügen
fig.add_trace(go.Scatter(x=df["Matchday"], y=p_xg_diff(df["Matchday"]), mode='lines', name='xG-Diff Regressionsgerade', line=dict(color='red', dash='dot')))
fig.add_trace(go.Scatter(x=df["Matchday"], y=p_goal_diff(df["Matchday"]), mode='lines', name='Goal-Diff Regressionsgerade', line=dict(color='blue', dash='dot')))

# Achsenbeschriftung und Titel
fig.update_layout(
    title="Spielstatistiken: xG-Diff und Goal-Diff pro Spieltag",
    xaxis_title="Matchday",
    yaxis_title="Differenz-Werte",
    legend_title="Legende",
    hovermode="x unified"
)

# Diagramm anzeigen
fig.show()
