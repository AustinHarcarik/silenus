import pandas as pd
import bs4 as bs
import urllib.request
import ssl
import re
import math

ssl._create_default_https_context = ssl._create_unverified_context

base_url = 'https://beerxchange.com/users'
source = urllib.request.urlopen(base_url)
soup = bs.BeautifulSoup(source,'lxml')

total_users = soup.find(id = "homeTitle").text
total_users = float(''.join(c for c in total_users if c.isdigit()))

n_iters = math.ceil(total_users / 10)

usernames = []

user_divs = soup.find_all("h4", {"class": "media-heading"})
for i in range(len(user_divs)): 
    user = user_divs[i].text
    user = re.sub('\s+',' ', user)
    usernames.append(user)

for iter in range(1, n_iters): 
    url = base_url + f'?p={iter}'
    source = urllib.request.urlopen(url)
    soup = bs.BeautifulSoup(source,'lxml')
    user_divs = soup.find_all("h4", {"class": "media-heading"})
    for i in range(len(user_divs)): 
        user = user_divs[i].text
        user = re.sub('\s+',' ', user)
        usernames.append(user)

output = pd.DataFrame(usernames, columns=['user'])
output.to_csv('usernames.csv', index = False)