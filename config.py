"""Configuration settings for NFL Fantasy Agent."""
import os
from dotenv import load_dotenv

load_dotenv()

# Database settings
DATABASE_PATH = "fantasy_football.db"

# API settings
ESPN_API_BASE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
SLEEPER_API_BASE = "https://api.sleeper.app/v1"

# Data refresh settings
REFRESH_TIME = os.getenv("REFRESH_TIME", "06:00")

# League settings
LEAGUE_SIZE = int(os.getenv("LEAGUE_SIZE", "12"))
SCORING_FORMAT = os.getenv("SCORING_FORMAT", "PPR")  # PPR, Standard, or Half-PPR

# Analysis settings
WEEKS_TO_ANALYZE = 4  # Number of recent weeks to consider for trends
MIN_GAMES_PLAYED = 2  # Minimum games to include in analysis

# Position limits for roster
ROSTER_LIMITS = {
    "QB": 2,
    "RB": 4,
    "WR": 4,
    "TE": 2,
    "K": 1,
    "DEF": 1
}
