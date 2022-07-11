import pandas as pd
import bs4 as bs
import urllib.request
import ssl
import re
import argparse

def main(params):
    page_start = int(params.page_start)
    page_end = int(params.page_end)
    include_first_page = params.include_first_page

    base_url = 'https://www.beerxchange.com/users'

    file_name = f'usernamesp{page_start}-p{page_end}.csv'

    ssl._create_default_https_context = ssl._create_unverified_context

    usernames = []

    if include_first_page: 
        source = urllib.request.urlopen(base_url)
        soup = bs.BeautifulSoup(source,'lxml')
        user_divs = soup.find_all("h4", {"class": "media-heading"})
        for i in range(len(user_divs)): 
            user = user_divs[i].text
            user = re.sub('\s+',' ', user)
            usernames.append(user)

    for page in range(page_start, page_end + 1): 
        url = base_url + f'?p={page}'
        source = urllib.request.urlopen(url)
        soup = bs.BeautifulSoup(source,'lxml')
        user_divs = soup.find_all("h4", {"class": "media-heading"})
        for i in range(len(user_divs)): 
            user = user_divs[i].text
            user = re.sub('\s+',' ', user)
            usernames.append(user)

    output = pd.DataFrame(usernames, columns=['user'])
    output.to_csv(file_name, index = False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'scrape untappd usernames from beerxchange.com')

    parser.add_argument('--page_start', help = 'page to start on', default = 1)
    parser.add_argument('--page_end', help = 'page to end on', default = 10)
    parser.add_argument('--include_first_page', help = 'very first page has no number in url', default = False)

    args = parser.parse_args()

    main(args)