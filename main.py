#!/usr/bin/env python3
"""NFL Fantasy Football Agent - Main CLI Interface."""
import sys
from tabulate import tabulate
from src.data_fetcher import NFLDataFetcher
from src.analyzer import PlayerAnalyzer
from src.team_manager import TeamManager
from src.trade_recommender import TradeRecommender
from src.csv_importer import CSVImporter


class FantasyAgent:
    """Main CLI interface for NFL Fantasy Agent."""

    def __init__(self):
        """Initialize the agent."""
        self.fetcher = NFLDataFetcher()
        self.analyzer = PlayerAnalyzer()
        self.team_manager = TeamManager()
        self.trade_recommender = TradeRecommender()
        self.csv_importer = CSVImporter()

    def print_menu(self):
        """Display main menu."""
        print("\n" + "=" * 60)
        print("NFL FANTASY FOOTBALL AGENT")
        print("=" * 60)
        print("\n--- DATA MANAGEMENT ---")
        print("1. Refresh NFL data (pull latest player stats)")
        print("2. Quick update (current week only)")
        print("17. Import data from CSV (players/stats)")
        print("18. Export CSV templates")
        print("\n--- MY TEAM ---")
        print("3. View my team")
        print("4. Add player to my team")
        print("5. Remove player from my team")
        print("6. Analyze my team")
        print("7. Get team improvement suggestions")
        print("\n--- PLAYER ANALYSIS ---")
        print("8. Search and analyze a player")
        print("9. Compare two players")
        print("10. View top players by position")
        print("11. Find breakout candidates")
        print("12. Find buy-low candidates")
        print("13. Find sell-high candidates")
        print("\n--- TRADE ANALYSIS ---")
        print("14. Evaluate a trade")
        print("15. Find upgrade opportunities")
        print("16. Get trade recommendations")
        print("\n0. Exit")
        print("=" * 60)

    def run(self):
        """Run the main CLI loop."""
        print("\nWelcome to NFL Fantasy Football Agent!")
        print("Your personal assistant for fantasy football dominance.")

        while True:
            self.print_menu()
            choice = input("\nEnter your choice: ").strip()

            if choice == "0":
                print("\nThanks for using Fantasy Agent. Good luck!")
                break
            elif choice == "1":
                self.refresh_data()
            elif choice == "2":
                self.quick_update()
            elif choice == "3":
                self.view_team()
            elif choice == "4":
                self.add_player_to_team()
            elif choice == "5":
                self.remove_player_from_team()
            elif choice == "6":
                self.analyze_team()
            elif choice == "7":
                self.team_suggestions()
            elif choice == "8":
                self.search_player()
            elif choice == "9":
                self.compare_players()
            elif choice == "10":
                self.view_rankings()
            elif choice == "11":
                self.breakout_candidates()
            elif choice == "12":
                self.buy_low_candidates()
            elif choice == "13":
                self.sell_high_candidates()
            elif choice == "14":
                self.evaluate_trade()
            elif choice == "15":
                self.upgrade_opportunities()
            elif choice == "16":
                self.trade_recommendations()
            elif choice == "17":
                self.import_csv_data()
            elif choice == "18":
                self.export_csv_templates()
            else:
                print("\nInvalid choice. Please try again.")

            input("\nPress Enter to continue...")

    # Data Management
    def refresh_data(self):
        """Refresh all player data."""
        print("\nStarting full data refresh...")
        print("This may take a few minutes...")
        self.fetcher.full_data_refresh()

    def quick_update(self):
        """Quick update for current week."""
        print("\nUpdating current week stats...")
        week = self.fetcher.get_current_week()
        self.fetcher.update_weekly_stats(week)

    # Team Management
    def view_team(self):
        """Display user's team."""
        team = self.team_manager.get_team()

        if not team:
            print("\nYour team is empty. Add some players!")
            return

        print(f"\n--- MY TEAM ({len(team)} players) ---")

        # Group by position
        by_position = {}
        for player in team:
            pos = player['position']
            if pos not in by_position:
                by_position[pos] = []
            by_position[pos].append(player)

        for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            if position in by_position:
                print(f"\n{position}:")
                for player in by_position[position]:
                    analysis = self.analyzer.get_player_analysis(player['player_id'])
                    avg = analysis.get('avg_points', 0) if 'error' not in analysis else 0
                    trend = analysis.get('trend', 'N/A') if 'error' not in analysis else 'N/A'
                    print(f"  - {player['name']} ({player['team']}) - "
                          f"Avg: {avg:.1f} pts, Trend: {trend}")

    def add_player_to_team(self):
        """Add a player to team."""
        search = input("\nEnter player name to search: ").strip()

        if not search:
            return

        players = self.fetcher.db.search_players(search)

        if not players:
            print("No players found.")
            return

        print("\nSearch results:")
        for i, player in enumerate(players[:10], 1):
            print(f"{i}. {player['name']} - {player['position']} ({player['team']})")

        choice = input("\nEnter number to add (or 0 to cancel): ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(players):
                player = players[idx]
                result = self.team_manager.add_player(player['player_id'])
                print(f"\n{result['message']}")
        except (ValueError, IndexError):
            print("Invalid selection.")

    def remove_player_from_team(self):
        """Remove a player from team."""
        team = self.team_manager.get_team()

        if not team:
            print("\nYour team is empty.")
            return

        print("\nYour team:")
        for i, player in enumerate(team, 1):
            print(f"{i}. {player['name']} - {player['position']}")

        choice = input("\nEnter number to remove (or 0 to cancel): ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(team):
                player = team[idx]
                result = self.team_manager.remove_player(player['player_id'])
                print(f"\n{result['message']}")
        except (ValueError, IndexError):
            print("Invalid selection.")

    def analyze_team(self):
        """Analyze the user's team."""
        analysis = self.team_manager.get_team_analysis()

        if "message" in analysis:
            print(f"\n{analysis['message']}")
            return

        print("\n--- TEAM ANALYSIS ---")
        print(f"Team Size: {analysis['team_size']} players")
        print(f"Total Projected Points: {analysis['total_projected_points']:.2f}")

        print("\n--- BY POSITION ---")
        for position, data in analysis['by_position'].items():
            avg = data.get('avg_per_player', 0)
            count = data['count']
            print(f"{position}: {count} players, Avg {avg:.2f} pts/player")

        if analysis['strengths']:
            print("\n--- STRENGTHS ---")
            for strength in analysis['strengths']:
                print(f"  + {strength}")

        if analysis['weaknesses']:
            print("\n--- WEAKNESSES ---")
            for weakness in analysis['weaknesses']:
                print(f"  - {weakness}")

    def team_suggestions(self):
        """Get team improvement suggestions."""
        suggestions = self.team_manager.suggest_improvements()

        print("\n--- IMPROVEMENT SUGGESTIONS ---")

        if not suggestions['suggestions']:
            print("Your team looks good! No major suggestions.")
            return

        for i, suggestion in enumerate(suggestions['suggestions'], 1):
            priority = suggestion['priority'].upper()
            print(f"\n{i}. [{priority}] {suggestion['action']}")
            print(f"   Reason: {suggestion['reason']}")

    # Player Analysis
    def search_player(self):
        """Search and analyze a specific player."""
        search = input("\nEnter player name: ").strip()

        if not search:
            return

        players = self.fetcher.db.search_players(search)

        if not players:
            print("No players found.")
            return

        print("\nSearch results:")
        for i, player in enumerate(players[:10], 1):
            print(f"{i}. {player['name']} - {player['position']} ({player['team']})")

        choice = input("\nEnter number to analyze (or 0 to cancel): ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(players):
                player = players[idx]
                self._display_player_analysis(player['player_id'])
        except (ValueError, IndexError):
            print("Invalid selection.")

    def _display_player_analysis(self, player_id: str):
        """Display detailed player analysis."""
        analysis = self.analyzer.get_player_analysis(player_id)

        if "error" in analysis:
            print(f"\n{analysis['error']}")
            return

        player = analysis['player']
        print(f"\n--- {player['name']} ({player['position']} - {player['team']}) ---")
        print(f"Average Points: {analysis['avg_points']:.2f}")
        print(f"Consistency Score: {analysis['consistency']:.2f}/100")
        print(f"Trend: {analysis['trend'].upper()} ({analysis['trend_value']:+.2f})")
        print(f"Games Played: {analysis['games_played']}")

        if analysis['recent_stats']:
            print("\nRecent Games:")
            for stat in analysis['recent_stats'][:4]:
                print(f"  Week {stat['week']}: {stat['fantasy_points']:.2f} pts")

    def compare_players(self):
        """Compare two players."""
        print("\n--- COMPARE PLAYERS ---")

        # Player 1
        search1 = input("Enter first player name: ").strip()
        players1 = self.fetcher.db.search_players(search1)

        if not players1:
            print("First player not found.")
            return

        print("\nMatches:")
        for i, p in enumerate(players1[:5], 1):
            print(f"{i}. {p['name']} - {p['position']} ({p['team']})")

        idx1 = int(input("Select first player: ")) - 1
        if not (0 <= idx1 < len(players1)):
            return

        # Player 2
        search2 = input("\nEnter second player name: ").strip()
        players2 = self.fetcher.db.search_players(search2)

        if not players2:
            print("Second player not found.")
            return

        print("\nMatches:")
        for i, p in enumerate(players2[:5], 1):
            print(f"{i}. {p['name']} - {p['position']} ({p['team']})")

        idx2 = int(input("Select second player: ")) - 1
        if not (0 <= idx2 < len(players2)):
            return

        # Compare
        comparison = self.analyzer.compare_players(
            players1[idx1]['player_id'],
            players2[idx2]['player_id']
        )

        if "error" in comparison:
            print(f"\n{comparison['error']}")
            return

        p1 = comparison['player1']
        p2 = comparison['player2']
        comp = comparison['comparison']

        print(f"\n--- COMPARISON ---")
        print(f"\n{p1['player']['name']}:")
        print(f"  Avg Points: {p1['avg_points']:.2f}")
        print(f"  Consistency: {p1['consistency']:.2f}")
        print(f"  Trend: {p1['trend']}")

        print(f"\n{p2['player']['name']}:")
        print(f"  Avg Points: {p2['avg_points']:.2f}")
        print(f"  Consistency: {p2['consistency']:.2f}")
        print(f"  Trend: {p2['trend']}")

        print(f"\nWinner (Points): {comp['points_winner']}")
        print(f"Winner (Consistency): {comp['consistency_winner']}")

    def view_rankings(self):
        """View top players by position."""
        print("\nPositions: QB, RB, WR, TE, K, DEF")
        position = input("Enter position: ").strip().upper()

        if position not in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            print("Invalid position.")
            return

        print(f"\n--- TOP {position}s ---")
        rankings = self.analyzer.get_position_rankings(position)

        if not rankings:
            print("No data available.")
            return

        table_data = []
        for i, rank in enumerate(rankings[:20], 1):
            player = rank['player']
            table_data.append([
                i,
                player['name'],
                player['team'],
                f"{rank['avg_points']:.2f}",
                f"{rank['consistency']:.1f}"
            ])

        print(tabulate(table_data,
                      headers=['Rank', 'Player', 'Team', 'Avg Pts', 'Consistency'],
                      tablefmt='grid'))

    def breakout_candidates(self):
        """Find breakout candidates."""
        print("\n--- BREAKOUT CANDIDATES (Trending Up) ---")
        candidates = self.analyzer.get_breakout_candidates()

        if not candidates:
            print("No breakout candidates found.")
            return

        table_data = []
        for candidate in candidates[:15]:
            player = candidate['player']
            table_data.append([
                player['name'],
                player['position'],
                player['team'],
                f"{candidate['avg_points']:.2f}",
                f"+{candidate['trend_value']:.2f}"
            ])

        print(tabulate(table_data,
                      headers=['Player', 'Pos', 'Team', 'Avg Pts', 'Trend'],
                      tablefmt='grid'))

    def buy_low_candidates(self):
        """Find buy-low candidates."""
        print("\n--- BUY LOW CANDIDATES (Recent Dip) ---")
        candidates = self.analyzer.get_buy_low_candidates()

        if not candidates:
            print("No buy-low candidates found.")
            return

        table_data = []
        for candidate in candidates[:15]:
            player = candidate['player']
            table_data.append([
                player['name'],
                player['position'],
                player['team'],
                f"{candidate['avg_points']:.2f}",
                f"{candidate['recent_avg']:.2f}",
                f"-{candidate['dip']:.2f}"
            ])

        print(tabulate(table_data,
                      headers=['Player', 'Pos', 'Team', 'Avg', 'Recent', 'Dip'],
                      tablefmt='grid'))

    def sell_high_candidates(self):
        """Find sell-high candidates."""
        print("\n--- SELL HIGH CANDIDATES (Recent Spike) ---")
        candidates = self.analyzer.get_sell_high_candidates()

        if not candidates:
            print("No sell-high candidates found.")
            return

        table_data = []
        for candidate in candidates[:15]:
            player = candidate['player']
            table_data.append([
                player['name'],
                player['position'],
                player['team'],
                f"{candidate['avg_points']:.2f}",
                f"{candidate['recent_avg']:.2f}",
                f"+{candidate['spike']:.2f}"
            ])

        print(tabulate(table_data,
                      headers=['Player', 'Pos', 'Team', 'Avg', 'Recent', 'Spike'],
                      tablefmt='grid'))

    # Trade Analysis
    def evaluate_trade(self):
        """Evaluate a proposed trade."""
        print("\n--- EVALUATE TRADE ---")
        print("Enter players you're GIVING AWAY")

        giving = []
        while True:
            search = input("Enter player name (or press Enter to finish): ").strip()
            if not search:
                break

            players = self.fetcher.db.search_players(search)
            if players:
                print("Matches:")
                for i, p in enumerate(players[:5], 1):
                    print(f"{i}. {p['name']} - {p['position']} ({p['team']})")

                idx = int(input("Select player: ")) - 1
                if 0 <= idx < len(players):
                    giving.append(players[idx]['player_id'])
                    print(f"Added {players[idx]['name']}")

        if not giving:
            print("No players selected.")
            return

        print("\nEnter players you're RECEIVING")
        receiving = []
        while True:
            search = input("Enter player name (or press Enter to finish): ").strip()
            if not search:
                break

            players = self.fetcher.db.search_players(search)
            if players:
                print("Matches:")
                for i, p in enumerate(players[:5], 1):
                    print(f"{i}. {p['name']} - {p['position']} ({p['team']})")

                idx = int(input("Select player: ")) - 1
                if 0 <= idx < len(players):
                    receiving.append(players[idx]['player_id'])
                    print(f"Added {players[idx]['name']}")

        if not receiving:
            print("No players selected.")
            return

        # Evaluate
        evaluation = self.trade_recommender.evaluate_trade(giving, receiving)

        print("\n" + "=" * 60)
        print("TRADE EVALUATION")
        print("=" * 60)

        print("\nYOU GIVE:")
        for p in evaluation['giving']:
            print(f"  - {p['player']['name']} ({p['player']['position']}) - "
                  f"Value: {p['value']:.2f}, Avg: {p['avg_points']:.2f} pts")

        print("\nYOU RECEIVE:")
        for p in evaluation['receiving']:
            print(f"  + {p['player']['name']} ({p['player']['position']}) - "
                  f"Value: {p['value']:.2f}, Avg: {p['avg_points']:.2f} pts")

        print(f"\nTotal Value Giving: {evaluation['value_giving']:.2f}")
        print(f"Total Value Receiving: {evaluation['value_receiving']:.2f}")
        print(f"Value Difference: {evaluation['value_difference']:+.2f} "
              f"({evaluation['percent_change']:+.1f}%)")

        print(f"\n>>> RECOMMENDATION: {evaluation['recommendation']} <<<")
        print(f"Reason: {evaluation['reason']}")

    def upgrade_opportunities(self):
        """Find upgrade opportunities."""
        print("\n--- UPGRADE OPPORTUNITIES ---")
        opportunities = self.trade_recommender.find_upgrade_opportunities()

        if not opportunities:
            print("No upgrade opportunities found.")
            return

        for opp in opportunities[:10]:
            print(f"\n{opp['position']} Upgrade:")
            print(f"  From: {opp['upgrade_from']['name']}")
            print(f"  To: {opp['upgrade_to']['name']} ({opp['upgrade_to']['team']})")
            print(f"  Value Gain: +{opp['value_gain']:.2f}")
            print(f"  Target Avg: {opp['target_analysis']['avg_points']:.2f} pts")

    def trade_recommendations(self):
        """Get personalized trade recommendations."""
        print("\n--- TRADE RECOMMENDATIONS ---")
        recommendations = self.trade_recommender.find_trade_partners_for_needs()

        print("\n--- PLAYERS TO TARGET ---")
        if recommendations['to_acquire']:
            for i, target in enumerate(recommendations['to_acquire'][:10], 1):
                player = target['player']
                print(f"{i}. {player['name']} ({player['position']} - {player['team']})")
                print(f"   Reason: {target['reason']}")
                print(f"   Avg: {target['avg_points']:.2f} pts, Value: {target['value']:.2f}")
        else:
            print("No specific targets identified.")

        print("\n--- PLAYERS TO TRADE AWAY ---")
        if recommendations['to_trade_away']:
            for i, tradeable in enumerate(recommendations['to_trade_away'][:10], 1):
                player = tradeable['player']
                print(f"{i}. {player['name']} ({player['position']} - {player['team']})")
                print(f"   Reason: {tradeable['reason']}")
                print(f"   Avg: {tradeable['avg_points']:.2f} pts, Value: {tradeable['value']:.2f}")
        else:
            print("No players recommended to trade away.")

    def import_csv_data(self):
        """Import player data or stats from CSV files."""
        print("\n--- IMPORT DATA FROM CSV ---")
        print("1. Import players")
        print("2. Import stats")
        print("0. Cancel")

        choice = input("\nSelect import type: ").strip()

        if choice == "1":
            filepath = input("Enter path to players CSV file: ").strip()
            if filepath:
                count = self.csv_importer.import_players_csv(filepath)
                if count > 0:
                    print(f"\n✓ Successfully imported {count} players!")
                else:
                    print("\n✗ No players were imported. Check the file format.")

        elif choice == "2":
            filepath = input("Enter path to stats CSV file: ").strip()
            if filepath:
                week = input("Week number (press Enter to use value from CSV): ").strip()
                season = input("Season year (press Enter to use value from CSV): ").strip()

                week = int(week) if week else None
                season = int(season) if season else None

                count = self.csv_importer.import_stats_csv(filepath, week, season)
                if count > 0:
                    print(f"\n✓ Successfully imported {count} stat records!")
                else:
                    print("\n✗ No stats were imported. Check the file format.")

    def export_csv_templates(self):
        """Export CSV template files."""
        print("\n--- EXPORT CSV TEMPLATES ---")
        print("Creating template files...")

        self.csv_importer.export_players_template("players_template.csv")
        self.csv_importer.export_stats_template("stats_template.csv")

        print("\n✓ Templates created:")
        print("  - players_template.csv")
        print("  - stats_template.csv")
        print("\nEdit these files with your data, then use Option 17 to import.")


def main():
    """Main entry point."""
    agent = FantasyAgent()

    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n\nExiting... Good luck with your team!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        print("Please check your setup and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
