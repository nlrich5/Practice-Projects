from espn_api.football import League, Team

league = League(
    league_id=522250,   # found in your league's URL
    year=2026,
    espn_s2='AEBUTP2wxBbF%2F7wnnpqs3pZQIQhDhu5quEFFKdSLOeUPfmCU2tl0TDrWmHrDpB%2BIyLsGdGefGNsXiLbJHLlWcZwoJ3nLhuDMQ6M0gaGKgP57b8jjuk7zuQ4cwKg%2BE%2B8OjjM3r8fkvXKAQwUzlNWVS95EvcAGP3Hz3IOLKhXwRVSo5LU1tYJy3yr%2BS44s7bjQUK6Qo0ZKD5t%2F9OqWNyVUrOB%2FyWUxj%2BSARiLJPgIlhhsbDjHuN5SG8%2FOZhtcB9puhw%2F7dLE3AiLfNxItFCMRLbQBT7KmVGjty0L1MJwJ3s4pJXA%3D%3D',
    swid='21E007AC-17E1-43C9-B8F7-F70C9CB78E91'
)

for team in league.teams:
    if team.team_name == "Silly Little Guys":
        silly_little_fellas = team

project_week = int(input("What week to project: "))
results_week = int(input("What week for results: "))
get_FAs = input("Get free agents (y/n): ")

if project_week != 0:
    box_scores = league.box_scores(week=project_week)
    with open(f"./project_week{project_week}.csv", "w") as f:
        f.write("Name,Position,Current Position,Status,Projected Points,Opposition Rank,Points\n")
        for match in box_scores:
            if match.away_team == silly_little_fellas:
                for player in match.away_lineup:
                    f.write(f"{player.name},{player.position},{player.slot_position},{player.injuryStatus},{player.projected_points},{player.pro_pos_rank}\n")
            elif match.home_team == silly_little_fellas:
                for player in match.home_lineup:
                    f.write(f"{player.name},{player.position},{player.slot_position},{player.injuryStatus},{player.projected_points},{player.pro_pos_rank}\n")

if results_week != 0:
    box_scores = league.box_scores(week=results_week)
    with open(f"./results_week{results_week}.csv", "w") as f:
        f.write("Name,Position,Current Position,Projected Points,Points\n")
        for match in box_scores:
            if match.away_team == silly_little_fellas:
                for player in match.away_lineup:
                    f.write(f"{player.name},{player.position},{player.slot_position},{player.projected_points},{player.points}\n")
            elif match.home_team == silly_little_fellas:
                for player in match.home_lineup:
                    f.write(f"{player.name},{player.position},{player.slot_position},{player.projected_points},{player.points}\n")

if get_FAs.find("y") != -1:
    with open(f"./free_agents.csv", "w") as f:
        f.write("Name,Position,Projected Average Points,Percent Owned\n")
        for player in league.free_agents(size=200):
            f.write(f"{player.name},{player.position},{player.projected_avg_points},{player.percent_owned}\n")