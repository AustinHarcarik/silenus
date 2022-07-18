import pandas as pd
import bs4 as bs
import urllib.request
import ssl
import argparse
import time
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
import os

def main(params):
    load_dotenv(find_dotenv())
    
    verbose = params.verbose
    page_start = params.page_start
    page_end = params.page_end
    include_first_page = params.include_first_page
    db = params.db
    db_username = params.db_username
    db_password = params.db_password
    host = params.host
    port = params.port
    table = params.table

    if db == 'null':
        db = os.environ.get('DB')
    if db_username == 'null':
        db_username = os.environ.get('DB_USERNAME')
    if db_password == 'null':
        db_password = os.environ.get('DB_PASSWORD')
    if host == 'null': 
        host = os.environ.get('HOST')
    if port == 'null': 
        port = os.environ.get('PORT')
    if table == 'null':
        table = os.environ.get('TABLE')

    engine = create_engine(f'postgresql://{db_username}:{db_password}@{host}:{port}/{db}')
    engine.connect()

    base_url = 'https://www.beerxchange.com/users'

    ssl._create_default_https_context = ssl._create_unverified_context

    if include_first_page: 
        usernames = []

        source = urllib.request.urlopen(base_url)
        soup = bs.BeautifulSoup(source,'lxml')
        user_divs = soup.find_all("h4", {"class": "media-heading"})
        if verbose:
            print('scraping first page')
        for i in range(len(user_divs)): 
            user = user_divs[i].text
            user = user.lstrip()
            user = user.split(' ', 1)[0]
            user = user.strip()
            usernames.append(user)

        delete_query = f'delete from {table} where username in {usernames}'
        delete_query = delete_query.replace('[', '(')
        delete_query = delete_query[::-1]
        delete_query = delete_query.replace(']', ')')
        delete_query = delete_query[::-1]
        engine.execute(delete_query)

        output = pd.DataFrame(usernames, columns=['username'])
        output.to_sql(name = table, con = engine, index = False, if_exists = "append")

    for page in range(page_start, page_end): 
        if verbose:
            print(f'scraping page {page}')

        usernames = []

        url = base_url + f'?p={page}'
        try: 
            source = urllib.request.urlopen(url)
        except: 
            return

        soup = bs.BeautifulSoup(source,'lxml')
        user_divs = soup.find_all("h4", {"class": "media-heading"})
        for i in range(len(user_divs)): 
            user = user_divs[i].text
            user = user.lstrip()
            user = user.split(' ', 1)[0]
            user = user.strip()
            usernames.append(user)

        delete_query = f'delete from {table} where username in {usernames}'
        delete_query = delete_query.replace('[', '(')
        delete_query = delete_query[::-1]
        delete_query = delete_query.replace(']', ')')
        delete_query = delete_query[::-1]
        engine.execute(delete_query)

        output = pd.DataFrame(usernames, columns=['username'])
        output.to_sql(name = table, con = engine, index = False, if_exists = "append")
        
        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'scrape untappd usernames from beerxchange.com')

    parser.add_argument('--verbose', help = 'verbose output', default = True, type = bool)
    parser.add_argument('--page_start', help = 'page to start on', default = 1, type = int)
    parser.add_argument('--page_end', help = 'page to end on', default = 25, type = int)
    parser.add_argument('--include_first_page', help = 'first page has no page number', default = False, type = bool)
    parser.add_argument('--db', help = 'postgres database name', default = 'null', type = str)
    parser.add_argument('--db_username', help = 'postgres database username', default = 'null', type = str)
    parser.add_argument('--db_password', help = 'postgres database password', default = 'null', type = str)
    parser.add_argument('--host', help = 'postgres db hostname', default = 'null', type = str)
    parser.add_argument('--port', help = 'postgres db port', default = 'null', type = str)
    parser.add_argument('--table', help = 'postgres table name', default = 'beerxchange_users', type = str)

    args = parser.parse_args()

    main(args)