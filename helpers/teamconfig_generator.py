'''
teamconfig_generator - python module to generate config file for teams

- uses game inventory to create dict with team name as key and team abbreviation and teamID as values
- saves result to json file

usage: python3 teamconfig_generator.py

'''

import pandas as pd
import json

game_inventory = pd.read_csv('~/nba-dl/data/game-inventory/all-games-corrected.csv')

teams_dict = {}
for index, row in game_inventory.iterrows():
    team_info = {'TEAM_ABBREVIATION': row['TEAM_ABBREVIATION'], 'TEAM_ID': row['TEAM_ID']}
    if row['TEAM_NAME'] not in teams_dict.keys():
        teams_dict[row['TEAM_NAME']] = team_info

with open('data/config/teams.json', 'w') as f:
    f.write(json.dumps(teams_dict, indent=4))