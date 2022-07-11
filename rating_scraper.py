import pandas as pd
import bs4 as bs
import urllib.request
import re

usernames = pd.read_csv('usernames.csv')['user']

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

# output_schema = {
#     "user":"|S50", 
#     "beer":"|S100", 
#     "brewery":"|S100", 
#     "style":"|S100", 
#     "user_rating":"float64", 
#     "abv":"float64", 
#     "ibu":"int64", 
#     "check_in_ts":"datetime64[ns]"
# }

def scrape_beer(user, beer_div, detail_div):
    beer = beer_div.find("p", {"class":"name"}).text

    brewery = beer_div.find("p", {"class":"brewery"}).text

    style = beer_div.find("p", {"class":"style"}).text

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
        "style":style, 
        "user_rating":user_rating, 
        "global_rating":global_rating, 
        "abv":abv, 
        "ibu":ibu, 
        "check_in_ts":check_in_ts
    }

    output_list.append(beer_dict)

output_list = []

for username in usernames:
    url = f'https://untappd.com/user/{username}/beers'

    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source,'lxml')

    beer_divs = soup.find_all("div", {"class": "beer-details"})
    detail_divs = soup.find_all("div", {"class": "details"})

    n_check_ins = len(beer_divs)

    if n_check_ins == 0:
        pass

    for i in range(n_check_ins):
        scrape_beer(username, beer_divs[i], detail_divs[i])

output_df = pd.DataFrame(output_list)
# output_df = output_df.astype(output_schema)

output_df.to_csv('ratings.csv', index = False)
