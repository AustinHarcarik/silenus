import pandas as pd
import bs4 as bs
import urllib.request
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context

url = url = f'https://beerxchange.com/users'
source = urllib.request.urlopen(url)
soup = bs.BeautifulSoup(source,'lxml')

total_users = soup.find(id = "homeTitle").text
total_users = int(''.join(c for c in total_users if c.isdigit()))

