import pandas as pd
import bs4 as bs
import urllib.request
import re
import argparse
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
import os
import time

month_map = {
    "Jan":"01", 
    "Feb":"02", 
    "Mar":"03", 
    "Apr":"04", 
    "May":"05", 
    "Jun":"06", 
    "Jul":"07", 
    "Aug":"08", 
    "Sep":"09", 
    "Oct":"10", 
    "Nov":"11", 
    "Dec":"12"
}

data_types = {
    "check_in_id":"int",
    "username":"str", 
    "check_in_ts":"datetime64", 
    "beer":"str", 
    "beer_id":"int", 
    "beer_url_suffix":"str",
    "brewery":"str", 
    "beer_style":"str", 
    "user_rating":"float", 
    "global_rating":"float", 
    "abv":"float", 
    "ibu":"int"
}

def scrape_beer(user, beer_div, detail_div):
    check_in_id = detail_div.find_all("p", {"class":"date"})[1].find("a", href = True)["href"][:-1]
    check_in_id_reversed = check_in_id[::-1]
    check_in_id = int(check_in_id_reversed.split('/')[0][::-1])

    beer = beer_div.find("p", {"class":"name"}).text

    beer_url_suffix = beer_div.find("p", {"class":"name"}).find("a", href = True)["href"]

    beer_url_suffix_reversed = beer_url_suffix[::-1]
    beer_id = int(beer_url_suffix_reversed.split('/')[0][::-1])

    brewery = beer_div.find("p", {"class":"brewery"}).text

    beer_style = beer_div.find("p", {"class":"style"}).text

    ratings = beer_div.find_all("div", {"class":"you"})
    if len(ratings) < 2: 
        user_rating = None
        global_rating = None
    else: 
        user_rating = ratings[0].text
        user_rating = user_rating[user_rating.find("(")+1:user_rating.find(")")]
        global_rating = ratings[1].text
        global_rating = global_rating[global_rating.find("(")+1:global_rating.find(")")]
        if user_rating == 'N/A': 
            user_rating = None
        else: 
            user_rating = float(user_rating)
        if global_rating == 'N/A': 
            global_rating = None
        else: 
            global_rating = float(global_rating)

    abv = detail_div.find("p", {"class":"abv"}).text.strip()
    abv = abv.replace('No', '0')
    abv = round(float(re.findall(r"\d+(?:\.\d+)?", abv)[0]) / 100, 3)

    ibu = detail_div.find("p", {"class":"ibu"}).text.strip()
    ibu = ibu.replace(' IBU', '')
    ibu = int(ibu.replace('No', '0'))

    check_in_ts = detail_div.find("abbr").text
    check_in_ts = check_in_ts[5:25]
    day = check_in_ts[0:2]
    month = month_map[check_in_ts[3:6]]
    year = check_in_ts[7:11]
    time = check_in_ts[12:25]
    check_in_ts = f'{year}-{month}-{day} {time}'

    beer_dict = {
        "check_in_id":check_in_id,
        "username":user,
        "check_in_ts":check_in_ts, 
        "beer":beer, 
        "beer_id":beer_id,
        "beer_url_suffix":beer_url_suffix,
        "brewery":brewery, 
        "beer_style":beer_style, 
        "user_rating":user_rating, 
        "global_rating":global_rating, 
        "abv":abv, 
        "ibu":ibu
    }

    return(beer_dict)

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

    username_query = f'select * from beerxchange_users order by username'
    usernames = pd.read_sql(username_query, con = engine)['username']

    for username in usernames:
        if verbose:
            print(f'scraping check ins for {username}')
        output_list = []

        url = f'https://untappd.com/user/{username}/beers'

        try: 
            source = urllib.request.urlopen(url).read()
        except: 
            continue

        soup = bs.BeautifulSoup(source,'lxml')

        beer_divs = soup.find_all("div", {"class": "beer-details"})
        detail_divs = soup.find_all("div", {"class": "details"})

        n_check_ins = len(beer_divs)

        if n_check_ins == 0: 
            continue

        for i in range(n_check_ins):
            scraped = scrape_beer(username, beer_divs[i], detail_divs[i])
            output_list.append(scraped)

        output_df = pd.DataFrame(output_list)
        output_df = output_df.astype(data_types)

        t = tuple(list(output_df['check_in_id'].values))
        if n_check_ins == 1: 
            delete_query = f"delete from ratings where check_in_id = {output_df['check_in_id'].values[0]}"
        else: 
            delete_query = "delete from ratings where check_in_id in {}".format(t)
        engine.execute(delete_query)

        output_df.to_sql(name = table, con = engine, index = False, if_exists = "append")

        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'scrape untappd ratings and beer info')

    parser.add_argument('--verbose', help = 'verbose output', default = True, type = bool)
    parser.add_argument('--db', help = 'postgres database name', default = 'null', type = str)
    parser.add_argument('--db_username', help = 'postgres database username', default = 'null', type = str)
    parser.add_argument('--db_password', help = 'postgres database password', default = 'null', type = str)
    parser.add_argument('--host', help = 'postgres db hostname', default = 'null', type = str)
    parser.add_argument('--port', help = 'postgres db port', default = 'null', type = str)
    parser.add_argument('--table', help = 'postgres table name', default = 'ratings', type = str)

    args = parser.parse_args()

    main(args)
