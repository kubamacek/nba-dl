from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
import requests
import utils
import sys
from bs4 import BeautifulSoup
import csv

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

season_parts = ['Regular Season', 'Playoffs']

date = datetime.now()
one_day_before = (date - timedelta(days=1)).strftime('%Y-%m-%d')

def generate_last_seasons():
    seasons = []
    current_season = season = utils.game_date_to_season(date.strftime('%Y-%m-%d'))
    seasons.append(current_season)
    year =  current_season.split('-')[1]
    for i in range(1,6):
        year = int(year) - 1
        prev_year = '20' + str(year - 1)
        season = '{}-{}'.format(prev_year, year)
        seasons.append(season)
    return seasons
    
def get_todays_data():
    api_date = date.strftime('%Y%m%d')
    logger.info("Getting data for {} ...".format(date.strftime('%Y-%m-%d')))
    url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={}'.format(api_date)
    response = requests.get(url)
    raw_data = response.json()
    return raw_data

def generate_matches(data):
    events = data['events']
    matches = [event['name'] for event in events]
    date_for_model = date.strftime('%Y-%m-%d')
    formatted_matches = []
    for match in matches:
        match_dict = {}
        away_team, home_team = match.split(' at ')
        match_dict['HOME_TEAM_NAME'] = home_team
        match_dict['AWAY_TEAM_NAME'] = away_team
        match_dict['GAME_DATE'] = date_for_model
        formatted_matches.append(match_dict)
    return formatted_matches

def write_to_csv(name, headers, data_table):
    
    logger.debug("Creating csv file...")
    with open(name, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        for data_row in data_table:
            csv_writer.writerow(data_row)

def scrape_league_standings(date, tableid):
    year, month, day = date.split('-')
    url = 'https://www.basketball-reference.com/friv/standings.fcgi?month={}&day={}&year={}&lg_id=NBA'.format(month, day, year)
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        logger.error(e)
        sys.exit(1)

    table_data = []
    soup = BeautifulSoup(r.text, 'html5lib')
    table = soup.find(id=tableid)
    table_head = table.find('thead')
    headers = [element.text.strip() for element in table_head.find_all('th')]
    headers = [header for header in headers if header]
    headers[0] = 'Team'
    table_body = table.find('tbody')
    rows = table_body.findAll('tr', {'class': 'full_table'})
    for row in rows:
        cols = row.find_all('td')
        if row.find('th'):
            cols.insert(0, row.find('th'))
        cols = [element.text.strip().replace('*', '') for element in cols]
        table_data.append([element for element in cols if element])

    return headers, table_data

def get_daily_league_standings():
    logger.info('Getting league standings...')
    headers_eastern, table_eastern = scrape_league_standings(one_day_before, 'standings_e')
    headers_western, table_western = scrape_league_standings(one_day_before, 'standings_w')
    if headers_eastern == headers_western:
        headers = headers_eastern
    table = table_eastern + table_western
    write_to_csv('data/league-standings/{}_league_standings.csv'.format(one_day_before), headers, table)

def create_game_inventory():
    game_inventory = pd.DataFrame()
    seasons = generate_last_seasons()
    for season in seasons:
        for season_part in season_parts:
            game_finder = leaguegamefinder.LeagueGameFinder(season_type_nullable=season_part, season_nullable=season, league_id_nullable='00')
            games = game_finder.get_data_frames()[0]
            game_inventory = game_inventory.append(games)
            logger.debug("Appending {} games for {} season to game-inventory...".format(season_part, season))
            time.sleep(5)
    return game_inventory

def create_dataset(games, game_inventory):
    columns = ['HOME_TEAM_NAME', 'AWAY_TEAM_NAME','GAME_DATE', 'HPO', 'APO', 'HGLW', 'AGLW',
               'HLGR', 'ALGR', 'HLH2HR', 'ALH2HR', 'HTFR', 'ATFR', 'HSWR', 'ASWR', 'HSPS', 'ASPS', 'HSPL', 'ASPL']
    df = pd.DataFrame(columns=columns)
    for game in games:
        logger.info("Preparing data for {} @ {}".format(game['AWAY_TEAM_NAME'], game['HOME_TEAM_NAME']))
        game_row = {}
        game_row['HOME_TEAM_NAME'] = game['HOME_TEAM_NAME']
        game_row['AWAY_TEAM_NAME'] = game['AWAY_TEAM_NAME']
        game_row['GAME_DATE'] = game['GAME_DATE']
        game_row['HPO'] = utils.get_home_team_preseason_odds(game)
        game_row['APO'] = utils.get_away_team_preseason_odds(game)
        game_row['HGLW'] = utils.home_games_in_last_week(game, game_inventory)
        game_row['AGLW'] = utils.away_games_in_last_week(game, game_inventory)
        game_row['HLGR'] = utils.home_last_x_games_ratio(game, game_inventory, 10)
        game_row['ALGR'] = utils.away_last_x_games_ratio(game, game_inventory, 10)
        game_row['HLH2HR'] = utils.home_last_10_games_h2h_ratio(game, game_inventory)
        game_row['ALH2HR'] = utils.away_last_10_games_h2h_ratio(game, game_inventory)
        game_row['HTFR'] = utils.team_home_form_ratio(game, game_inventory, 10)
        game_row['ATFR'] = utils.team_away_form_ratio(game, game_inventory, 10)
        # hack for league standings - get them from day before - basketball reference issue
        game["GAME_DATE"] = one_day_before
        game_row['HSWR'] = utils.get_home_team_season_ratio(game)
        game_row['ASWR'] = utils.get_away_team_season_ratio(game)
        game_row['HSPS'] = utils.get_home_team_season_avg_pts_scored(game)
        game_row['ASPS'] = utils.get_away_team_season_avg_pts_scored(game)
        game_row['HSPL'] = utils.get_home_team_season_avg_pts_lost(game)
        game_row['ASPL'] = utils.get_away_team_season_avg_pts_lost(game)
        df = df.append(game_row, ignore_index=True)
    
    df.to_csv('data/realtime/{}.csv'.format(date.strftime('%Y-%m-%d')), index=False)
    logger.info("Finished!")

def main():
    logger.info("Started creating matches dataset for today - {}".format(date.strftime('%Y-%m-%d')))
    todays_data = get_todays_data()
    matches_list = generate_matches(todays_data)
    get_daily_league_standings()
    logger.info("Started creating game inventory...")
    game_inventory = create_game_inventory()
    logger.info("Started creating matches dataset for {}".format(date.strftime('%Y-%m-%d')))
    create_dataset(matches_list, game_inventory)

if __name__ == '__main__':
    main()