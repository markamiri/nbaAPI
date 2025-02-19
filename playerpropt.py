#get playpropt info /
from pprint import pprint
from nba_api.stats.endpoints import leaguegamelog
from nba_api.stats.endpoints import BoxScoreTraditionalV2

import pandas as pd

#works for player propts

# Define the target date
search_date = "2025-02-12"

# Fetch all NBA games from the 2024-25 season
game_log = leaguegamelog.LeagueGameLog(season="2024-25", league_id="00")

# Convert response to a DataFrame
games = game_log.get_data_frames()[0]

# Filter games by the GAME_DATE column
games_on_date = games[games["GAME_DATE"] == search_date]

# Convert DataFrame to dictionary format and print all games
games_dict = games_on_date.to_dict(orient="records")

# 🔹 Find the GAME_ID for Charlotte Hornets
hornets_game = games_on_date[games_on_date["TEAM_NAME"] == "Charlotte Hornets"]

# Check if the Hornets played that day
game_id = hornets_game.iloc[0]["GAME_ID"]
if not hornets_game.empty:
    hornets_game_id = hornets_game.iloc[0]["GAME_ID"]
    print(f"\nCharlotte Hornets GAME_ID on {search_date}: {hornets_game_id}")
    box_score = BoxScoreTraditionalV2(game_id=game_id)
    player_stats = box_score.get_data_frames()[0]
    player_stats_dict = player_stats.to_dict(orient="records")
    pprint(player_stats_dict)
else:
    print(f"\nNo game found for Charlotte Hornets on {search_date}.")

