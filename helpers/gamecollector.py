'''
game_collector - python module for team match stats

- uses nba_api and LeagueGameFinder endpoint - more info: https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguegamefinder.md
- connects gamelogs for single teams to one row per match
- drop data to csv file

usage: python3 game_collector.py -t SEASONTYPE

'''

from nba_api.stats.endpoints import leaguegamefinder
import csv
import re
import pandas as pd
import sys
import logging
import argparse
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--seasontype", type=str, required=True, help="part of season, Regular Season(RS) or Play-Off(PO)")
args = parser.parse_args()

regular_season_pattern = re.compile('^RS$')
if regular_season_pattern.match(args.seasontype):
    season_type = 'Regular Season'
else:
    season_type = 'Playoffs'

years = [ '1999-00' ,'2000-01', '2001-02', '2002-03', '2003-04', '2004-05', '2005-06', '2006-07', '2007-08', '2008-09',
          '2009-10', '2010-11', '2011-12', '2012-13', '2013-14', '2014-15', '2015-16', '2016-17', '2017-18', '2018-19' ]

for year in years:
    logger.info("Collecting games for {} season".format(year))
    game_finder = leaguegamefinder.LeagueGameFinder(season_nullable=year, season_type_nullable='Regular Season', league_id_nullable='00')
    time.sleep(5)
    games = game_finder.get_data_frames()[0]

    columns = ['SEASON_ID', 'HOME_TEAM_NAME', 'AWAY_TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'HWIN', 'HPLUSMINUS',
            'HFGM', 'HFGA', 'HFG_PCT', 'HFG3M', 'HFG3A', 'HFG3_PCT', 'HFTM', 'HFTA', 'HFT_PCT',
            'HOREB', 'HDREB', 'HREB', 'HAST', 'HSTL', 'HBLK', 'HTOV', 'HPF',
            'AFGM', 'AFGA', 'AFG_PCT', 'AFG3M', 'AFG3A', 'AFG3_PCT', 'AFTM', 'AFTA', 'AFT_PCT',
            'AOREB', 'ADREB', 'AREB', 'AAST', 'ASTL', 'ABLK', 'ATOV', 'APF']    

    game_ids = list(set(games['GAME_ID']))

    final = pd.DataFrame(columns=columns)
    
    for game in game_ids:
        temp = games.loc[games.GAME_ID == game]
        final_data_row = {}
        for row, index in temp.iterrows():
            if '@' not in index['MATCHUP']:
                final_data_row['SEASON_ID'] = index['SEASON_ID']
                final_data_row['GAME_ID'] = index['GAME_ID']
                final_data_row['GAME_DATE'] = index['GAME_DATE']
                final_data_row['HWIN'] = index['WL']
                final_data_row['HPLUSMINUS'] = index['PLUS_MINUS']
                final_data_row['HOME_TEAM_NAME'] = index['TEAM_NAME']
                final_data_row['HFGM'] = index['FGM']
                final_data_row['HFGA'] = index['FGA']
                final_data_row['HFG_PCT'] = index['FG_PCT']
                final_data_row['HFG3M'] = index['FG3M']
                final_data_row['HFG3A'] = index['FG3A']
                final_data_row['HFG3_PCT'] = index['FG3_PCT']
                final_data_row['HFTM'] = index['FTM']
                final_data_row['HFTA'] = index['FTA']
                final_data_row['HFT_PCT'] = index['FT_PCT']
                final_data_row['HDREB'] = index['DREB']
                final_data_row['HOREB'] = index['OREB']
                final_data_row['HREB'] = index['REB']
                final_data_row['HAST'] = index['AST']
                final_data_row['HSTL'] = index['STL']
                final_data_row['HBLK'] = index['BLK']
                final_data_row['HPF'] = index['PF']
                final_data_row['HTOV'] = index['TOV']
            else:
                final_data_row['AWAY_TEAM_NAME'] = index['TEAM_NAME']
                final_data_row['AFGM'] = index['FGM']
                final_data_row['AFGA'] = index['FGA']
                final_data_row['AFG_PCT'] = index['FG_PCT']
                final_data_row['AFG3M'] = index['FG3M']
                final_data_row['AFG3A'] = index['FG3A']
                final_data_row['AFG3_PCT'] = index['FG3_PCT']
                final_data_row['AFTM'] = index['FTM']
                final_data_row['AFTA'] = index['FTA']
                final_data_row['AFT_PCT'] = index['FT_PCT']
                final_data_row['ADREB'] = index['DREB']
                final_data_row['AOREB'] = index['OREB']
                final_data_row['AREB'] = index['REB']
                final_data_row['AAST'] = index['AST']
                final_data_row['ASTL'] = index['STL']
                final_data_row['ABLK'] = index['BLK']
                final_data_row['ATOV'] = index['TOV']
                final_data_row['APF'] = index['PF']
        final = final.append(final_data_row, ignore_index=True)

    if final.isnull().values.any():
        print("ERROR - NaN detected!")
        sys.exit(1)

    final.to_csv('{}-games.csv'.format(year), index=False)