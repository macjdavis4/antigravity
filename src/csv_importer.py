"""Import player stats from CSV files."""
import csv
from typing import Dict, List
from src.database import Database
import config


class CSVImporter:
    """Import player data and stats from CSV files."""

    def __init__(self):
        """Initialize the importer."""
        self.db = Database()

    def import_players_csv(self, filepath: str) -> int:
        """
        Import players from CSV.

        Expected columns:
        player_id, name, team, position
        """
        count = 0
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    player_id = row.get('player_id', '').strip()
                    name = row.get('name', '').strip()
                    team = row.get('team', 'FA').strip()
                    position = row.get('position', '').strip()

                    if player_id and name and position:
                        self.db.upsert_player(player_id, name, team, position)
                        count += 1

            print(f"Imported {count} players from {filepath}")
            return count

        except Exception as e:
            print(f"Error importing players: {e}")
            return 0

    def import_stats_csv(self, filepath: str, week: int = None, season: int = None) -> int:
        """
        Import player stats from CSV.

        Expected columns:
        player_id, week, season, passing_yards, passing_tds, interceptions,
        rushing_yards, rushing_tds, receptions, receiving_yards, receiving_tds,
        fumbles, fantasy_points
        """
        count = 0

        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    player_id = row.get('player_id', '').strip()
                    row_week = int(row.get('week', week or 1))
                    row_season = int(row.get('season', season or 2024))

                    if not player_id:
                        continue

                    # Check if player exists
                    player = self.db.get_player_by_id(player_id)
                    if not player:
                        print(f"Warning: Player {player_id} not found, skipping stats")
                        continue

                    stats = {
                        'passing_yards': float(row.get('passing_yards', 0)),
                        'passing_tds': int(row.get('passing_tds', 0)),
                        'interceptions': int(row.get('interceptions', 0)),
                        'rushing_yards': float(row.get('rushing_yards', 0)),
                        'rushing_tds': int(row.get('rushing_tds', 0)),
                        'receptions': int(row.get('receptions', 0)),
                        'receiving_yards': float(row.get('receiving_yards', 0)),
                        'receiving_tds': int(row.get('receiving_tds', 0)),
                        'fumbles': int(row.get('fumbles', 0)),
                    }

                    # Calculate fantasy points if not provided
                    if 'fantasy_points' in row and row['fantasy_points']:
                        stats['fantasy_points'] = float(row['fantasy_points'])
                    else:
                        stats['fantasy_points'] = self._calculate_fantasy_points(stats)

                    self.db.upsert_player_stats(player_id, row_week, row_season, stats)
                    count += 1

            print(f"Imported {count} stat records from {filepath}")
            return count

        except Exception as e:
            print(f"Error importing stats: {e}")
            return 0

    def _calculate_fantasy_points(self, stats: Dict) -> float:
        """Calculate fantasy points based on stats."""
        points = 0.0

        # Passing stats
        points += stats.get('passing_yards', 0) * 0.04
        points += stats.get('passing_tds', 0) * 4
        points -= stats.get('interceptions', 0) * 2

        # Rushing stats
        points += stats.get('rushing_yards', 0) * 0.1
        points += stats.get('rushing_tds', 0) * 6

        # Receiving stats
        points += stats.get('receiving_yards', 0) * 0.1
        points += stats.get('receiving_tds', 0) * 6

        # PPR bonus
        if config.SCORING_FORMAT == "PPR":
            points += stats.get('receptions', 0) * 1.0
        elif config.SCORING_FORMAT == "Half-PPR":
            points += stats.get('receptions', 0) * 0.5

        # Fumbles
        points -= stats.get('fumbles', 0) * 2

        return round(points, 2)

    def export_players_template(self, filepath: str):
        """Export a template CSV for players."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['player_id', 'name', 'team', 'position'])
            writer.writerow(['mahomes_patrick', 'Patrick Mahomes', 'KC', 'QB'])
            writer.writerow(['mccaffrey_christian', 'Christian McCaffrey', 'SF', 'RB'])

        print(f"Created player template: {filepath}")

    def export_stats_template(self, filepath: str):
        """Export a template CSV for stats."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'player_id', 'week', 'season',
                'passing_yards', 'passing_tds', 'interceptions',
                'rushing_yards', 'rushing_tds',
                'receptions', 'receiving_yards', 'receiving_tds',
                'fumbles', 'fantasy_points'
            ])
            writer.writerow([
                'mahomes_patrick', '1', '2024',
                '291', '2', '1',
                '5', '0',
                '0', '0', '0',
                '0', '19.64'
            ])

        print(f"Created stats template: {filepath}")
