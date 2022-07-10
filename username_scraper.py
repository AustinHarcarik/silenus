import math
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

driver_path = "C:\Program Files (x86)\chromedriver"
usernames_url = "https://www.beerxchange.com/users"

driver = webdriver.Chrome(driver_path)

driver.get(usernames_url)

total_users = driver.find_element(By.ID, "homeTitle").text
total_users = int(''.join(c for c in total_users if c.isdigit()))
n_iters = math.ceil(total_users / 10)
remainder = total_users % 10
max_range = 12 # 10 users per page, divs range from 2 to 11

usernames = []
count = 1
while count <= n_iters:
    if count == n_iters:
        max_range = remainder + 1
    for user in range(2, max_range):
        username = driver.find_element(By.XPATH, f'/html/body/div[2]/section/div/div/div[{user}]/div/div[1]/div/div/h4/a').text
        usernames.append(username)
    time.sleep(3)
    driver.find_element(By.XPATH, "/html/body/div[2]/section/div/div/div[12]/ul/li[3]/a").click()
    count += 1
    output = pd.DataFrame(usernames, columns = ["username"])
    output.to_csv('usernames.csv')

driver.quit()