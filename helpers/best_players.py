# -*- coding: utf-8 -*-
import pandas as pd
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

years = [  '1999', '2000' ,'2001', '2002', '2003', '2004', '2005',
           '2006', '2007', '2008', '2009', '2010', '2011', '2012',
           '2013', '2014', '2015', '2016', '2017', '2018', '2019'  ]

def get_best_x_players(year, x):
    stats = pd.read_csv('~/nba-dl/data/player-stats/{}_player_adv_stats.csv'.format(year))
    stats = stats[stats.G > 30] 
    best = stats.sort_values(by=['PER'], ascending=False)
    best_players = best.head(x)
    best_dict = {}
    for row, series in best_players.iterrows():
        best_dict[series['Player']] = series['PER']
    with open(os.path.expanduser('~/nba-dl/data/best-players/{}.csv'.format(year)), 'w+') as f:
        f.write(json.dumps(best_dict, indent=4))

if __name__ == "__main__":
    for year in years:
        logger.info('Preparing best players for {}'.format(year))
        get_best_x_players(year, 100)