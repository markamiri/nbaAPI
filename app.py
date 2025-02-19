from nba_api.stats.static import teams
from nba_api.stats.endpoints import LeagueGameFinder
import pandas as pd

# Get all NBA teams
nba_teams = teams.get_teams()

# Extract team abbreviations
abrev = [team["abbreviation"] for team in nba_teams]

# Fetch all games for the 2024-25 season
game_finder = LeagueGameFinder(season_nullable="2024-25")
games_df = game_finder.get_data_frames()[0]  # Convert response to a DataFrame

# Filter games where BOTH teams are in the abbreviation list
filtered_games = games_df[
    (games_df["TEAM_ABBREVIATION"].isin(abrev)) & 
    (games_df["MATCHUP"].apply(lambda x: any(team in x for team in abrev)))
]

# Display first 10 rows in console
print(filtered_games.head(10))

# Optional: Save the filtered data to a CSV file
filtered_games.to_csv("filtered_nba_games.csv", index=False)
print("Filtered games saved to 'filtered_nba_games.csv'")
