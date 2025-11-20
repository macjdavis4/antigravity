# Quick Start Guide

Get up and running with your NFL Fantasy Football Agent in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - API calls
- `pandas` - Data manipulation
- `numpy` - Statistical analysis
- `python-dotenv` - Configuration
- `schedule` - Daily updates
- `tabulate` - Pretty tables

## Step 2: Initial Configuration (Optional)

```bash
cp .env.example .env
```

Edit `.env` if you want to customize:
- Data refresh time (default: 6:00 AM)
- League size (default: 12)
- Scoring format (default: PPR)

## Step 3: First Run

```bash
python3 main.py
```

Select **Option 1** when the menu appears to fetch player data. This takes 2-3 minutes and downloads:
- All active NFL players (~2000+ players)
- Stats for the last 4 weeks
- Current season data

## Step 4: Build Your Team

After data loads:

1. **Option 4**: Add player to my team
2. Search for your players by name (e.g., "mahomes", "mccaffrey")
3. Select from the results
4. Repeat for all your players

## Step 5: Get Insights

Now you can:

- **Option 6**: Analyze your team (see strengths/weaknesses)
- **Option 7**: Get improvement suggestions
- **Option 14**: Evaluate a trade offer
- **Option 16**: Get personalized trade recommendations

## Step 6: Keep Data Fresh (Optional)

Run the scheduler to automatically update data daily:

```bash
python3 scheduler.py
```

Or manually refresh before each use (Option 1).

## Common First Actions

### Evaluate a Trade Someone Offered You

1. Main menu: Select **14**
2. Enter players you'd give away (one at a time)
3. Press Enter when done
4. Enter players you'd receive (one at a time)
5. Press Enter when done
6. Review the recommendation!

### Find Waiver Wire Pickups

1. **Option 11**: Breakout candidates (hot players)
2. **Option 12**: Buy-low candidates (good players in a slump)
3. **Option 10**: Top players by position

### Compare Two Players

1. **Option 9**: Compare two players
2. Search for first player
3. Search for second player
4. See side-by-side comparison

## Tips

- **First time setup**: Run Option 1 to load all data (required!)
- **Before trades**: Refresh data (Option 1 or 2) for latest stats
- **Weekly routine**: Check sell-high candidates (Option 13) on your team
- **Position needs**: Add all your players first for best trade recommendations

## Troubleshooting

**"No players found"**: You need to run Option 1 first to download player data

**"No stats available"**: Normal for players who haven't played yet this season

**Import errors**: Run `pip install -r requirements.txt`

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Customize roster limits in `config.py` for your league format
- Set up the scheduler for automatic daily updates

Happy fantasy football! 🏈
