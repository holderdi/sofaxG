import pandas as pd
import matplotlib.pyplot as plt

# Function to calculate the distribution of goals by time intervals
def calculate_goal_distribution(filename):
    try:
        # Load the CSV file
        df = pd.read_csv(filename)

        # Filter only the entries with ShotType = "goal"
        goals = df[df['ShotType'] == 'goal'].copy()  # `.copy()` erstellt eine explizite Kopie des DataFrame

        # Add a new column for game time quarters (1st Quarter: 0-22, 2nd Quarter: 23-45, etc.)
        goals.loc[:, 'Quarter'] = pd.cut(
            goals['Time'],
            bins=[0, 22, 45, 67, 90],
            labels=['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter'],
            right=True
        )

        # Convert 'Quarter' to a category with an additional category for 'Overtime'
        goals['Quarter'] = goals['Quarter'].cat.add_categories(['Overtime'])

        # Goals in overtime (Overtime > 0) are placed in the 'Overtime' category
        goals.loc[:, 'Quarter'] = goals.apply(
            lambda row: 'Overtime' if row['Overtime'] > 0 else row['Quarter'], axis=1
        )

        # Calculate the distribution
        goal_distribution = goals['Quarter'].value_counts().sort_index()

        return goal_distribution
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while processing the file '{filename}': {e}")
        return None


# Function to process multiple files
def process_files(filenames):
    distributions = []
    for filename in filenames:
        if filename:
            distribution = calculate_goal_distribution(filename)
            if distribution is not None:
                distributions.append(distribution)
    return distributions

# Main script
print("\r\nLoad 1 to 3 files. Enter the filenames (leave empty if no additional file):\r\n")
filenames = [
    input("File 1: ").strip(),
    input("File 2: ").strip(),
    input("File 3: ").strip()
]

# Calculate distributions for all files
goal_distributions = process_files(filenames)

# Create the chart if data is available
if goal_distributions:
    # Collect all categories
    all_categories = sorted(set(cat for dist in goal_distributions for cat in dist.index))

    # Prepare data for the chart
    percentages = []
    absolute_values = []
    for dist in goal_distributions:
        total_goals = dist.sum()
        percentages.append([(dist.get(cat, 0) / total_goals * 100) if total_goals > 0 else 0 for cat in all_categories])
        absolute_values.append([dist.get(cat, 0) for cat in all_categories])

    # Define custom colors for the bars
    colors = ['#005C9D', '#B22222', '#FFD700']  # Blue, deep red, yellow

    # Draw the bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    bar_width = 0.2
    x = range(len(all_categories))

    for i, (abs_vals, pct_vals) in enumerate(zip(absolute_values, percentages)):
        ax.bar(
            [pos + i * bar_width for pos in x],
            abs_vals,
            bar_width,
            label=f"File {i + 1}: {filenames[i]}",
            color=colors[i] if i < len(colors) else 'gray',  # Use gray for additional files
            edgecolor='black'
        )
        # Display values above the bars
        for j, (abs_val, pct_val) in enumerate(zip(abs_vals, pct_vals)):
            ax.text(j + i * bar_width, abs_val, f"{abs_val} ({pct_val:.1f}%)", ha='center', va='bottom', fontsize=8)

    # Chart details
    ax.set_title("Goal Distribution by Game Time Quarters", fontsize=14)
    ax.set_xlabel("Game Time Intervals", fontsize=12)
    ax.set_ylabel("Number of Goals", fontsize=12)
    ax.set_xticks([pos + bar_width for pos in x])
    ax.set_xticklabels(all_categories, rotation=45)
    ax.legend()
    plt.tight_layout()
    plt.show()
else:
    print("No valid files loaded.")
