from datetime import datetime, timedelta
import json
import os
import pandas as pd

def get_team_abbreviation(team):
    with open(os.path.expanduser('~/nba-dl/data/config/teams.json')) as f:
        teams_config = json.load(f)

    return teams_config[team]['TEAM_ABBREVIATION']

def get_season_from_id(season_id):
    with open(os.path.expanduser('~/nba-dl/data/config/season-config.json')) as f:
        season_config = json.load(f)
    for season, ids in season_config.items():
        if season_id in ids:
            return season

def get_home_team_preseason_odds(game):
    season_id = game['SEASON_ID'].values[0]
    team = game['HOME_TEAM_NAME'].values[0]
    season = get_season_from_id(season_id)
    odds = pd.read_csv('~/nba-dl/data/preseason-odds/{}-preseason-odds.csv'.format(season))
    team_row = odds[odds['Team'] == team]
    return team_row["Probability"].values[0]
    
def get_away_team_preseason_odds(game):
    season_id = game['SEASON_ID'].values[0]
    team = game['AWAY_TEAM_NAME'].values[0]
    season = get_season_from_id(season_id)
    odds = pd.read_csv('~/nba-dl/data/preseason-odds/{}-preseason-odds.csv'.format(season))
    team_row = odds[odds['Team'] == team]
    return team_row["Probability"].values[0]

def home_games_in_last_week(game, game_inventory):
    game_date = game['GAME_DATE'].values[0]
    team = game['HOME_TEAM_NAME'].values[0]
    team_games = game_inventory[game_inventory['TEAM_NAME'] == team]
    parsed_date = datetime.strptime(game_date, '%Y-%m-%d')
    parsed_week_before = parsed_date - timedelta(days=7)
    week_before = parsed_week_before.strftime('%Y-%m-%d')
    last_games = team_games[team_games['GAME_DATE'] < game_date].sort_values(by=['GAME_DATE'], ascending=False)
    last_week_games = last_games[last_games['GAME_DATE'] >= week_before]
    return len(last_week_games.index)

def away_games_in_last_week(game, game_inventory):
    game_date = game['GAME_DATE'].values[0]
    team = game['AWAY_TEAM_NAME'].values[0]
    team_games = game_inventory[game_inventory['TEAM_NAME'] == team]
    parsed_date = datetime.strptime(game_date, '%Y-%m-%d')
    parsed_week_before = parsed_date - timedelta(days=7)
    week_before = parsed_week_before.strftime('%Y-%m-%d')
    last_games = team_games[team_games['GAME_DATE'] < game_date].sort_values(by=['GAME_DATE'], ascending=False)
    last_week_games = last_games[last_games['GAME_DATE'] >= week_before]
    return len(last_week_games.index)

def home_last_x_games_ratio(game, game_inventory, x):
    date = game['GAME_DATE'].values[0]
    team = game['HOME_TEAM_NAME'].values[0]
    team_games = game_inventory[game_inventory['TEAM_NAME'] == team]
    last_x_games = team_games[team_games['GAME_DATE'] < date].sort_values(by=['GAME_DATE'], ascending=False)[:x]
    wins = 0
    for index, row in last_x_games.iterrows():
        if row['WL'] == 'W':
            wins+=1
    return wins/x

def away_last_x_games_ratio(game, game_inventory, x):
    date = game['GAME_DATE'].values[0]
    team = game['AWAY_TEAM_NAME'].values[0]
    team_games = game_inventory[game_inventory['TEAM_NAME'] == team]
    last_x_games = team_games[team_games['GAME_DATE'] < date].sort_values(by=['GAME_DATE'], ascending=False)[:x]
    wins = 0
    for index, row in last_x_games.iterrows():
        if row['WL'] == 'W':
            wins+=1
    return wins/x

def home_last_10_games_h2h_ratio(game, game_inventory):
    date = game['GAME_DATE'].values[0]
    home_team = game['HOME_TEAM_NAME'].values[0]
    away_team = game['AWAY_TEAM_NAME'].values[0]
    away_team_abbreviation = get_team_abbreviation(away_team)
    team_games = game_inventory[game_inventory['TEAM_NAME'] == home_team]
    last_team_games = team_games[team_games['GAME_DATE'] < date].sort_values(by=['GAME_DATE'], ascending=False)
    last_team_hh_games = last_team_games[last_team_games['MATCHUP'].str.contains(away_team_abbreviation)][:10]
    wins = 0
    for index, row in last_team_hh_games.iterrows():
        if row['WL'] == 'W':
            wins+=1
    return wins/10

def away_last_10_games_h2h_ratio(game, game_inventory):
    date = game['GAME_DATE'].values[0]
    home_team = game['HOME_TEAM_NAME'].values[0]
    away_team = game['AWAY_TEAM_NAME'].values[0]
    home_team_abbreviation = get_team_abbreviation(home_team)
    team_games = game_inventory[game_inventory['TEAM_NAME'] == away_team]
    last_team_games = team_games[team_games['GAME_DATE'] < date].sort_values(by=['GAME_DATE'], ascending=False)
    last_team_hh_games = last_team_games[last_team_games['MATCHUP'].str.contains(home_team_abbreviation)][:10]
    wins = 0
    for index, row in last_team_hh_games.iterrows():
        if row['WL'] == 'W':
            wins+=1
    return wins/10

def team_home_form_ratio(game, game_inventory, number_of_games):
    date = game['GAME_DATE'].values[0]
    team = game['HOME_TEAM_NAME'].values[0]
    team_games = game_inventory[game_inventory['TEAM_NAME'] == team]
    team_home_games = team_games[~team_games['MATCHUP'].str.contains('@')]
    last_home_games = team_home_games[team_home_games['GAME_DATE'] < date].sort_values(by=['GAME_DATE'], ascending=False)[:number_of_games]
    wins = 0
    for index, row in last_home_games.iterrows():
        if row['WL'] == 'W':
            wins+=1
    return wins/number_of_games

def team_away_form_ratio(game, game_inventory, number_of_games):
    date = game['GAME_DATE'].values[0]
    team = game['AWAY_TEAM_NAME'].values[0]
    team_games = game_inventory[game_inventory['TEAM_NAME'] == team]    
    team_away_games = team_games[team_games['MATCHUP'].str.contains('@')]
    last_away_games = team_away_games[team_away_games['GAME_DATE'] < date].sort_values(by=['GAME_DATE'], ascending=False)[:number_of_games]
    wins = 0
    for index, row in last_away_games.iterrows():
        if row['WL'] == 'W':
            wins+=1
    return wins/number_of_games