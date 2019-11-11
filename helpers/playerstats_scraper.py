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

years = [  '1999', '2000' ,'2001', '2002', '2003', '2004', '2005',
           '2006', '2007', '2008', '2009', '2010', '2011', '2012',
           '2013', '2014', '2015', '2016', '2017', '2018', '2019'  ]

def write_to_csv(name, headers, data_table):
    
    logger.info("Creating csv file...")
    with open(name, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        for data_row in data_table:
            csv_writer.writerow(data_row)

def scrape_league_standings(year, tableid):
    url = 'https://www.basketball-reference.com/leagues/NBA_{}_advanced.html'.format(year)
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
    for year in years:
        logger.info('Getting league standings for {}'.format(year))
        headers, table = scrape_league_standings(year, 'advanced_stats')
        write_to_csv('data/player-stats/{}_player_adv_stats.csv'.format(year), headers, table)

if __name__ == "__main__":
    main()

