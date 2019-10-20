'''
preseason-odds-scraper - python module for collecting preseason odds

- gets data from https://www.basketball-reference.com/
- computes probability of winning title from american odds
- drop data to csv file

usage: python3 preseason-odds-scraper.py

'''

import requests
from bs4 import BeautifulSoup
import logging
import sys
import csv

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

seasons = [ '1999-00' ,'2000-01', '2001-02', '2002-03', '2003-04', '2004-05', '2005-06', '2006-07', '2007-08', '2008-09',
          '2009-10', '2010-11', '2011-12', '2012-13', '2013-14', '2014-15', '2015-16', '2016-17', '2017-18', '2018-19' ]

def write_to_csv(name, headers, data_table):
    
    logger.info("Creating csv file...")
    with open(name, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        for data_row in data_table:
            csv_writer.writerow(data_row)

def calculate_probability(odd):
    if '-' in odd:
        probability = ( - (int(odd)) / ( - (int(odd)) + 100 ))
    else:
        odd = odd.replace('+', '') 
        probability = ( 100 / ( int(odd) + 100 ))
    return probability

def append_probability(data_table):
    for data_row in data_table:
        probability = calculate_probability(data_row[1])
        data_row.append(round(probability, 4))

def append_probability_to_headers(headers):
    headers.append('Probability')

def scrape_preseason_odds(season):

    if season == '1999-00':
        year = '2000'
    else:
        year = season.split('-')[0][:2] + season.split('-')[1]
    
    url = 'https://www.basketball-reference.com/leagues/NBA_{}_preseason_odds.html'.format(year)
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        logger.error(e)
        sys.exit(1)
    
    logger.info("Collecting preseason odds for {} season".format(season))
    table_data = []
    soup = BeautifulSoup(r.text, 'html5lib')
    table = soup.find(id='NBA_preseason_odds')
    table_head = table.find('thead')
    headers = [element.text.strip() for element in table_head.find_all('th')]
    headers = [header for header in headers if header]
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols.insert(0, row.find('th'))
        cols = [element.text.strip() for element in cols]
        table_data.append([element for element in cols if element])

    return headers, table_data

def main():
    for season in seasons:
        headers, data = scrape_preseason_odds(season)
        append_probability(data)
        append_probability_to_headers(headers)
        write_to_csv('data/preseason-odds/{}-preseason-odds.csv'.format(season), headers, data)

if __name__ == "__main__":
    main()