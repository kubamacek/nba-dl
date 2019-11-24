'''
dataset_creator - python module to create dataset for realtime model

- to be used separately for regular season and playoffs matches
- uses functions from utils module to prepare numerical values for each feature

usage: python3 dataset_creator.py

'''

import pandas as pd
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.expanduser('~/nba-dl/helpers'))
import utils
import logging
import argparse

rs_data = pd.read_csv('~/nba-dl/data/matches/RS/book-RS.csv')
po_data = pd.read_csv('~/nba-dl/data/matches/PO/book-PO.csv')

game_inventory = pd.read_csv('~/nba-dl/data/game-inventory/all-games-corrected.csv')

'''
GLOSSARY:

HWIN         - home team result, W/L
HPLUSMINUS   - home team match +-
HPO          - home team preseason odds - chances for trophy
APO          - away team preseason odds - chances for trophy
HGLW         - home team games last week - how many 
AGLW         - away team games last week - how many
HLGR         - home team last x games ratio - wins/matches
ALGR         - away team last x games ratio - wins/matches
HLH2HR       - home team last head2head ratio - wins/matches
ALH2HR       - away team last head2head ratio - wins/matches
HFTR         - home team form last x games as host - wins/matches
AFTR         - away team form last x games as visitor - wins/matches
HSWR         - home team season win ratio
ASWR         - away team season win ratio
HSPS         - home team season average points scored
ASPS         - away team season average points scored
HSPL         - home team season average points lost
ASPL         - away team season average points lost
'''

columns = ['SEASON_ID', 'HOME_TEAM_NAME', 'AWAY_TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'HWIN', 'HPLUSMINUS',
           'HPO', 'APO', 'HGLW', 'AGLW', 'HLGR', 'ALGR', 'HLH2HR', 'ALH2HR', 'HTFR', 'ATFR',
           'HSWR', 'ASWR', 'HSPS', 'ASPS', 'HSPL', 'ASPL']

df = pd.DataFrame(columns=columns)

for row, series in po_data.iterrows():
    try:        
        game_row = {}
        game_row['SEASON_ID'] = series['SEASON_ID']
        game_row['HOME_TEAM_NAME'] = series['HOME_TEAM_NAME']
        game_row['AWAY_TEAM_NAME'] = series['AWAY_TEAM_NAME']
        game_row['GAME_ID'] = series['GAME_ID']
        game_row['GAME_DATE'] = series['GAME_DATE']
        game_row['HWIN'] = series['HWIN']
        game_row['HPLUSMINUS'] = series['HPLUSMINUS']    
        game_row['HPO'] = utils.get_home_team_preseason_odds(series)
        game_row['APO'] = utils.get_away_team_preseason_odds(series)
        game_row['HGLW'] = utils.home_games_in_last_week(series, game_inventory)
        game_row['AGLW'] = utils.away_games_in_last_week(series, game_inventory)
        game_row['HLGR'] = utils.home_last_x_games_ratio(series, game_inventory, 10)
        game_row['ALGR'] = utils.away_last_x_games_ratio(series, game_inventory, 10)
        game_row['HLH2HR'] = utils.home_last_10_games_h2h_ratio(series, game_inventory)
        game_row['ALH2HR'] = utils.away_last_10_games_h2h_ratio(series, game_inventory)
        game_row['HTFR'] = utils.team_home_form_ratio(series, game_inventory, 10)
        game_row['ATFR'] = utils.team_away_form_ratio(series, game_inventory, 10)
        #hack - get league standings for day before - ONLY REGULAR SEASON
        #one_day_before = (datetime.strptime(game_row["GAME_DATE"], '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        #series['GAME_DATE'] =  one_day_before
        game_row['HSWR'] = utils.get_home_team_season_ratio(series)
        game_row['ASWR'] = utils.get_away_team_season_ratio(series)
        game_row['HSPS'] = utils.get_home_team_season_avg_pts_scored(series)
        game_row['ASPS'] = utils.get_away_team_season_avg_pts_scored(series)
        game_row['HSPL'] = utils.get_home_team_season_avg_pts_lost(series)
        game_row['ASPL'] = utils.get_away_team_season_avg_pts_lost(series)
        df = df.append(game_row, ignore_index=True)
    except ZeroDivisionError: # first meeting between teams
        print("ZeroDivisionError, skipping {}".format(series['GAME_ID']))
        continue
    except IndexError: # getting season stanings for team before first game of the season
        print("IndexError, skipping {}".format(series['GAME_ID']))
    except FileNotFoundError: # getting season standings for first day of the season
        print("FileNotFoundError, skipping {}".format(series['GAME_ID']))
        continue

df.to_csv('dataset.csv', index=False)