from flask import Flask, jsonify, request
from nba_api.stats.endpoints import leaguegamelog, BoxScoreTraditionalV2
import pandas as pd

app = Flask(__name__)


# 🔹 Get GAME_ID for a specified team and date
@app.route('/api/game_id', methods=['GET'])
def get_game_id():
    # Fetch query parameters safely
    game_date = request.args.get('game_date')
    team_name = request.args.get('team_name')

    # Debugging print statements
    print(f"🔹 Received parameters - game_date: {game_date}, team_name: {team_name}")

    # Validate inputs
    if not game_date or not team_name:
        print("❌ Error: Missing game_date or team_name parameter")
        return jsonify({"error": "Missing required parameters: game_date and team_name"}), 400

    # Fetch NBA game logs
    game_log = leaguegamelog.LeagueGameLog(season="2024-25", league_id="00")
    games = game_log.get_data_frames()[0]

    # Print first few rows for debugging
    print("🔹 First 5 rows of fetched data:")
    print(games.head())

    # Ensure 'TEAM_NAME' column exists before filtering
    if "TEAM_NAME" not in games.columns or "GAME_DATE" not in games.columns:
        print("❌ Error: Missing required columns in fetched data")
        return jsonify({"error": "Required columns missing in fetched data"}), 500

    # Print unique GAME_DATE values for debugging
    print(f"🔹 Unique GAME_DATE values in dataset: {games['GAME_DATE'].unique()}")
    print(f"🔹 Unique TEAM_NAME values in dataset: {games['TEAM_NAME'].unique()}")

    # Filter games by user-provided parameters
    filtered_games = games[(games["GAME_DATE"].str.strip() == game_date.strip()) &(games["TEAM_NAME"].str.strip().str.lower() == team_name.strip().lower())]


    # Print filtered results
    print(f"🔹 Filtered games count: {len(filtered_games)}")
    if not filtered_games.empty:
        print("🔹 Filtered DataFrame:")
        print(filtered_games)

    # If no game is found, return an error
    if filtered_games.empty:
        print(f"❌ No game found for {team_name} on {game_date}")
        return jsonify({"message": f"No game found for {team_name} on {game_date}"}), 404

    # Extract GAME_ID
    game_id = filtered_games.iloc[0]["GAME_ID"]
    print(f"✅ Found GAME_ID: {game_id}")
    
    return jsonify({"date": game_date, "team": team_name, "game_id": game_id})


# Get the player prop date 
@app.route('/api/player_stats', methods=['GET'])
def get_player_stats():
    # Get query parameters
    game_date = request.args.get('game_date')
    team_name = request.args.get('team_name')

    # Validate input
    if not game_date or not team_name:
        return jsonify({"error": "Missing required parameters: game_date and team_name"}), 400

    # 🔹 Call get_game_id() function to fetch GAME_ID
    with app.test_request_context(f'/api/game_id?game_date={game_date}&team_name={team_name}'):
        response = get_game_id()
    
    # Parse the response
    if response.status_code != 200:
        return response  # If get_game_id() fails, return the same response

    game_data = response.get_json()
    game_id = game_data.get("game_id")

    if not game_id:
        return jsonify({"error": "Could not retrieve GAME_ID"}), 404

    # Fetch Player Stats using the found GAME_ID
    box_score = BoxScoreTraditionalV2(game_id=game_id)
    player_stats = box_score.get_data_frames()[0]

    return jsonify(player_stats.to_dict(orient="records"))


@app.route('/api/game_details', methods=['GET'])
def get_game_details():
    # Get query parameters
    game_date = request.args.get('game_date')
    team_name = request.args.get('team_name')

    # Validate input
    if not game_date or not team_name:
        return jsonify({"error": "Missing required parameters: game_date and team_name"}), 400

    # 🔹 Call get_game_id() function to fetch GAME_ID
    with app.test_request_context(f'/api/game_id?game_date={game_date}&team_name={team_name}'):
        response = get_game_id()
    
    # Parse the response
    if response.status_code != 200:
        return response  # If get_game_id() fails, return the same response

    game_data = response.get_json()
    game_id = game_data.get("game_id")

    if not game_id:
        return jsonify({"error": "Could not retrieve GAME_ID"}), 404

    # Fetch all NBA games for the season
    game_log = leaguegamelog.LeagueGameLog(season="2024-25", league_id="00")
    games = game_log.get_data_frames()[0]

    # Convert GAME_DATE to string
    games["GAME_DATE"] = games["GAME_DATE"].astype(str)

    # 🔹 Filter games by GAME_ID
    filtered_games = games[games["GAME_ID"] == game_id]

    # Return JSON response
    return jsonify(filtered_games.to_dict(orient="records"))



@app.route('/api/team_totals', methods=['GET'])
def get_team_totals():
    # Get query parameters
    game_date = request.args.get('game_date')
    team_name = request.args.get('team_name')

    # Validate input
    if not game_date or not team_name:
        return jsonify({"error": "Missing required parameters: game_date and team_name"}), 400

    # 🔹 Call get_game_id() function to fetch GAME_ID
    with app.test_request_context(f'/api/game_id?game_date={game_date}&team_name={team_name}'):
        response = get_game_id()
    
    # Parse the response
    if response.status_code != 200:
        return response  # If get_game_id() fails, return the same response

    game_data = response.get_json()
    game_id = game_data.get("game_id")

    if not game_id:
        return jsonify({"error": "Could not retrieve GAME_ID"}), 404

    # Fetch all NBA games for the season
    game_log = leaguegamelog.LeagueGameLog(season="2024-25", league_id="00")
    games = game_log.get_data_frames()[0]

    # Convert GAME_DATE to string
    games["GAME_DATE"] = games["GAME_DATE"].astype(str)

    # 🔹 Filter games by GAME_ID and team name
    filtered_games = games[
        (games["GAME_ID"] == game_id) & (games["TEAM_NAME"].str.strip().str.lower() == team_name.strip().lower())
    ]

    if filtered_games.empty:
        return jsonify({"message": f"No team totals found for {team_name} on {game_date}"}), 404

    # Return JSON response
    return jsonify(filtered_games.to_dict(orient="records"))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
