# NFL Fantasy Football Agent

Your personal AI-powered assistant for dominating your fantasy football league! This agent pulls daily NFL player data, analyzes performance trends, manages your team, and provides data-driven trade recommendations.

## Features

### Data Management
- **Automated Daily Updates**: Pulls the latest NFL player stats from public APIs
- **Comprehensive Player Database**: Tracks all active NFL players across positions
- **Historical Stats**: Maintains weekly performance data for trend analysis
- **Scoring Formats**: Supports PPR, Half-PPR, and Standard scoring

### Team Management
- **Roster Management**: Add/remove players from your team with position limits
- **Team Analysis**: Get comprehensive insights into your team's strengths and weaknesses
- **Position Depth Analysis**: Evaluate depth at each position
- **Improvement Suggestions**: AI-powered recommendations to strengthen your roster

### Player Analysis
- **Performance Metrics**: Average points, consistency scores, and trend analysis
- **Player Comparisons**: Side-by-side comparison of any two players
- **Position Rankings**: See top performers at each position
- **Breakout Candidates**: Identify players showing strong upward trends
- **Buy-Low Candidates**: Find undervalued players with temporary dips
- **Sell-High Candidates**: Spot players on unsustainable hot streaks

### Trade Analysis
- **Trade Evaluation**: Analyze proposed trades with value calculations
- **Smart Recommendations**: Get accept/decline advice based on multiple factors
- **Upgrade Opportunities**: Find better players to target for each position
- **Trade Targets**: Personalized suggestions based on your team's needs
- **Historical Tracking**: Keep records of all trade analyses

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd antigravity
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure settings (optional):
```bash
cp .env.example .env
# Edit .env to customize settings
```

## Usage

### Initial Setup

When you first run the agent, you'll need to fetch player data:

```bash
python3 main.py
```

Select option **1** (Refresh NFL data) to download the initial player database and recent stats. This takes a few minutes but only needs to be done once.

### Main Interface

Run the interactive CLI:

```bash
python3 main.py
```

You'll see a menu with all available options:

#### Data Management (Options 1-2)
- Update player data and stats
- Quick refresh for current week only

#### My Team (Options 3-7)
- View your roster
- Add/remove players
- Get team analysis and improvement suggestions

#### Player Analysis (Options 8-13)
- Search and analyze any player
- Compare players head-to-head
- View position rankings
- Find breakout, buy-low, and sell-high candidates

#### Trade Analysis (Options 14-16)
- Evaluate specific trade proposals
- Find upgrade opportunities
- Get personalized trade recommendations

### Daily Automated Updates

To keep your data fresh, run the scheduler in the background:

```bash
python3 scheduler.py
```

This will:
- Run a full data refresh immediately
- Schedule daily updates at 6:00 AM (configurable in `.env`)
- Keep running until you stop it (Ctrl+C)

You can run this in the background or use a process manager like `systemd`, `supervisor`, or `screen`.

## Configuration

Edit `.env` to customize:

```bash
# Data refresh time (24-hour format)
REFRESH_TIME=06:00

# League settings
LEAGUE_SIZE=12
SCORING_FORMAT=PPR  # Options: PPR, Half-PPR, Standard
```

## How It Works

### Data Sources
The agent uses free, public APIs:
- **Sleeper API**: Player information and weekly statistics
- **ESPN API**: Real-time game data and current week

No API keys required!

### Analysis Algorithms

**Player Value Calculation**:
- 60% average fantasy points (recent weeks)
- 20% consistency score (lower variance = better)
- 20% trend value (improving/declining)

**Trend Detection**:
- Linear regression on recent performance
- Classifies as improving (+2 pts/week), declining (-2 pts/week), or stable

**Trade Evaluation**:
- Compares total value of players in vs. out
- Considers positional impact on roster depth
- Provides percentage-based recommendations

**Consistency Score**:
- Calculated using coefficient of variation
- 100 = perfectly consistent, 0 = highly volatile

## Example Workflows

### Setting Up Your Team

1. Refresh data: Option 1
2. Search for your players: Option 8
3. Add them to your team: Option 4
4. Analyze your team: Option 6

### Evaluating a Trade Offer

1. Select Option 14 (Evaluate a trade)
2. Enter players you'd give away
3. Enter players you'd receive
4. Review the recommendation and reasoning

### Finding Waiver Wire Gems

1. Option 11: Find breakout candidates (trending up)
2. Option 12: Find buy-low candidates (temporary dip)
3. Option 8: Analyze specific players in detail

### Weekly Routine

1. Run scheduler daily for automatic updates
2. Check Option 13 for sell-high candidates on your team
3. Review Option 16 for personalized trade recommendations
4. Use Option 6 to monitor your team's performance

## Database

All data is stored locally in `fantasy_football.db` (SQLite):
- `players`: Player information (name, team, position)
- `player_stats`: Weekly statistics
- `my_team`: Your roster
- `trade_history`: Past trade analyses

## Project Structure

```
antigravity/
├── main.py                 # Main CLI interface
├── scheduler.py            # Daily data refresh scheduler
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env                   # User configuration (create from .env.example)
├── fantasy_football.db    # SQLite database (created on first run)
└── src/
    ├── data_fetcher.py    # NFL data API integration
    ├── analyzer.py        # Player performance analysis
    ├── team_manager.py    # Team management logic
    ├── trade_recommender.py # Trade evaluation engine
    └── database.py        # Database operations
```

## Tips for Success

1. **Keep Data Fresh**: Run the scheduler daily or manually refresh before making decisions
2. **Build Your Team First**: Add all your players before using trade analysis
3. **Look at Trends**: Don't just focus on average points - consider trends and consistency
4. **Consider Your Needs**: The agent factors in your team's weaknesses when recommending trades
5. **Cross-Reference**: Use multiple analysis tools (breakout candidates + player comparison, etc.)
6. **Update Weekly**: Check sell-high and buy-low candidates each week

## Limitations

- Data quality depends on public API availability
- Analysis is statistical - doesn't account for injuries, matchups, or other context
- Designed for standard fantasy leagues (adjust ROSTER_LIMITS in config.py for custom leagues)
- Historical data limited to current season

## Troubleshooting

**No data showing up?**
- Make sure you ran Option 1 (Refresh NFL data) first
- Check your internet connection

**Player not found?**
- Database only includes active NFL players
- Try searching by last name only
- Refresh data if player was recently added to a team

**Scheduler not running?**
- Check REFRESH_TIME format in .env (must be HH:MM)
- Ensure Python process stays running (use screen/tmux for background)

## Contributing

This is a personal fantasy football tool, but feel free to:
- Report issues
- Suggest features
- Submit pull requests
- Fork and customize for your league

## License

MIT License - Use freely for your fantasy football domination!

## Disclaimer

This tool is for entertainment and informational purposes. Fantasy football involves chance, and no analysis can guarantee success. Always do your own research and trust your instincts!

Good luck with your season! 🏈📊