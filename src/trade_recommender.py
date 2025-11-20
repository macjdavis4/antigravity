"""Trade recommendation engine."""
from typing import Dict, List, Tuple
from src.database import Database
from src.analyzer import PlayerAnalyzer
from src.team_manager import TeamManager


class TradeRecommender:
    """Recommends trades based on player analysis and team needs."""

    def __init__(self):
        """Initialize trade recommender."""
        self.db = Database()
        self.analyzer = PlayerAnalyzer()
        self.team_manager = TeamManager()

    def calculate_player_value(self, player_id: str) -> float:
        """Calculate overall player value score."""
        analysis = self.analyzer.get_player_analysis(player_id)

        if "error" in analysis:
            return 0.0

        # Value components
        avg_points = analysis['avg_points']
        consistency = analysis['consistency']
        trend_value = analysis['trend_value']

        # Weighted value calculation
        # 60% average points, 20% consistency, 20% trend
        value = (avg_points * 0.6) + (consistency * 0.002 * avg_points) + (trend_value * 0.2)

        return round(max(0, value), 2)

    def evaluate_trade(self, players_out: List[str], players_in: List[str]) -> Dict:
        """
        Evaluate a proposed trade.
        players_out: List of player IDs you're giving away
        players_in: List of player IDs you're receiving
        """
        if not players_out or not players_in:
            return {"error": "Must specify players for both sides of trade"}

        # Calculate values
        value_out = sum(self.calculate_player_value(p) for p in players_out)
        value_in = sum(self.calculate_player_value(p) for p in players_in)

        value_diff = value_in - value_out
        percent_change = (value_diff / value_out * 100) if value_out > 0 else 0

        # Get player details
        players_out_details = []
        for player_id in players_out:
            player = self.db.get_player_by_id(player_id)
            if player:
                analysis = self.analyzer.get_player_analysis(player_id)
                players_out_details.append({
                    "player": player,
                    "value": self.calculate_player_value(player_id),
                    "avg_points": analysis.get('avg_points', 0),
                    "trend": analysis.get('trend', 'unknown')
                })

        players_in_details = []
        for player_id in players_in:
            player = self.db.get_player_by_id(player_id)
            if player:
                analysis = self.analyzer.get_player_analysis(player_id)
                players_in_details.append({
                    "player": player,
                    "value": self.calculate_player_value(player_id),
                    "avg_points": analysis.get('avg_points', 0),
                    "trend": analysis.get('trend', 'unknown')
                })

        # Determine recommendation
        if percent_change > 15:
            recommendation = "STRONG ACCEPT"
            reason = f"Excellent value gain of {abs(percent_change):.1f}%"
        elif percent_change > 5:
            recommendation = "ACCEPT"
            reason = f"Good value gain of {percent_change:.1f}%"
        elif percent_change > -5:
            recommendation = "FAIR TRADE"
            reason = "Values are relatively equal"
        elif percent_change > -15:
            recommendation = "DECLINE"
            reason = f"Losing {abs(percent_change):.1f}% value"
        else:
            recommendation = "STRONG DECLINE"
            reason = f"Significant value loss of {abs(percent_change):.1f}%"

        # Consider positional needs
        team_analysis = self.team_manager.get_team_analysis()
        positional_impact = self._assess_positional_impact(
            players_out_details, players_in_details, team_analysis
        )

        if positional_impact:
            reason += f". {positional_impact}"

        # Save trade analysis
        self.db.save_trade_analysis(
            players_out,
            players_in,
            recommendation,
            value_diff
        )

        return {
            "giving": players_out_details,
            "receiving": players_in_details,
            "value_giving": round(value_out, 2),
            "value_receiving": round(value_in, 2),
            "value_difference": round(value_diff, 2),
            "percent_change": round(percent_change, 2),
            "recommendation": recommendation,
            "reason": reason
        }

    def _assess_positional_impact(self, players_out: List[Dict],
                                  players_in: List[Dict],
                                  team_analysis: Dict) -> str:
        """Assess how trade impacts positional depth."""
        # Count positions being traded
        positions_out = {}
        positions_in = {}

        for p in players_out:
            pos = p['player']['position']
            positions_out[pos] = positions_out.get(pos, 0) + 1

        for p in players_in:
            pos = p['player']['position']
            positions_in[pos] = positions_in.get(pos, 0) + 1

        impacts = []

        # Check if losing depth at critical positions
        for pos, count in positions_out.items():
            gaining = positions_in.get(pos, 0)
            net_change = gaining - count

            if net_change < 0:
                # Losing players at this position
                depth = self.team_manager.get_position_depth(pos)
                if depth['count'] - abs(net_change) < 2:
                    impacts.append(f"Weakens {pos} depth")

        # Check if gaining needed depth
        weaknesses = team_analysis.get('weaknesses', [])
        for weakness in weaknesses:
            for pos in positions_in.keys():
                if pos in weakness:
                    impacts.append(f"Addresses {pos} weakness")
                    break

        return " ".join(impacts) if impacts else ""

    def suggest_trades_for_player(self, target_player_id: str) -> List[Dict]:
        """Suggest which of your players to trade for a target player."""
        target_player = self.db.get_player_by_id(target_player_id)

        if not target_player:
            return []

        target_value = self.calculate_player_value(target_player_id)
        my_team = self.team_manager.get_team()

        suggestions = []

        for player in my_team:
            my_value = self.calculate_player_value(player['player_id'])

            # Look for fair trades (within 20% value)
            value_diff = abs(target_value - my_value)
            if value_diff / max(my_value, target_value) < 0.2:
                trade_eval = self.evaluate_trade(
                    [player['player_id']],
                    [target_player_id]
                )

                suggestions.append({
                    "your_player": player,
                    "target_player": target_player,
                    "evaluation": trade_eval
                })

        # Sort by value difference (ascending)
        suggestions.sort(key=lambda x: abs(x['evaluation']['value_difference']))

        return suggestions[:5]  # Top 5 suggestions

    def find_upgrade_opportunities(self, position: str = None) -> List[Dict]:
        """Find players available who would upgrade your team."""
        my_team = self.team_manager.get_team()
        opportunities = []

        # Get position rankings
        positions = [position] if position else ['QB', 'RB', 'WR', 'TE']

        for pos in positions:
            # Get my players at this position
            my_players = [p for p in my_team if p['position'] == pos]

            if not my_players:
                continue

            # Find my weakest player at position
            weakest_value = float('inf')
            weakest_player = None

            for player in my_players:
                value = self.calculate_player_value(player['player_id'])
                if value < weakest_value:
                    weakest_value = value
                    weakest_player = player

            if not weakest_player:
                continue

            # Find better players at same position
            all_players = self.db.get_all_players(pos)

            for available in all_players:
                # Skip if already on team
                if any(p['player_id'] == available['player_id'] for p in my_team):
                    continue

                available_value = self.calculate_player_value(available['player_id'])

                # If significantly better
                if available_value > weakest_value * 1.2:
                    analysis = self.analyzer.get_player_analysis(available['player_id'])

                    if "error" not in analysis and analysis['games_played'] >= 2:
                        opportunities.append({
                            "position": pos,
                            "upgrade_from": weakest_player,
                            "upgrade_to": available,
                            "value_gain": round(available_value - weakest_value, 2),
                            "target_analysis": analysis
                        })

        # Sort by value gain
        opportunities.sort(key=lambda x: x['value_gain'], reverse=True)

        return opportunities[:10]

    def find_trade_partners_for_needs(self) -> Dict:
        """Analyze team and suggest specific trade targets."""
        team_analysis = self.team_manager.get_team_analysis()
        suggestions = self.team_manager.suggest_improvements()

        trade_targets = {
            "to_acquire": [],  # Players to target
            "to_trade_away": []  # Players to shop
        }

        # Find players to acquire based on weaknesses
        for suggestion in suggestions.get("suggestions", []):
            if "Add" in suggestion['action'] or "Upgrade" in suggestion['action']:
                # Extract position
                words = suggestion['action'].split()
                for word in words:
                    if word in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
                        position = word
                        # Get top available players at position
                        rankings = self.analyzer.get_position_rankings(position, weeks=4)

                        for rank in rankings[:5]:
                            player = rank['player']
                            # Check not on team
                            my_team = self.team_manager.get_team()
                            if not any(p['player_id'] == player['player_id'] for p in my_team):
                                trade_targets["to_acquire"].append({
                                    "player": player,
                                    "reason": suggestion['action'],
                                    "value": self.calculate_player_value(player['player_id']),
                                    "avg_points": rank['avg_points']
                                })
                        break

        # Find players to trade away (declining or sell-high candidates)
        my_team = self.team_manager.get_team()

        for player in my_team:
            analysis = self.analyzer.get_player_analysis(player['player_id'])

            if "error" in analysis:
                continue

            # Sell high or declining
            if (analysis['trend'] == "declining" or
                (analysis['recent_avg'] > analysis['earlier_avg'] * 1.3)):

                trade_targets["to_trade_away"].append({
                    "player": player,
                    "reason": f"Trending {analysis['trend']}",
                    "value": self.calculate_player_value(player['player_id']),
                    "avg_points": analysis['avg_points']
                })

        return trade_targets

    def batch_evaluate_trades(self, trade_scenarios: List[Tuple[List[str], List[str]]]) -> List[Dict]:
        """Evaluate multiple trade scenarios at once."""
        results = []

        for players_out, players_in in trade_scenarios:
            evaluation = self.evaluate_trade(players_out, players_in)
            results.append(evaluation)

        # Sort by value difference (descending)
        results.sort(key=lambda x: x.get('value_difference', 0), reverse=True)

        return results
