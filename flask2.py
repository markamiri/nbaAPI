from flask import Flask, jsonify, request
from nba_api.stats.endpoints import leaguegamelog
import requests

app = Flask(__name__)

# Proxy settings
PROXY_URL = "http://rp.scrapegw.com:6060"
PROXY_USER = "hxz9qgkiv1ihrxp-country-us"
PROXY_PASS = "t6bbs2ddwi3qq8g"

# Function to create a proxy session
def get_proxy_session():
    session = requests.Session()
    session.proxies = {
        "http": f"http://{PROXY_USER}:{PROXY_PASS}@rp.scrapegw.com:6060",
        "https": f"https://{PROXY_USER}:{PROXY_PASS}@rp.scrapegw.com:6060",
    }
    return session

# Inject session into nba_api
def fetch_nba_data_with_proxy():
    from nba_api.stats.library.http import NBAStatsHTTP

    proxy_session = get_proxy_session()

    class ProxyNBAStatsHTTP(NBAStatsHTTP):
        def send_request(self, *args, **kwargs):
            kwargs["session"] = proxy_session
            return super().send_request(*args, **kwargs)

    NBAStatsHTTP.send_request = ProxyNBAStatsHTTP.send_request

# Apply proxy configuration globally
fetch_nba_data_with_proxy()

@app.route('/api/game_id', methods=['GET'])
def get_game_id():
    game_date = request.args.get('game_date')
    team_name = request.args.get('team_name')

    if not game_date or not team_name:
        return jsonify({"error": "Missing required parameters: game_date and team_name"}), 400

    try:
        # Fetch NBA game logs with proxy
        game_log = leaguegamelog.LeagueGameLog(season="2024-25", league_id="00")
        games = game_log.get_data_frames()[0]

        # Filter games
        filtered_games = games[
            (games["GAME_DATE"].str.strip() == game_date.strip()) &
            (games["TEAM_NAME"].str.strip().str.lower() == team_name.strip().lower())
        ]

        if filtered_games.empty:
            return jsonify({"message": f"No game found for {team_name} on {game_date}"}), 404

        game_id = filtered_games.iloc[0]["GAME_ID"]
        return jsonify({"date": game_date, "team": team_name, "game_id": game_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/test_connection', methods=['GET'])
def test_connection():
    try:
        response = requests.get("https://stats.nba.com", timeout=10)
        return jsonify({"status": "Success", "content": response.text[:200]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/test_proxy', methods=['GET'])
def test_proxy():
    try:
        proxy_url = "http://hxz9qgkiv1ihrxp-country-us:t6bbs2ddwi3qq8g@rp.scrapegw.com:6060"
        response = requests.get(
            "https://stats.nba.com",
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=10
        )
        return jsonify({"status": "Proxy Working", "content": response.text[:200]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/test_google', methods=['GET'])
def test_google():
    try:
        response = requests.get("https://www.google.com", timeout=10)
        return jsonify({"status": "Success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)