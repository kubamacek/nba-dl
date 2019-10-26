from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

years = [  '1998-99', '1999-00' ,'2000-01', '2001-02', '2002-03',
           '2003-04', '2004-05', '2005-06', '2006-07', '2007-08',
           '2008-09', '2009-10', '2010-11', '2011-12', '2012-13',
           '2013-14', '2014-15', '2015-16', '2016-17', '2017-18', '2018-19'  ]

season_parts = ['Regular Season', 'Playoffs']

all_games = pd.DataFrame()
for year in years:
    for season_part in season_parts:
        game_finder = leaguegamefinder.LeagueGameFinder(season_type_nullable=season_part, season_nullable=year, league_id_nullable='00')
        games = game_finder.get_data_frames()[0]
        all_games = all_games.append(games)
        logger.info("Appending {} games for {} season to game-inventory...".format(season_part, year))
        time.sleep(5)

all_games.to_csv('data/game-inventory/all-games.csv', index=False)