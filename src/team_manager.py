"""Manage user's fantasy team."""
from typing import Dict, List, Optional
from src.database import Database
from src.analyzer import PlayerAnalyzer
import config


class TeamManager:
    """Manages the user's fantasy football team."""

    def __init__(self):
        """Initialize team manager."""
        self.db = Database()
        self.analyzer = PlayerAnalyzer()

    def add_player(self, player_id: str, notes: str = "") -> Dict:
        """Add a player to the team."""
        player = self.db.get_player_by_id(player_id)

        if not player:
            return {"success": False, "message": "Player not found"}

        # Check position limits
        team = self.get_team()
        position_count = sum(1 for p in team if p['position'] == player['position'])
        max_allowed = config.ROSTER_LIMITS.get(player['position'], 0)

        if position_count >= max_allowed:
            return {
                "success": False,
                "message": f"Position limit reached. Max {max_allowed} {player['position']} allowed."
            }

        success = self.db.add_to_my_team(player_id, notes)

        if success:
            return {
                "success": True,
                "message": f"Added {player['name']} ({player['position']}) to your team!"
            }
        else:
            return {
                "success": False,
                "message": "Player already on your team"
            }

    def remove_player(self, player_id: str) -> Dict:
        """Remove a player from the team."""
        player = self.db.get_player_by_id(player_id)

        if not player:
            return {"success": False, "message": "Player not found"}

        success = self.db.remove_from_my_team(player_id)

        if success:
            return {
                "success": True,
                "message": f"Removed {player['name']} from your team"
            }
        else:
            return {
                "success": False,
                "message": "Player not on your team"
            }

    def get_team(self) -> List[Dict]:
        """Get the user's current team."""
        return self.db.get_my_team()

    def get_team_analysis(self) -> Dict:
        """Get analysis of the entire team."""
        team = self.get_team()

        if not team:
            return {"message": "Your team is empty"}

        analysis_by_position = {}
        total_avg_points = 0
        player_analyses = []

        for player in team:
            player_analysis = self.analyzer.get_player_analysis(player['player_id'])
            player_analyses.append(player_analysis)

            position = player['position']
            if position not in analysis_by_position:
                analysis_by_position[position] = {
                    "players": [],
                    "total_avg": 0,
                    "count": 0
                }

            if "error" not in player_analysis:
                analysis_by_position[position]["players"].append(player_analysis)
                analysis_by_position[position]["total_avg"] += player_analysis['avg_points']
                analysis_by_position[position]["count"] += 1
                total_avg_points += player_analysis['avg_points']

        # Calculate averages per position
        for position in analysis_by_position:
            count = analysis_by_position[position]["count"]
            if count > 0:
                analysis_by_position[position]["avg_per_player"] = round(
                    analysis_by_position[position]["total_avg"] / count, 2
                )

        return {
            "team_size": len(team),
            "total_projected_points": round(total_avg_points, 2),
            "by_position": analysis_by_position,
            "player_analyses": player_analyses,
            "strengths": self._identify_strengths(analysis_by_position),
            "weaknesses": self._identify_weaknesses(analysis_by_position)
        }

    def _identify_strengths(self, position_analysis: Dict) -> List[str]:
        """Identify team strengths."""
        strengths = []

        for position, data in position_analysis.items():
            avg = data.get("avg_per_player", 0)

            # Position-specific thresholds
            thresholds = {
                "QB": 20,
                "RB": 15,
                "WR": 15,
                "TE": 10,
                "K": 8,
                "DEF": 8
            }

            threshold = thresholds.get(position, 10)

            if avg > threshold:
                strengths.append(f"Strong {position} position (avg {avg} pts)")

        return strengths

    def _identify_weaknesses(self, position_analysis: Dict) -> List[str]:
        """Identify team weaknesses."""
        weaknesses = []

        # Check for unfilled positions
        for position, limit in config.ROSTER_LIMITS.items():
            current_count = position_analysis.get(position, {}).get("count", 0)

            if current_count == 0:
                weaknesses.append(f"No {position} on roster")
            elif current_count < limit:
                weaknesses.append(f"Only {current_count}/{limit} {position} positions filled")

        # Check for low-performing positions
        for position, data in position_analysis.items():
            avg = data.get("avg_per_player", 0)

            thresholds = {
                "QB": 15,
                "RB": 10,
                "WR": 10,
                "TE": 6,
                "K": 5,
                "DEF": 5
            }

            threshold = thresholds.get(position, 5)

            if avg < threshold and avg > 0:
                weaknesses.append(f"Weak {position} position (avg {avg} pts)")

        return weaknesses

    def get_position_depth(self, position: str) -> Dict:
        """Analyze depth at a specific position."""
        team = self.get_team()
        position_players = [p for p in team if p['position'] == position]

        analyses = []
        for player in position_players:
            analysis = self.analyzer.get_player_analysis(player['player_id'])
            if "error" not in analysis:
                analyses.append(analysis)

        # Sort by average points
        analyses.sort(key=lambda x: x['avg_points'], reverse=True)

        return {
            "position": position,
            "count": len(position_players),
            "max_allowed": config.ROSTER_LIMITS.get(position, 0),
            "players": analyses,
            "depth_score": self._calculate_depth_score(analyses)
        }

    def _calculate_depth_score(self, analyses: List[Dict]) -> str:
        """Calculate depth score for a position."""
        if len(analyses) == 0:
            return "None"
        elif len(analyses) == 1:
            return "Shallow"
        elif len(analyses) == 2:
            # Check if both are good
            if all(a['avg_points'] > 10 for a in analyses):
                return "Good"
            else:
                return "Adequate"
        else:
            # 3+ players
            if all(a['avg_points'] > 10 for a in analyses[:2]):
                return "Excellent"
            else:
                return "Good"

    def suggest_improvements(self) -> Dict:
        """Suggest improvements for the team."""
        team_analysis = self.get_team_analysis()
        suggestions = []

        # Based on weaknesses
        for weakness in team_analysis.get("weaknesses", []):
            if "No" in weakness and "on roster" in weakness:
                position = weakness.split()[1]
                suggestions.append({
                    "priority": "high",
                    "action": f"Add a {position} player to your roster",
                    "reason": "Position not filled"
                })
            elif "Weak" in weakness:
                position = weakness.split()[1]
                suggestions.append({
                    "priority": "medium",
                    "action": f"Upgrade your {position} position",
                    "reason": "Below average performance"
                })

        # Look for declining players
        for player_analysis in team_analysis.get("player_analyses", []):
            if "error" in player_analysis:
                continue

            if player_analysis['trend'] == "declining":
                player_name = player_analysis['player']['name']
                suggestions.append({
                    "priority": "medium",
                    "action": f"Consider trading {player_name}",
                    "reason": "Performance declining"
                })

        return {
            "suggestions": suggestions[:10]  # Top 10 suggestions
        }
