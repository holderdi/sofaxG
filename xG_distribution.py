import pandas as pd
import matplotlib.pyplot as plt

print("\r\n")
print("Filename Pattern: xG_shots_players_per_team_csv/1_to_19_{TEAM-Id}_xG.csv")

# Dateien einlesen
filename1 = input("\nFilename 1: ")
filename2 = input("Filename 2: ")
filename3 = input("Filename 3: ")  # Dritte Datei

# Option wählen: Prozentwerte, absolute Werte oder beides
print("\nOptionen für die Anzeige über den Säulen:")
print("1: Prozentwerte")
print("2: Absolute Werte")
print("3: Beide (Prozent und absolut)")
option = input("Wählen Sie eine Option (1/2/3): ")

try:
    # Funktion zur Verarbeitung der xG-Werte in einer Datei
    def process_xg(filename):
        df = pd.read_csv(filename)
        if 'xG' in df.columns:
            df['xG'] = pd.to_numeric(df['xG'], errors='coerce')
            df = df.dropna(subset=['xG'])
            bins = [i / 5 for i in range(6)]  # Intervalle: 0.0 - 1.0
            df['xG_bins'] = pd.cut(df['xG'], bins=bins, include_lowest=True)
            return df['xG_bins'].value_counts().sort_index()
        else:
            print(f"Die Spalte 'xG' existiert nicht in der Datei {filename}.")
            return None

    # Verteilung der xG-Werte für alle Dateien berechnen
    xg_dist1 = process_xg(filename1)
    xg_dist2 = process_xg(filename2)
    xg_dist3 = process_xg(filename3)  # Dritte Datei

    if xg_dist1 is not None and xg_dist2 is not None and xg_dist3 is not None:
        # Prozentsätze berechnen
        total1 = xg_dist1.sum()
        total2 = xg_dist2.sum()
        total3 = xg_dist3.sum()
        xg_percent1 = (xg_dist1 / total1 * 100).round(2)
        xg_percent2 = (xg_dist2 / total2 * 100).round(2)
        xg_percent3 = (xg_dist3 / total3 * 100).round(2)

        # Balkendiagramm erstellen
        fig, ax = plt.subplots(figsize=(12, 6))
        width = 0.3  # Breite der Balken
        x = range(len(xg_dist1))  # Positionen der xG-Intervalle

        # Balken für Datei 1
        bars1 = ax.bar(
            [i - width for i in x],
            xg_dist1,
            width,
            label=f"Datei 1: {filename1}",
            color="darkblue",
            edgecolor="black",
        )

        # Balken für Datei 2
        bars2 = ax.bar(
            x,
            xg_dist2,
            width,
            label=f"Datei 2: {filename2}",
            color="red",
            edgecolor="black",
        )

        # Balken für Datei 3
        bars3 = ax.bar(
            [i + width for i in x],
            xg_dist3,
            width,
            label=f"Datei 3: {filename3}",
            color="yellow",  # Farbe für dritte Datei
            edgecolor="black",
        )

        # Werte (Prozent, absolut oder beide) über den Säulen anzeigen
        def annotate_bars(bars, values_abs, values_pct):
            for bar, abs_val, pct_val in zip(bars, values_abs, values_pct):
                height = bar.get_height()
                if option == "1":  # Prozentwerte
                    ax.text(bar.get_x() + bar.get_width() / 2, height, f"{pct_val}%", ha="center", va="bottom", fontsize=9)
                elif option == "2":  # Absolute Werte
                    ax.text(bar.get_x() + bar.get_width() / 2, height, f"{abs_val}", ha="center", va="bottom", fontsize=9)
                elif option == "3":  # Beide
                    ax.text(bar.get_x() + bar.get_width() / 2, height, f"{abs_val} ({pct_val}%)", ha="center", va="bottom", fontsize=9)

        annotate_bars(bars1, xg_dist1, xg_percent1)
        annotate_bars(bars2, xg_dist2, xg_percent2)
        annotate_bars(bars3, xg_dist3, xg_percent3)

        # Diagramm anpassen
        ax.set_title("Vergleich der xG-Verteilungen zwischen drei Dateien", fontsize=14)
        ax.set_xlabel("xG-Intervalle", fontsize=12)
        ax.set_ylabel("Anzahl", fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(xg_dist1.index.astype(str), rotation=45)
        ax.legend()
        plt.tight_layout()
        plt.show()

    else:
        print("Die Verarbeitung der Dateien war nicht erfolgreich.")
except FileNotFoundError as e:
    print(f"Die Datei wurde nicht gefunden: {e}")
except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
