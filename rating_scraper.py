import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

driver_path = "C:\Program Files (x86)\chromedriver"

usernames = list(pd.read_csv("usernames_1.csv")['username'])

driver = webdriver.Chrome(driver_path)

users = []
beers = []
breweries = []
kinds = []
ratings = []
abvs = []
ibus = []

for username in usernames:
    print(username)
    driver.get(f'https://untappd.com/user/{username}/beers')

    n_beers = driver.find_element(By.CLASS_NAME, "stat").text
    print(n_beers)
    pass
    n_beers = int(''.join(c for c in n_beers if c.isdigit()))
    print(n_beers)
    if n_beers == 0:
        pass 
    range_max = min(n_beers, 25) + 1
    
    # can only get last 25 beers before being stopped by captcha
    for beer_num in range(1, range_max):
        user = username
        beer = driver.find_element(By.XPATH, f'//*[@id="slide"]/div/div/div[1]/div/div[2]/div/div[5]/div/div[{beer_num}]/div[1]/p[1]/a').text
        brewery = driver.find_element(By.XPATH, f'//*[@id="slide"]/div/div/div[1]/div/div[2]/div/div[5]/div/div[{beer_num}]/div[1]/p[2]/a').text 
        kind = driver.find_element(By.XPATH, f'//*[@id="slide"]/div/div/div[1]/div/div[2]/div/div[5]/div/div[{beer_num}]/div[1]/p[3]').text 
        rating = driver.find_element(By.XPATH, f'//*[@id="slide"]/div/div/div[1]/div/div[2]/div/div[5]/div/div[{beer_num}]/div[1]/div/div[1]/p').text 
        abv = driver.find_element(By.XPATH, f'//*[@id="slide"]/div/div/div[1]/div/div[2]/div/div[5]/div/div[{beer_num}]/div[2]/p[1]').text
        ibu = driver.find_element(By.XPATH, f'//*[@id="slide"]/div/div/div[1]/div/div[2]/div/div[5]/div/div[{beer_num}]/div[2]/p[2]').text 

        users.append(user)
        beers.append(beer)
        breweries.append(brewery)
        kinds.append(kind)
        ratings.append(rating)
        abvs.append(abv)
        ibus.append(ibu)

output_dict = {
    "user":users,
    "beer":beers, 
    "brewery":breweries, 
    "kind":kinds, 
    "rating":ratings, 
    "abv":abvs, 
    "ibu":ibus
}

output = pd.DataFrame(output_dict)
output.to_csv('ratings.csv', index = False)

driver.quit()