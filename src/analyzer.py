"""Analyze player performance and trends."""
import numpy as np
from typing import Dict, List, Tuple
from src.database import Database
import config


class PlayerAnalyzer:
    """Analyzes player statistics and performance trends."""

    def __init__(self):
        """Initialize the analyzer."""
        self.db = Database()

    def calculate_average_points(self, player_id: str, weeks: int = None) -> float:
        """Calculate average fantasy points over recent weeks."""
        stats = self.db.get_player_stats(player_id, weeks or config.WEEKS_TO_ANALYZE)

        if not stats:
            return 0.0

        total_points = sum(s['fantasy_points'] for s in stats)
        return round(total_points / len(stats), 2)

    def calculate_consistency(self, player_id: str, weeks: int = None) -> float:
        """
        Calculate player consistency (lower standard deviation = more consistent).
        Returns a score from 0-100, where 100 is most consistent.
        """
        stats = self.db.get_player_stats(player_id, weeks or config.WEEKS_TO_ANALYZE)

        if len(stats) < 2:
            return 0.0

        points = [s['fantasy_points'] for s in stats]
        std_dev = np.std(points)
        avg = np.mean(points)

        if avg == 0:
            return 0.0

        # Calculate coefficient of variation and convert to consistency score
        cv = (std_dev / avg) * 100
        consistency_score = max(0, 100 - cv)

        return round(consistency_score, 2)

    def calculate_trend(self, player_id: str, weeks: int = None) -> Tuple[str, float]:
        """
        Calculate performance trend (improving, declining, stable).
        Returns trend direction and slope value.
        """
        stats = self.db.get_player_stats(player_id, weeks or config.WEEKS_TO_ANALYZE)

        if len(stats) < 2:
            return "insufficient_data", 0.0

        # Reverse to get chronological order
        stats = list(reversed(stats))
        points = [s['fantasy_points'] for s in stats]

        # Calculate linear regression slope
        x = np.arange(len(points))
        slope = np.polyfit(x, points, 1)[0]

        # Classify trend
        if slope > 2:
            trend = "improving"
        elif slope < -2:
            trend = "declining"
        else:
            trend = "stable"

        return trend, round(slope, 2)

    def get_player_analysis(self, player_id: str) -> Dict:
        """Get comprehensive analysis for a player."""
        player = self.db.get_player_by_id(player_id)

        if not player:
            return {"error": "Player not found"}

        stats = self.db.get_player_stats(player_id, config.WEEKS_TO_ANALYZE)

        if not stats:
            return {
                "player": player,
                "error": "No stats available",
                "avg_points": 0.0,
                "consistency": 0.0,
                "trend": "no_data",
                "trend_value": 0.0
            }

        avg_points = self.calculate_average_points(player_id)
        consistency = self.calculate_consistency(player_id)
        trend, trend_value = self.calculate_trend(player_id)

        # Calculate recent performance (last 2 weeks vs previous weeks)
        recent_avg = np.mean([s['fantasy_points'] for s in stats[:2]]) if len(stats) >= 2 else 0
        earlier_avg = np.mean([s['fantasy_points'] for s in stats[2:]]) if len(stats) > 2 else recent_avg

        return {
            "player": player,
            "avg_points": avg_points,
            "consistency": consistency,
            "trend": trend,
            "trend_value": trend_value,
            "recent_avg": round(recent_avg, 2),
            "earlier_avg": round(earlier_avg, 2),
            "recent_stats": stats[:4],
            "games_played": len(stats),
            "total_points": round(sum(s['fantasy_points'] for s in stats), 2)
        }

    def get_position_rankings(self, position: str, weeks: int = None) -> List[Dict]:
        """Get top players by position ranked by average points."""
        players = self.db.get_all_players(position)
        rankings = []

        for player in players:
            avg_points = self.calculate_average_points(player['player_id'], weeks)

            if avg_points > 0:  # Only include players with stats
                rankings.append({
                    "player": player,
                    "avg_points": avg_points,
                    "consistency": self.calculate_consistency(player['player_id'], weeks)
                })

        # Sort by average points descending
        rankings.sort(key=lambda x: x['avg_points'], reverse=True)

        return rankings

    def compare_players(self, player_id1: str, player_id2: str) -> Dict:
        """Compare two players side by side."""
        analysis1 = self.get_player_analysis(player_id1)
        analysis2 = self.get_player_analysis(player_id2)

        if "error" in analysis1 or "error" in analysis2:
            return {"error": "One or both players not found or have no stats"}

        # Calculate who's better
        points_diff = analysis1['avg_points'] - analysis2['avg_points']
        consistency_diff = analysis1['consistency'] - analysis2['consistency']

        return {
            "player1": analysis1,
            "player2": analysis2,
            "comparison": {
                "points_difference": round(points_diff, 2),
                "points_winner": analysis1['player']['name'] if points_diff > 0 else analysis2['player']['name'],
                "consistency_difference": round(consistency_diff, 2),
                "consistency_winner": analysis1['player']['name'] if consistency_diff > 0 else analysis2['player']['name']
            }
        }

    def get_breakout_candidates(self, position: str = None, min_trend: float = 3.0) -> List[Dict]:
        """Find players showing strong upward trends (breakout candidates)."""
        players = self.db.get_all_players(position) if position else self.db.get_all_players()
        candidates = []

        for player in players:
            trend, trend_value = self.calculate_trend(player['player_id'])

            if trend == "improving" and trend_value >= min_trend:
                stats = self.db.get_player_stats(player['player_id'], config.WEEKS_TO_ANALYZE)

                if len(stats) >= config.MIN_GAMES_PLAYED:
                    candidates.append({
                        "player": player,
                        "trend_value": trend_value,
                        "avg_points": self.calculate_average_points(player['player_id']),
                        "recent_games": len(stats)
                    })

        # Sort by trend value descending
        candidates.sort(key=lambda x: x['trend_value'], reverse=True)

        return candidates[:20]  # Return top 20

    def get_buy_low_candidates(self, position: str = None) -> List[Dict]:
        """Find undervalued players (good avg but recent decline)."""
        players = self.db.get_all_players(position) if position else self.db.get_all_players()
        candidates = []

        for player in players:
            analysis = self.get_player_analysis(player['player_id'])

            if "error" in analysis:
                continue

            # Good average but recent dip
            if (analysis['avg_points'] > 10 and
                analysis['recent_avg'] < analysis['earlier_avg'] and
                analysis['trend'] != "declining"):

                candidates.append({
                    "player": player,
                    "avg_points": analysis['avg_points'],
                    "recent_avg": analysis['recent_avg'],
                    "earlier_avg": analysis['earlier_avg'],
                    "dip": round(analysis['earlier_avg'] - analysis['recent_avg'], 2)
                })

        # Sort by average points descending
        candidates.sort(key=lambda x: x['avg_points'], reverse=True)

        return candidates[:15]

    def get_sell_high_candidates(self, position: str = None) -> List[Dict]:
        """Find players to sell high (recent hot streak but declining trend)."""
        players = self.db.get_all_players(position) if position else self.db.get_all_players()
        candidates = []

        for player in players:
            analysis = self.get_player_analysis(player['player_id'])

            if "error" in analysis:
                continue

            # Recent hot streak but trending down
            if (analysis['recent_avg'] > analysis['earlier_avg'] * 1.2 and
                analysis['trend'] in ["declining", "stable"]):

                candidates.append({
                    "player": player,
                    "avg_points": analysis['avg_points'],
                    "recent_avg": analysis['recent_avg'],
                    "earlier_avg": analysis['earlier_avg'],
                    "spike": round(analysis['recent_avg'] - analysis['earlier_avg'], 2)
                })

        # Sort by recent spike descending
        candidates.sort(key=lambda x: x['spike'], reverse=True)

        return candidates[:15]
