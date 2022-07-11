import pandas as pd
import numpy as np
import bs4 as bs
import urllib.request
import ssl
import argparse
from datetime import datetime

def main(params):
    n_users = params.n_users

    hour = datetime.now().hour

    page_ranges = np.linspace(1, n_users / 10, 25, dtype = int)
    
    page_start = page_ranges[hour]
    page_end = page_ranges[hour + 1] - 1

    base_url = 'https://www.beerxchange.com/users'

    file_name = f'usernames/usernamesp{page_start}-p{page_end}.csv'

    ssl._create_default_https_context = ssl._create_unverified_context

    usernames = []

    if hour == 0: 
        source = urllib.request.urlopen(base_url)
        soup = bs.BeautifulSoup(source,'lxml')
        user_divs = soup.find_all("h4", {"class": "media-heading"})
        for i in range(len(user_divs)): 
            user = user_divs[i].text
            user = user.lstrip()
            user = user.split(' ', 1)[0]
            user = user.strip()
            usernames.append(user)

    for page in range(page_start, page_end + 1): 
        url = base_url + f'?p={page}'
        source = urllib.request.urlopen(url)
        soup = bs.BeautifulSoup(source,'lxml')
        user_divs = soup.find_all("h4", {"class": "media-heading"})
        for i in range(len(user_divs)): 
            user = user_divs[i].text
            user = user.lstrip()
            user = user.split(' ', 1)[0]
            user = user.strip()
            usernames.append(user)

    output = pd.DataFrame(usernames, columns=['user'])
    output.to_csv(file_name, index = False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'scrape untappd usernames from beerxchange.com')

    parser.add_argument('--verbose', help = 'verbose output', default = True, type = bool)
    parser.add_argument('--n_users', help = 'total number of users', default = 19568, type = int)

    args = parser.parse_args()

    main(args)