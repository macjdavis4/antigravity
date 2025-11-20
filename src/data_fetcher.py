"""Fetch NFL player data from various APIs."""
import requests
from typing import Dict, List, Optional
from datetime import datetime
import config
from src.database import Database


class NFLDataFetcher:
    """Fetches NFL player statistics from public APIs."""

    def __init__(self):
        """Initialize the data fetcher."""
        self.db = Database()
        self.current_season = datetime.now().year
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_current_week(self) -> int:
        """Get the current NFL week."""
        try:
            url = f"{config.ESPN_API_BASE}/scoreboard"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('week', {}).get('number', 1)
        except Exception as e:
            print(f"Error getting current week: {e}")
            # Return approximate week based on date
            week_of_year = datetime.now().isocalendar()[1]
            # NFL season typically starts week 36-37
            return max(1, min(18, week_of_year - 35))

    def fetch_players_from_sleeper(self) -> Dict:
        """Fetch all NFL players from Sleeper API."""
        try:
            url = f"{config.SLEEPER_API_BASE}/players/nfl"
            print(f"Fetching player data from Sleeper API...")
            print(f"URL: {url}")
            response = self.session.get(url, timeout=30)
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print(f"✓ Successfully fetched {len(data)} players")
            return data
        except requests.exceptions.ProxyError as e:
            print(f"✗ Proxy/Network error: Cannot reach Sleeper API")
            print(f"  This may be due to network restrictions or firewall settings")
            print(f"  Consider using CSV import instead (see documentation)")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error fetching players: {type(e).__name__}")
            print(f"  Details: {str(e)[:100]}")
            return {}
        except Exception as e:
            print(f"✗ Unexpected error fetching players: {e}")
            return {}

    def update_player_database(self):
        """Update the local database with latest player information."""
        print("\n" + "=" * 60)
        print("UPDATING PLAYER DATABASE")
        print("=" * 60)
        players_data = self.fetch_players_from_sleeper()

        if not players_data:
            print("\n✗ No player data received from API.")
            print("  Options:")
            print("  1. Check your internet connection")
            print("  2. Try again later")
            print("  3. Use CSV import feature (Option 17 in main menu)")
            return

        count = 0
        # Filter for active NFL players only
        for player_id, player_info in players_data.items():
            if player_info.get('status') != 'Active':
                continue

            position = player_info.get('position', 'N/A')
            if position not in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
                continue

            name = f"{player_info.get('first_name', '')} {player_info.get('last_name', '')}".strip()
            if not name:
                continue

            team = player_info.get('team', 'FA')

            self.db.upsert_player(player_id, name, team, position)
            count += 1

        if count > 0:
            print(f"\n✓ Successfully updated {count} players in database.")
        else:
            print(f"\n✗ No players were added to database.")
        print("=" * 60)

    def calculate_fantasy_points(self, stats: Dict, scoring: str = "PPR") -> float:
        """Calculate fantasy points based on stats and scoring format."""
        points = 0.0

        # Passing stats
        points += stats.get('passing_yards', 0) * 0.04  # 1 point per 25 yards
        points += stats.get('passing_tds', 0) * 4
        points -= stats.get('interceptions', 0) * 2

        # Rushing stats
        points += stats.get('rushing_yards', 0) * 0.1  # 1 point per 10 yards
        points += stats.get('rushing_tds', 0) * 6

        # Receiving stats
        points += stats.get('receiving_yards', 0) * 0.1  # 1 point per 10 yards
        points += stats.get('receiving_tds', 0) * 6

        # PPR bonus
        if scoring == "PPR":
            points += stats.get('receptions', 0) * 1.0
        elif scoring == "Half-PPR":
            points += stats.get('receptions', 0) * 0.5

        # Fumbles
        points -= stats.get('fumbles', 0) * 2

        return round(points, 2)

    def fetch_player_stats_espn(self, week: int = None) -> List[Dict]:
        """Fetch player stats from ESPN for a specific week."""
        if week is None:
            week = self.get_current_week()

        try:
            url = f"{config.ESPN_API_BASE}/summary"
            params = {
                'week': week,
                'season': self.current_season
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching stats from ESPN: {e}")
            return []

    def fetch_sleeper_stats(self, week: int = None, season: int = None) -> Dict:
        """Fetch player stats from Sleeper API for a specific week."""
        if week is None:
            week = self.get_current_week()
        if season is None:
            season = self.current_season

        try:
            # Sleeper stats endpoint
            url = f"{config.SLEEPER_API_BASE}/stats/nfl/regular/{season}/{week}"
            print(f"Fetching stats for Week {week}, Season {season}...")
            print(f"URL: {url}")
            response = self.session.get(url, timeout=15)
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print(f"✓ Successfully fetched stats for {len(data)} players")
            return data
        except requests.exceptions.ProxyError as e:
            print(f"✗ Proxy/Network error: Cannot reach Sleeper API")
            print(f"  This may be due to network restrictions or firewall settings")
            print(f"  Consider using CSV import instead (see documentation)")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error fetching stats: {type(e).__name__}")
            print(f"  Details: {str(e)[:100]}")
            return {}
        except Exception as e:
            print(f"✗ Unexpected error fetching stats: {e}")
            return {}

    def update_weekly_stats(self, week: int = None):
        """Update stats for all players for a specific week."""
        if week is None:
            week = self.get_current_week()

        print(f"\n" + "=" * 60)
        print(f"UPDATING STATS FOR WEEK {week}")
        print("=" * 60)
        stats_data = self.fetch_sleeper_stats(week)

        if not stats_data:
            print("\n✗ No stats data received from API.")
            print("  This could mean:")
            print("  1. Network/proxy is blocking the request")
            print("  2. The week hasn't been played yet")
            print("  3. API is temporarily unavailable")
            print("\n  Consider using CSV import for stats (see documentation)")
            return

        count = 0
        for player_id, stats in stats_data.items():
            # Check if player exists in our database
            player = self.db.get_player_by_id(player_id)
            if not player:
                continue

            # Calculate fantasy points
            fantasy_points = self.calculate_fantasy_points(stats, config.SCORING_FORMAT)

            # Prepare stats dict
            stats_dict = {
                'passing_yards': stats.get('pass_yd', 0),
                'passing_tds': stats.get('pass_td', 0),
                'interceptions': stats.get('pass_int', 0),
                'rushing_yards': stats.get('rush_yd', 0),
                'rushing_tds': stats.get('rush_td', 0),
                'receptions': stats.get('rec', 0),
                'receiving_yards': stats.get('rec_yd', 0),
                'receiving_tds': stats.get('rec_td', 0),
                'fumbles': stats.get('fum_lost', 0),
                'fantasy_points': fantasy_points
            }

            self.db.upsert_player_stats(player_id, week, self.current_season, stats_dict)
            count += 1

        if count > 0:
            print(f"\n✓ Successfully updated stats for {count} players.")
        else:
            print(f"\n✗ No stats were added to database.")
        print("=" * 60)

    def update_all_recent_weeks(self, num_weeks: int = 4):
        """Update stats for the last N weeks."""
        current_week = self.get_current_week()

        for week in range(max(1, current_week - num_weeks + 1), current_week + 1):
            self.update_weekly_stats(week)
            print(f"Completed week {week}")

    def full_data_refresh(self):
        """Perform a complete data refresh - players and recent stats."""
        print("Starting full data refresh...")
        print("=" * 50)

        # Update player database
        self.update_player_database()

        # Update recent weeks stats
        self.update_all_recent_weeks(config.WEEKS_TO_ANALYZE)

        print("=" * 50)
        print("Data refresh complete!")
