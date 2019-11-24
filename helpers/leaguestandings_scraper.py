'''
leaguestandings_scraper - python module for collecting daily league standings

- gets data from https://www.basketball-reference.com/
- creates file with league standings for every date in game inventory
- drop data to csv file

usage: python3 leaguestandings_scraper.py

'''

import requests
from bs4 import BeautifulSoup
import logging
import sys
import csv
import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def write_to_csv(name, headers, data_table):
    
    logger.info("Creating csv file...")
    with open(name, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        for data_row in data_table:
            csv_writer.writerow(data_row)

def get_all_dates():
    game_inventory = pd.read_csv('~/nba-dl/data/game-inventory/all-games-corrected.csv')
    dates = []
    logger.info('Getting dates for all collected matches...')
    for row, index in game_inventory.iterrows():
        if index['GAME_DATE'] not in dates:
            dates.append(index['GAME_DATE'])
    
    return dates

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

def main():
    dates = get_all_dates()
    for date in dates:
        logger.info('Getting league standings for {}'.format(date))
        headers_eastern, table_eastern = scrape_league_standings(date, 'standings_e')
        headers_western, table_western = scrape_league_standings(date, 'standings_w')
        if headers_eastern == headers_western:
            headers = headers_eastern
        table = table_eastern + table_western
        write_to_csv('data/league-standings/{}_league_standings.csv'.format(date), headers, table)

if __name__ == "__main__":
    main()

