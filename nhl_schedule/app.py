from flask import Flask, request, render_template, send_file
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf_parser"))
import pdf_parser

app = Flask(__name__)

_HERE       = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(_HERE, "config", "config.json")

def update_config(team_status):
    with open(CONFIG_FILE, 'r') as config:
        config_json = json.load(config)

    for item in config_json:
        item['selected'] = team_status.get(item['team'], 'no')

    with open(CONFIG_FILE, 'w') as config:
        json.dump(config_json, config, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    with open(CONFIG_FILE, 'r') as config_file:
        config_json = json.load(config_file)
        TEAMS = [{
            'team': item['team'],
            'selected': item.get('selected', 'no')
        } for item in config_json]

    if request.method == 'POST':
        team_status = {
            team['team']: request.form.get(team['team'], 'no')
            for team in TEAMS
        }
        timezone = request.form.get('timezone')
        print("Team status:", team_status)
        print("Timezone:", timezone)
        update_config(team_status=team_status)
        pdf_parser.parse_pdf(timezone)

        output_path = os.path.join(_HERE, "output", "schedule.csv")                                                                                                                   
        return send_file(                                                                                                                                                                                               
            output_path,                                                                                                                                                                                                
            as_attachment=True,                                                                                                                                    
            download_name="schedule.csv"                                                                                                                                                       
        )

    return render_template("home.html", items=TEAMS)

if __name__ == '__main__':
    app.run(debug=True)
