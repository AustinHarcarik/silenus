from numpy import dtype
import pandas as pd
import bs4 as bs
import urllib.request
import re
import argparse
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
import os

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

def scrape_beer(user, beer_div, detail_div):
    beer = beer_div.find("p", {"class":"name"}).text

    brewery = beer_div.find("p", {"class":"brewery"}).text

    beer_style = beer_div.find("p", {"class":"style"}).text

    ratings = beer_div.find_all("div", {"class":"you"})
    user_rating = ratings[0].text
    user_rating = float(user_rating[user_rating.find("(")+1:user_rating.find(")")])
    global_rating = ratings[1].text
    global_rating = global_rating[global_rating.find("(")+1:global_rating.find(")")]

    abv = detail_div.find("p", {"class":"abv"}).text.strip()
    abv = float(re.findall(r"\d+(?:\.\d+)?", abv)[0]) / 100

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
        "user":user,
        "beer":beer, 
        "brewery":brewery, 
        "style":beer_style, 
        "user_rating":user_rating, 
        "global_rating":global_rating, 
        "abv":abv, 
        "ibu":ibu, 
        "check_in_ts":check_in_ts
    }

    return(beer_dict)

def main(params):
    load_dotenv(find_dotenv())

    verbose = params.verbose
    user_start = params.user_start
    user_end = params.user_end
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

    username_query = f'select * from {table} limit 10'
    usernames = pd.read_sql(username_query, con = engine)['username']

    output_list = []

    for username in usernames:
        print(username)
        url = f'https://untappd.com/user/{username}/beers'

        source = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(source,'lxml')

        beer_divs = soup.find_all("div", {"class": "beer-details"})
        detail_divs = soup.find_all("div", {"class": "details"})

        n_check_ins = len(beer_divs)

        if n_check_ins == 0:
            pass

        for i in range(n_check_ins):
            scraped = scrape_beer(username, beer_divs[i], detail_divs[i])
            output_list.append(scraped)

    output_df = pd.DataFrame(output_list)
    print(output_df.dtypes)

    # output_df.to_csv('ratings.csv', index = False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'scrape untappd ratings and beer info')

    parser.add_argument('--verbose', help = 'verbose output', default = True, type = bool)
    parser.add_argument('--user_start', help = 'username number to start at', default = 1, type = int)
    parser.add_argument('--user_end', help = 'username number to end at', default = 100, type = int)
    parser.add_argument('--db', help = 'postgres database name', default = 'null', type = str)
    parser.add_argument('--db_username', help = 'postgres database username', default = 'null', type = str)
    parser.add_argument('--db_password', help = 'postgres database password', default = 'null', type = str)
    parser.add_argument('--host', help = 'postgres db hostname', default = 'null', type = str)
    parser.add_argument('--port', help = 'postgres db port', default = 'null', type = str)
    parser.add_argument('--table', help = 'postgres table name', default = 'null', type = str)

    args = parser.parse_args()

    main(args)
