import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import bs4

driver_path = "C:\Program Files (x86)\chromedriver"
usernames_url = "https://www.beerxchange.com/users"

driver = webdriver.Chrome(driver_path)

driver.get(usernames_url)

total_users = driver.find_element(By.ID, "homeTitle").text
print(total_users)

# usernames = []

# count = 1
# while count <= 10:
#     for user in range(2, 12):
#         username = driver.find_element(By.XPATH, f'/html/body/div[2]/section/div/div/div[{user}]/div/div[1]/div/div/h4/a').text
#         usernames.append(username)
#     driver.find_element(By.XPATH, "/html/body/div[2]/section/div/div/div[12]/ul/li[3]/a").click()
#     count += 1

# print(usernames)

# username_1 = driver.find_element(By.XPATH, '/html/body/div[2]/section/div/div/div[2]/div/div[1]/div/div/h4/a').text
# username_2 = driver.find_element(By.XPATH, '/html/body/div[2]/section/div/div/div[3]/div/div[1]/div/div/h4/a').text
# print(username_1)
# print(username_2)

driver.find_element(By.XPATH, "/html/body/div[2]/section/div/div/div[12]/ul/li[3]/a").click()
# driver.find_element(By.XPATH, "/html/body/div[2]/section/div/div/div[12]/ul/li[3]/a").click()

# /html/body/div[2]/section/div/div/div[2]/div/div[1]/div/div/h4/a

# /html/body/div[2]/section/div/div/div[11]/div/div[1]/div/div/h4/a