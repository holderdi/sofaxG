import random
from collections import defaultdict

# Aktuelle Punkte
initial_points = {
    "Dresden": 63,
    "Bielefeld": 62,
    "Cottbus": 58,
    "Saarbrücken": 56,
    "Ingolstadt": 51,
    "Rostock": 51,
    "1860 München": 0,
    "Sandhausen": 0,
    "Aue": 0,
    "Unterhaching": 0,
    "Essen": 0,
    "Aachen": 0,
    "Verl": 0,
    "Waldhof": 0,
    "Hannover II": 0,
    "BVB II": 0,
    "Viktoria Köln": 0,
    "Stuttgart II": 0,
    "Osnabrück": 0,
    "Wiesbaden": 0
}

# Alle Spiele im Restprogramm, Top 6-Teams
remaining_fixtures = [
    # Spieltag 35
    ("Rostock", "1860 München"),
    ("Ingolstadt", "Bielefeld"),#
    ("Dresden", "Sandhausen"),
    ("Unterhaching", "Cottbus"),
    ("Essen", "Saarbrücken"),

    # Spieltag 36
    ("Saarbrücken", "Verl"),
    ("Bielefeld", "Dresden"),#
    ("Cottbus", "Waldhof"),
    ("Sandhausen", "Rostock"),
    ("Aue", "Ingolstadt"),

     # Spieltag 37 
    ("Aachen", "Saarbrücken"),
    ("Rostock", "Cottbus"),#
    ("Waldhof", "Dresden"),
    ("Ingolstadt", "Wiesbaden"),
    ("Unterhaching", "Bielefeld"),
    # Spieltag 38
    ("Dresden", "Unterhaching"), 
    ("Cottbus", "Ingolstadt"), #
    ("Bielefeld", "Waldhof"),
    ("Hannover II", "Rostock"),
    ("Saarbrücken", "BVB II"),
]

# Feste Arminia-Ergebnisse (anpassen!)
arminia_results = {
    "Ingolstadt": "draw",
    "Dresden": "draw",
    "Unterhaching": "draw",
    "Waldhof": "draw",
}

# Ergebnis → Punkte
result_points = {
    "win": (3, 0),
    "draw": (1, 1),
    "loss": (0, 3),
}

def apply_fixed_arminia_results(points):
    for opponent, result in arminia_results.items():
        pts1, pts2 = result_points[result]
        points["Bielefeld"] += pts1
        if opponent in points:
            points[opponent] += pts2
    return points

def simulate_remaining_games(points, fixtures, samples=100000):
    promotion_count = 0

    for _ in range(samples):
        sim_points = points.copy()

        for home, away in fixtures:
            if home == "Bielefeld" or away == "Bielefeld":
                continue  # Arminia-Spiele sind festgelegt

            outcome = random.choice(["home", "draw", "away"])
            if outcome == "home":
                sim_points[home] += 3
            elif outcome == "draw":
                sim_points[home] += 1
                sim_points[away] += 1
            else:
                sim_points[away] += 3

        sorted_teams = sorted(sim_points.items(), key=lambda x: (-x[1], x[0]))
        for rank, (team, _) in enumerate(sorted_teams[:2], 1):
            if team == "Bielefeld":
                promotion_count += 1
                break

    return promotion_count / samples

def main():
    print("Berechne Aufstiegschance für Arminia mit festen Ergebnissen:")
    for match, result in arminia_results.items():
        print(f"- gegen {match}: {result}")

    base_points = initial_points.copy()
    base_points = apply_fixed_arminia_results(base_points)

    probability = simulate_remaining_games(base_points, remaining_fixtures)
    print(f"\n📈 Aufstiegschance: {probability*100:.2f} %")

if __name__ == "__main__":
    main()
