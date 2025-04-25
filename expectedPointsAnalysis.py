import pandas as pd
import numpy as np
import plotly.graph_objects as go

# CSV-Datei einlesen
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

# Summen berechnen
total_points = df["Points"].sum()
total_xpoints = df["xPoints"].sum()

# Durchschnittswerte berechnen
avg_points = df["Points"].mean()
avg_xpoints = df["xPoints"].mean()

# Trendlinie für xPoints berechnen
z_xg = np.polyfit(df["Matchday"], df["xPoints"], 1)
p_xg = np.poly1d(z_xg)

# Trendlinie für Points berechnen
z_points = np.polyfit(df["Matchday"], df["Points"], 1)
p_points = np.poly1d(z_points)

# Interaktives Diagramm erstellen
fig = go.Figure()

# Punkte hinzufügen
fig.add_trace(go.Scatter(x=df["Matchday"], y=df["Points"], mode='lines+markers', name='Points', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=df["Matchday"], y=df["xPoints"], mode='lines+markers', name='xPoints', line=dict(color='red', dash='dash')))

# Trendlinien hinzufügen
fig.add_trace(go.Scatter(x=df["Matchday"], y=p_xg(df["Matchday"]), mode='lines', name='Trendlinie xPoints', line=dict(color='green', dash='dash')))
fig.add_trace(go.Scatter(x=df["Matchday"], y=p_points(df["Matchday"]), mode='lines', name='Trendlinie Points', line=dict(color='orange', dash='dash')))

# Achsenbeschriftung und Titel
fig.update_layout(
    title="Vergleich von Points und xPoints mit Trendlinien",
    xaxis_title="Matchday",
    yaxis_title="Points",
    legend_title=f"Legende<br>Gesamte Punkte: {total_points}<br>Gesamte xPoints: {total_xpoints}<br>Durchschnittliche Punkte pro Spiel: {avg_points:.2f}<br>Durchschnittliche xPoints pro Spiel: {avg_xpoints:.2f}",
    hovermode="x unified"
)

# Summen und Durchschnittswerte ausgeben
print(f"Gesamte Punkte: {total_points}, Gesamte xPoints: {total_xpoints}")
print(f"Durchschnittliche Punkte pro Spiel: {avg_points:.2f}, Durchschnittliche xPoints pro Spiel: {avg_xpoints:.2f}")

# Diagramm anzeigen
fig.show()
