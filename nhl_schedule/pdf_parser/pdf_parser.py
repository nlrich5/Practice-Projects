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

TEAM_TIMEZONE_MAP = {
    "Anaheim Ducks":        "Pacific",
    "Boston Bruins":        "Eastern",
    "Buffalo Sabres":       "Eastern",
    "Calgary Flames":       "Alberta",
    "Carolina Hurricanes":  "Eastern",
    "Chicago Blackhawks":   "Central",
    "Colorado Avalanche":   "Mountain",
    "Columbus Blue Jackets":"Eastern",
    "Dallas Stars":         "Central",
    "Detroit Red Wings":    "Eastern",
    "Edmonton Oilers":      "Alberta",
    "Florida Panthers":     "Eastern",
    "Los Angeles Kings":    "Pacific",
    "Minnesota Wild":       "Central",
    "Montreal Canadiens":   "Eastern",
    "Nashville Predators":  "Central",
    "New Jersey Devils":    "Eastern",
    "N.Y. Islanders":       "Eastern",
    "N.Y. Rangers":         "Eastern",
    "Ottawa Senators":      "Eastern",
    "Philadelphia Flyers":  "Eastern",
    "Pittsburgh Penguins":  "Eastern",
    "San Jose Sharks":      "Pacific",
    "Seattle Kraken":       "Pacific",
    "St. Louis Blues":      "Central",
    "Tampa Bay Lightning":  "Eastern",
    "Toronto Maple Leafs":  "Eastern",
    "Utah Mammoth":         "Mountain",
    "Vancouver Canucks":    "BC",
    "Vegas Golden Knights": "Pacific",
    "Washington Capitals":  "Eastern",
    "Winnipeg Jets":        "Central",
}

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

TIMEZONE_MAP = {
    "Pacific":      -8,
    "Pacific DST":  -7,
    "BC":           -7,
    "BC DST":       -7,
    "Mountain":     -7,
    "Mountain DST": -6,
    "Arizona":      -7,
    "Arizona DST":  -7,
    "Central":      -6,
    "Central DST":  -5,
    "Alberta":      -6,
    "Alberta DST":  -6,
    "Eastern":      -5,
    "Eastern DST":  -4,
    "Atlantic":     -4,
    "Atlantic DST": -3
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

def is_DST_active(game_date: str):
    [month, day] = game_date.split(" ")
    day_int = int(day)

    match month:
        case "Sep":
            return True
        case "Oct":
            return True
        case "Nov":
            if day_int < 1:     # November 1st - DST ends
                return True
            else:
                return False
        case "Dec":
            return False
        case "Jan":
            return False
        case "Feb":
            return False
        case "Mar":
            if day_int < 14:    # March 14th - DST starts
                return False
            else:
                return True
        case "Apr":
            return True
        case "May":
            return True
        case "Jun":
            return True
        case "Jul":
            return True
        case "Aug":
            return True

def adjust_date(game_date: str):
    [month, day] = game_date.split(" ")
    day_int = int(day)
    year = 2026
    month_int = 0

    match month:
        case "Sep":
            month_int = 9
        case "Oct":
            month_int = 10
        case "Nov":
            month_int = 11
        case "Dec":
            month_int = 12
        case "Jan":
            month_int = 1
            year = 2027
        case "Feb":
            month_int = 2
            year = 2027
        case "Mar":
            month_int = 3
            year = 2027
        case "Apr":
            month_int = 4
            year = 2027
        case "May":
            month_int = 5
            year = 2027

    return str(month_int) + "/" + str(day_int) + "/" + str(year)

def handle_time_change(date_str: str, time_str: str, home_team: str, desired_timezone: str):
    timezone = TEAM_TIMEZONE_MAP[home_team]
    if is_DST_active(date_str):
        timezone = timezone + " DST"
        desired_timezone = desired_timezone + " DST"

    [time_string, am_pm] = time_str.split(" ")
    [hour, minute] = time_string.split(":")
    hour_int = int(hour)

    hour_24 = hour_int % 12
    if am_pm == "PM":
        hour_24 += 12

    hour_24 = (hour_24 + TIMEZONE_MAP[desired_timezone] - TIMEZONE_MAP[timezone]) % 24

    if hour_24 < 12:
        am_pm = "AM"
    else:
        am_pm = "PM"

    hour_int = hour_24 % 12
    if hour_int == 0:
        hour_int = 12

    return str(hour_int) + ":" + minute + " " + am_pm

def parse_schedule(text, team_name, timezone):
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
            "Date":      adjust_date(date_str),
            "Time":      handle_time_change(date_str, time_str, home_team, timezone),
            "Home Team": home_team,
            "Away Team": away_team,
        })
    return games

def parse_pdf(timezone):
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
            games = parse_schedule(text, team["team"], timezone)
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
