from nba_api.stats.endpoints import leaguegamelog
import pandas as pd
from pprint import pprint

#Moneyline, team Totals propts(not game total)

# Define the target date
search_date = "2025-02-12"

# Fetch all NBA games from the 2024-25 season
game_log = leaguegamelog.LeagueGameLog(season="2024-25", league_id="00")

# Convert response to a DataFrame
games = game_log.get_data_frames()[0]

# Filter games by date and Charlotte Hornets team name
hornets_games_on_date = games[
    (games["GAME_DATE"] == search_date) & (games["TEAM_NAME"] == "Charlotte Hornets")
]

# Check if there are any games for Charlotte Hornets on the specified date
if hornets_games_on_date.empty:
    print(f"No Charlotte Hornets games found on {search_date}.")
else:
    # Display the game log for the Charlotte Hornets
    pprint(hornets_games_on_date.to_dict(orient="records"))

