import pandas as pd
import numpy as np
from scipy.stats import poisson

print("\nFilename Pattern: xG_team_per_match_csv/xG_matches_{Team-Id}.csv")
filename = input("\nFilename: ")

try:
    # CSV einlesen und Komma in Punkt umwandeln
    df = pd.read_csv(filename, delimiter=",", quotechar='"',
                     converters={"xG": lambda x: float(x.replace(",", ".")) if x else 0.0,
                                 "xGA": lambda x: float(x.replace(",", ".")) if x else 0.0})

    if df.empty:
        print("Die Datei wurde gelesen, aber sie ist leer.")
    else:
        print("Die Datei wurde erfolgreich geöffnet.")
        print(df.head())  # Optional: erste Zeilen ausgeben
except FileNotFoundError:
    print(f"Die Datei '{filename}' wurde nicht gefunden.")
    exit()
except pd.errors.EmptyDataError:
    print(f"Die Datei '{filename}' ist leer oder enthält keine Daten.")
    exit()
except pd.errors.ParserError:
    print(f"Die Datei '{filename}' konnte nicht korrekt geparst werden.")
    exit()
except Exception as e:
    print(f"Ein unbekannter Fehler ist aufgetreten: {e}")
    exit()

# Funktion zur Berechnung von xPoints, WinProb, DrawProb, LossProb mit Korrektur
def calculate_xPoints(xG, xGA):
    max_goals = 10  # Bis zu 10 Tore pro Team berücksichtigen
    prob_matrix = np.zeros((max_goals, max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            prob_matrix[i, j] = poisson.pmf(i, xG) * poisson.pmf(j, xGA)

    win_prob = np.sum(np.tril(prob_matrix, -1))  # Eigene Tore > Gegner-Tore
    draw_prob = np.sum(np.diag(prob_matrix))     # Eigene Tore = Gegner-Tore
    loss_prob = np.sum(np.triu(prob_matrix, 1))  # Eigene Tore < Gegner-Tore

    xPoints = 3 * win_prob + 1 * draw_prob

    # Rundung auf 2 Dezimalstellen
    win_prob = np.around(win_prob, 2)
    draw_prob = np.around(draw_prob, 2)
    loss_prob = np.around(loss_prob, 2)

    # Korrektur: Summe muss genau 1.0 sein
    total = win_prob + draw_prob + loss_prob
    if total != 1.0:
        diff = round(1.0 - total, 2)  # Berechne Differenz
        max_prob = max(win_prob, draw_prob, loss_prob)  # Die größte Zahl korrigieren
        if max_prob == win_prob:
            win_prob += diff
        elif max_prob == draw_prob:
            draw_prob += diff
        else:
            loss_prob += diff

    # Die xPoints ebenfalls auf 2 Dezimalstellen runden
    xPoints = np.around(xPoints, 2)
    win_prob = np.around(win_prob, 2)
    draw_prob = np.around(draw_prob, 2)
    loss_prob = np.around(loss_prob, 2)

    return xPoints, win_prob, draw_prob, loss_prob

# Berechnungen durchführen und in DataFrame speichern
df[["xPoints", "WinProb", "DrawProb", "LossProb"]] = df.apply(
    lambda row: pd.Series(calculate_xPoints(row["xG"], row["xGA"])), axis=1
)

# Speichern der aktualisierten CSV-Datei
df.to_csv(filename, index=False)

print("Berechnung abgeschlossen! Die Datei wurde aktualisiert.")
