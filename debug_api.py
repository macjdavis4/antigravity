#!/usr/bin/env python3
"""Debug script to test API calls and see actual data structure."""
import requests
import json
from datetime import datetime


def test_sleeper_players():
    """Test Sleeper players API."""
    print("Testing Sleeper Players API...")
    print("=" * 60)

    url = "https://api.sleeper.app/v1/players/nfl"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Find a well-known player
        for player_id, player_info in list(data.items())[:5]:
            if player_info.get('position') in ['QB', 'RB', 'WR']:
                print(f"\nSample Player Data:")
                print(f"ID: {player_id}")
                print(json.dumps(player_info, indent=2))
                break

        print(f"\nTotal players: {len(data)}")

    except Exception as e:
        print(f"Error: {e}")


def test_sleeper_stats():
    """Test Sleeper stats API for different weeks."""
    print("\n\nTesting Sleeper Stats API...")
    print("=" * 60)

    season = datetime.now().year

    # Try different weeks
    for week in [1, 2, 3, 4, 5]:
        url = f"https://api.sleeper.app/v1/stats/nfl/regular/{season}/{week}"
        print(f"\nTrying Week {week}, Season {season}:")
        print(f"URL: {url}")

        try:
            response = requests.get(url, timeout=15)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Players with stats: {len(data)}")

                # Show a sample
                if data:
                    sample_id = list(data.keys())[0]
                    print(f"\nSample stats for player {sample_id}:")
                    print(json.dumps(data[sample_id], indent=2))
                    break
            else:
                print(f"Response: {response.text[:200]}")

        except Exception as e:
            print(f"Error: {e}")


def test_sleeper_projections():
    """Test Sleeper projections API."""
    print("\n\nTesting Sleeper Projections API...")
    print("=" * 60)

    season = datetime.now().year
    week = 10

    url = f"https://api.sleeper.app/v1/projections/nfl/regular/{season}/{week}"
    print(f"URL: {url}")

    try:
        response = requests.get(url, timeout=15)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Players with projections: {len(data)}")

            if data:
                sample_id = list(data.keys())[0]
                print(f"\nSample projection for player {sample_id}:")
                print(json.dumps(data[sample_id], indent=2))
        else:
            print(f"Response: {response.text[:200]}")

    except Exception as e:
        print(f"Error: {e}")


def test_espn_api():
    """Test ESPN API."""
    print("\n\nTesting ESPN API...")
    print("=" * 60)

    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            week = data.get('week', {})
            print(f"Current Week: {week.get('number')}")
            print(f"Season: {data.get('season', {}).get('year')}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_sleeper_players()
    test_sleeper_stats()
    test_sleeper_projections()
    test_espn_api()
