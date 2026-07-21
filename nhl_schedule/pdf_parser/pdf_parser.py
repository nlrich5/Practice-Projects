import csv
import json
import os
import re
from pypdf import PdfReader

# Paths relative to this script's location, regardless of where it is invoked from
_HERE       = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(_HERE, "..", "config", "config.json")
PDF_FILE    = os.path.join(_HERE, "schedule.pdf")
OUTPUT_FILE = os.path.join(_HERE, "..", "output", "schedule.csv")

SHORT_NAME_MAP = {
    "Anaheim":        "Anaheim Ducks",
    "Boston":         "Boston Bruins",
    "Buffalo":        "Buffalo Sabres",
    "Calgary":        "Calgary Flames",
    "Carolina":       "Carolina Hurricanes",
    "Chicago":        "Chicago Blackhawks",
    "Colorado":       "Colorado Avalanche",
    "Columbus":       "Columbus Blue Jackets",
    "Dallas":         "Dallas Stars",
    "Detroit":        "Detroit Red Wings",
    "Edmonton":       "Edmonton Oilers",
    "Florida":        "Florida Panthers",
    "Los Angeles":    "Los Angeles Kings",
    "Minnesota":      "Minnesota Wild",
    "Montreal":       "Montreal Canadiens",
    "Nashville":      "Nashville Predators",
    "New Jersey":     "New Jersey Devils",
    "N.Y. Islanders": "N.Y. Islanders",
    "N.Y. Rangers":   "N.Y. Rangers",
    "Ottawa":         "Ottawa Senators",
    "Philadelphia":   "Philadelphia Flyers",
    "Pittsburgh":     "Pittsburgh Penguins",
    "San Jose":       "San Jose Sharks",
    "Seattle":        "Seattle Kraken",
    "St. Louis":      "St. Louis Blues",
    "Tampa Bay":      "Tampa Bay Lightning",
    "Toronto":        "Toronto Maple Leafs",
    "Utah":           "Utah Mammoth",
    "Vancouver":      "Vancouver Canucks",
    "Vegas":          "Vegas Golden Knights",
    "Washington":     "Washington Capitals",
    "Winnipeg":       "Winnipeg Jets",
}

GAME_PATTERN = re.compile(
    r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\."   # Day abbreviation  (group 1)
    r"\s+"
    r"([A-Za-z]+\.?\s+\d+)"              # Month + day number  (group 2)
    r"\s+"
    r"(\d+:\d+\s+[AP]M)"                 # Time  (group 3)
    r"\s+"
    r"(AT\s+)?"                           # Optional "AT "  (group 4)
    r"([A-Za-z][A-Za-z0-9 .]+?)"         # Opponent name  (group 5)
    r"(?=\s+(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\.|\s*$|\s*\n)"  # lookahead: next game, EOL, or newline
)

def parse_schedule(text, team_name):
    games = []
    for match in GAME_PATTERN.finditer(text):
        day_abbr = match.group(1)
        date_str = match.group(2).strip()
        time_str = match.group(3).strip()
        at_flag  = match.group(4)
        opponent = SHORT_NAME_MAP.get(match.group(5).strip(), match.group(5).strip())

        if at_flag:
            home_team = opponent
            away_team = team_name
        else:
            home_team = team_name
            away_team = opponent

        games.append({
            "Day":       day_abbr,
            "Date":      date_str,
            "Time":      time_str,
            "Home Team": home_team,
            "Away Team": away_team,
        })
    return games

def parse_pdf():
    # Load teams and filter to selected ones
    with open(CONFIG_FILE, encoding="utf-8") as f:
        teams = json.load(f)

    selected_teams = [t for t in teams if t["selected"].strip().lower() == "yes"]

    if not selected_teams:
        print("No teams marked as selected in config.json.")
    else:
        reader = PdfReader(PDF_FILE)
        fieldnames = ["Day", "Date", "Time", "Home Team", "Away Team"]
        all_games = []

        for team in selected_teams:
            text  = reader.pages[team["page_index"]].extract_text()
            games = parse_schedule(text, team["team"])
            all_games.extend(games)
            print(f"Parsed {len(games)} games for {team['team']}")

        # Deduplicate: same date + home team + away team is the same game
        seen = {}
        for game in all_games:
            key = (game["Date"], game["Home Team"], game["Away Team"])
            seen.setdefault(key, game)
        all_games = list(seen.values())

        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_games)

        print(f"\nWrote {len(all_games)} total games to {OUTPUT_FILE}")
