# Troubleshooting Guide

## Player Shows 0 Points / No Data

### Symptoms
- Player stats show 0 points when they actually scored
- "No stats available" error
- Data refresh completes but no stats are updated

### Root Causes

**1. API Connection Issues**
The most common cause. The app uses public APIs that may be blocked by:
- Corporate/school firewalls
- VPN or proxy settings
- Network restrictions
- API rate limiting

**Solution: Use CSV Import**
```bash
# In the main menu, select:
# Option 18 - Export CSV templates
# Option 17 - Import data from CSV
```

**2. Wrong Season/Week**
The agent tries to fetch data for the current week, which may not be available yet.

**Solution: Specify Week/Season**
When importing CSV data, you can specify the week and season explicitly.

**3. Player Not in Database**
Stats can only be imported for players that exist in the database.

**Solution: Import Players First**
1. Import players CSV (Option 17 → 1)
2. Then import stats CSV (Option 17 → 2)

### Step-by-Step Fix

#### Option A: Use CSV Import (Recommended if APIs are blocked)

1. **Export Templates**
   ```bash
   # In main menu, select Option 18
   ```
   This creates:
   - `players_template.csv`
   - `stats_template.csv`

2. **Get Your Data**
   - Export data from your fantasy league website
   - Or manually create CSVs using the templates
   - Or use data from ESPN, Yahoo, Sleeper, etc.

3. **Import Players**
   ```bash
   # In main menu, select Option 17 → 1
   # Enter the path to your players CSV
   ```

4. **Import Stats**
   ```bash
   # In main menu, select Option 17 → 2
   # Enter the path to your stats CSV
   # Specify week and season when prompted
   ```

#### Option B: Debug API Connection

1. **Test Your Connection**
   ```bash
   python3 debug_api.py
   ```
   This will show exactly what's happening with API calls.

2. **Check for Proxy Errors**
   Look for messages like:
   - "Proxy/Network error"
   - "Max retries exceeded"
   - "403 Forbidden"

3. **Try Different Network**
   - Disable VPN
   - Try different Wi-Fi network
   - Use mobile hotspot
   - Try from home network instead of work/school

#### Option C: Manual Database Entry

If you only have a few players, you can manually add them:

1. Install SQLite browser:
   ```bash
   # Mac
   brew install --cask db-browser-for-sqlite

   # Linux
   sudo apt-get install sqlitebrowser

   # Windows
   # Download from https://sqlitebrowser.org/
   ```

2. Open `fantasy_football.db`

3. Add records to `player_stats` table

## CSV File Format

### Players CSV Format
```csv
player_id,name,team,position
mahomes_patrick,Patrick Mahomes,KC,QB
mccaffrey_christian,Christian McCaffrey,SF,RB
jefferson_justin,Justin Jefferson,MIN,WR
```

### Stats CSV Format
```csv
player_id,week,season,passing_yards,passing_tds,interceptions,rushing_yards,rushing_tds,receptions,receiving_yards,receiving_tds,fumbles,fantasy_points
mahomes_patrick,10,2024,320,3,1,12,0,0,0,0,0,23.28
mccaffrey_christian,10,2024,0,0,0,98,2,5,45,0,0,26.8
jefferson_justin,10,2024,0,0,0,0,0,8,121,2,0,32.1
```

**Notes:**
- `player_id` must be unique (use any format, e.g., lastname_firstname)
- `fantasy_points` is optional - will be calculated if not provided
- Stats for positions not used should be 0 (e.g., QB receiving stats)
- You can create records for multiple weeks

## Where to Get Data

### Option 1: Your Fantasy Platform

Most platforms allow CSV export:

**ESPN Fantasy:**
1. Go to your league
2. Players → Stats
3. Export to CSV

**Yahoo Fantasy:**
1. My Team → Players
2. Export Stats

**Sleeper:**
1. League → Players
2. Export option in menu

### Option 2: Public Data Sources

- [Pro Football Reference](https://www.pro-football-reference.com/)
- [FantasyPros](https://www.fantasypros.com/)
- [NFL.com](https://www.nfl.com/stats/)

### Option 3: Use Demo/Sample Data

Create a small sample dataset for testing:

```bash
# Use Option 18 to create templates
# Then edit them with a few players and their stats
# Import with Option 17
```

## Verifying the Fix

After importing data:

1. **Search for a player** (Option 8)
2. **Check their stats** - should show fantasy points
3. **View rankings** (Option 10) - should show players sorted by points

If you still see 0 points:
- Check that player_id in stats CSV matches player_id in players CSV
- Verify week and season are correct
- Ensure fantasy_points column has values OR other stat columns have values

## Getting Help

If you're still having issues:

1. **Check the error messages** - they often indicate the specific problem
2. **Verify CSV format** - use the templates as a guide
3. **Test with minimal data** - import just 1-2 players first
4. **Check database** - use `sqlite3 fantasy_football.db` to inspect data

## Common Error Messages

**"Player not found"**
- Player doesn't exist in database
- Import players first (Option 17 → 1)

**"No stats available"**
- No stats records for that player
- Import stats (Option 17 → 2)
- Or the API calls failed

**"No players found"**
- Database is empty
- Need to run Option 1 OR Option 17 → 1

**"Proxy/Network error"**
- APIs are blocked
- Use CSV import instead (Option 17)

## Prevention

To avoid this issue in the future:

1. **Use CSV Import from the start** if you're on a restricted network
2. **Export your data regularly** so you have backups
3. **Set up the scheduler** on an unrestricted network
4. **Keep templates handy** for quick manual updates

## Advanced: Creating Your Own Data Pipeline

If you have coding experience, you can:

1. Write a script to fetch data from your league's API
2. Export to the CSV format above
3. Import via Option 17
4. Automate this with cron/scheduled tasks

Example:
```python
import requests
import csv

# Fetch from your league API
data = get_league_data()

# Convert to our format
with open('my_stats.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['player_id', 'week', 'season', ...])
    for player in data:
        writer.writerow([player.id, player.week, ...])
```

Then import with Option 17!
