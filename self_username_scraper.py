import pandas as pd
import bs4 as bs
import urllib.request
import argparse
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
import os
import time

base_url = 'https://untappd.com'

def main(params):
    load_dotenv(find_dotenv())

    verbose = params.verbose
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

    beer_query = '''select distinct(beer_id), beer, beer_url_suffix 
                    from ratings a
                    where a.username not in 
                    (
	                    select username from beerxchange_users
                    ) '''
    beers = pd.read_sql(beer_query, con = engine)

    for i in range(len(beers)):
        if verbose:
            print(f"scraping check ins for {beers['beer'][i]}")

        url = base_url + beers['beer_url_suffix'][i]

        try: 
            source = urllib.request.urlopen(url).read()
        except: 
            continue

        soup = bs.BeautifulSoup(source,'lxml')

        user_divs = soup.find_all("a", {"class":"user"}, href = True)

        if len(user_divs == 0): 
            continue

        usernames = [user_divs[i]['href'].split('/user/')[1] for i in range(len(user_divs))]
        t = tuple(usernames)

        usernames_df = pd.DataFrame(usernames, columns=['username'])

        if len(user_divs == 1): 
            delete_query = f"delete from all_users where username = {usernames[0]}"
        else: 
            delete_query = "delete from all_users where username in {}".format(t)
        engine.execute(delete_query)

        usernames_df.to_sql(name = table, con = engine, index = False, if_exists = "append")

        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'scrape untappd ratings and beer info')

    parser.add_argument('--verbose', help = 'verbose output', default = True, type = bool)
    parser.add_argument('--db', help = 'postgres database name', default = 'null', type = str)
    parser.add_argument('--db_username', help = 'postgres database username', default = 'null', type = str)
    parser.add_argument('--db_password', help = 'postgres database password', default = 'null', type = str)
    parser.add_argument('--host', help = 'postgres db hostname', default = 'null', type = str)
    parser.add_argument('--port', help = 'postgres db port', default = 'null', type = str)
    parser.add_argument('--table', help = 'postgres table name', default = 'all_users', type = str)

    args = parser.parse_args()

    main(args)
