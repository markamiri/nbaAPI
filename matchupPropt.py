from pprint import pprint
from nba_api.stats.endpoints import leaguegamelog
import pandas as pd

#works for spread, totals, game total props (not team total)

# Define the target date
search_date = "2025-02-12"

# Fetch all NBA games from the 2024-25 season
game_log = leaguegamelog.LeagueGameLog(season="2024-25", league_id="00")

# Convert response to a DataFrame
games = game_log.get_data_frames()[0]

# 🔹 Step 1: Filter games by the GAME_DATE column
games_on_date = games[games["GAME_DATE"] == search_date]

# 🔹 Step 2: Find the GAME_ID for Charlotte Hornets
hornets_game = games_on_date[games_on_date["TEAM_NAME"] == "Charlotte Hornets"]

if not hornets_game.empty:
    hornets_game_id = hornets_game.iloc[0]["GAME_ID"]  # Get the first match if multiple
    print(f"Charlotte Hornets GAME_ID on {search_date}: {hornets_game_id}")

    # 🔹 Step 3: Use the extracted GAME_ID to filter the games
    filtered_games = games_on_date[games_on_date["GAME_ID"] == hornets_game_id]

    # Convert DataFrame to dictionary format and print only filtered games
    games_dict = filtered_games.to_dict(orient="records")
    pprint(games_dict)
else:
    print(f"No game found for Charlotte Hornets on {search_date}.")
