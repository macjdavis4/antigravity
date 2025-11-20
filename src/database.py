"""Database operations for NFL Fantasy Agent."""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import config


class Database:
    """Manages SQLite database for player stats and user team."""

    def __init__(self, db_path: str = config.DATABASE_PATH):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Create database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                team TEXT,
                position TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Player stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                week INTEGER NOT NULL,
                season INTEGER NOT NULL,
                passing_yards REAL DEFAULT 0,
                passing_tds INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                rushing_yards REAL DEFAULT 0,
                rushing_tds INTEGER DEFAULT 0,
                receptions INTEGER DEFAULT 0,
                receiving_yards REAL DEFAULT 0,
                receiving_tds INTEGER DEFAULT 0,
                fumbles INTEGER DEFAULT 0,
                fantasy_points REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                UNIQUE(player_id, week, season)
            )
        """)

        # User's team table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS my_team (
                player_id TEXT PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        """)

        # Trade analysis history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                players_out TEXT,
                players_in TEXT,
                recommendation TEXT,
                value_difference REAL
            )
        """)

        conn.commit()
        conn.close()

    def upsert_player(self, player_id: str, name: str, team: str, position: str):
        """Insert or update player information."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO players (player_id, name, team, position, last_updated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(player_id) DO UPDATE SET
                name = excluded.name,
                team = excluded.team,
                position = excluded.position,
                last_updated = CURRENT_TIMESTAMP
        """, (player_id, name, team, position))

        conn.commit()
        conn.close()

    def upsert_player_stats(self, player_id: str, week: int, season: int, stats: Dict):
        """Insert or update player stats for a specific week."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO player_stats (
                player_id, week, season,
                passing_yards, passing_tds, interceptions,
                rushing_yards, rushing_tds,
                receptions, receiving_yards, receiving_tds,
                fumbles, fantasy_points
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(player_id, week, season) DO UPDATE SET
                passing_yards = excluded.passing_yards,
                passing_tds = excluded.passing_tds,
                interceptions = excluded.interceptions,
                rushing_yards = excluded.rushing_yards,
                rushing_tds = excluded.rushing_tds,
                receptions = excluded.receptions,
                receiving_yards = excluded.receiving_yards,
                receiving_tds = excluded.receiving_tds,
                fumbles = excluded.fumbles,
                fantasy_points = excluded.fantasy_points,
                created_at = CURRENT_TIMESTAMP
        """, (
            player_id, week, season,
            stats.get('passing_yards', 0),
            stats.get('passing_tds', 0),
            stats.get('interceptions', 0),
            stats.get('rushing_yards', 0),
            stats.get('rushing_tds', 0),
            stats.get('receptions', 0),
            stats.get('receiving_yards', 0),
            stats.get('receiving_tds', 0),
            stats.get('fumbles', 0),
            stats.get('fantasy_points', 0)
        ))

        conn.commit()
        conn.close()

    def get_player_stats(self, player_id: str, weeks: int = None) -> List[Dict]:
        """Get player stats for recent weeks."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT * FROM player_stats
            WHERE player_id = ?
            ORDER BY season DESC, week DESC
        """

        if weeks:
            query += f" LIMIT {weeks}"

        cursor.execute(query, (player_id,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def get_all_players(self, position: Optional[str] = None) -> List[Dict]:
        """Get all players, optionally filtered by position."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if position:
            cursor.execute("""
                SELECT * FROM players WHERE position = ?
                ORDER BY name
            """, (position,))
        else:
            cursor.execute("SELECT * FROM players ORDER BY name")

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def search_players(self, search_term: str) -> List[Dict]:
        """Search players by name."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM players
            WHERE name LIKE ?
            ORDER BY name
            LIMIT 20
        """, (f"%{search_term}%",))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def add_to_my_team(self, player_id: str, notes: str = ""):
        """Add a player to user's team."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO my_team (player_id, notes)
                VALUES (?, ?)
            """, (player_id, notes))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def remove_from_my_team(self, player_id: str):
        """Remove a player from user's team."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM my_team WHERE player_id = ?", (player_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0

    def get_my_team(self) -> List[Dict]:
        """Get all players on user's team with their info."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.*, mt.added_at, mt.notes
            FROM my_team mt
            JOIN players p ON mt.player_id = p.player_id
            ORDER BY p.position, p.name
        """)

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def get_player_by_id(self, player_id: str) -> Optional[Dict]:
        """Get player information by ID."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
        result = cursor.fetchone()
        conn.close()

        return dict(result) if result else None

    def save_trade_analysis(self, players_out: List[str], players_in: List[str],
                           recommendation: str, value_diff: float):
        """Save a trade analysis for future reference."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trade_history (players_out, players_in, recommendation, value_difference)
            VALUES (?, ?, ?, ?)
        """, (",".join(players_out), ",".join(players_in), recommendation, value_diff))

        conn.commit()
        conn.close()
