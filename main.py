import os
import time
import config
import numpy as np
import spintax
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from random import randint, randrange, random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager as CM
from lxml.html import fromstring
import requests
from itertools import cycle
import json


def login(email, password, proxy=None):

    options = uc.ChromeOptions()
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    if proxy is not None:
        options.add_argument('--proxy-server=%s' % proxy)

    driver = uc.Chrome(options=options, executable_path=CM().install(),use_subprocess=True)
    driver.get('https://accounts.google.com/ServiceLogin')
    print("started Google Login with "+email)


    wait=WebDriverWait(driver, 50);
    email_field=wait.until(EC.visibility_of_element_located((By.ID,'identifierId')))
    for char in email:
        email_field.send_keys(char)

    wait.until(EC.visibility_of_element_located((By.ID,"identifierNext"))).click()
    time.sleep(3)
    password_field=wait.until(EC.visibility_of_element_located((By.NAME,'Passwd')))
    for char in password:
        password_field.send_keys(char)
    wait.until(EC.visibility_of_element_located((By.ID,"passwordNext"))).click()
    time.sleep(3)
    print("logged in successfully")
    driver.get("https://www.youtube.com/")
    time.sleep(3)
    print("-- returned --")

    return driver
# comment section
def getComment():
    comment = "amazing"
    with open('comments.txt', 'r',encoding="utf8") as f:
        comments = [line.strip() for line in f]
        r = np.random.randint(0, len(comments))
        comment = comments[r]
    return comment

def check_exists_by_xpath(driver, xpath):
    try:
        wait = WebDriverWait(driver, 50);
        wait.until(EC.visibility_of_element_located((By.XPATH,xpath)))
    except NoSuchElementException:
        return False
    return True

def youtubeActions(driver, urls, comment):

    if len(urls) == 0:
        print("============================================================================================================")
        print('Finished keyword jumping to next one...')
        return []

    # gettin a video link from the list
    url = urls.pop()

    driver.get(url)
    print("Video url:" + url)
    driver.implicitly_wait(1)
    wait = WebDriverWait(driver, 4);
    subscribeText = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="subscribe-button"]/ytd-subscribe-button-renderer/yt-button-shape/button/div/span')))
    time.sleep(2)
    # Subscribe
    if subscribeText.text=='Subscribe':
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="subscribe-button"]/ytd-subscribe-button-renderer/yt-button-shape/button'))).click()
    time.sleep(3)
    # like the video
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, '//*[@id="segmented-like-button"]/ytd-toggle-button-renderer/yt-button-shape/button'))).click()


    time.sleep(2)
    driver.execute_script("window.scrollTo(0, window.scrollY + 500)")
    time.sleep(1)

    comment_box = EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#placeholder-area'))
    WebDriverWait(driver, 4).until(comment_box)

    comment_box1 = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#placeholder-area')))
    ActionChains(driver).move_to_element(
        comment_box1).click(comment_box1).perform()
    add_comment_onit = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#contenteditable-root')))
    add_comment_onit.send_keys(comment)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#submit-button'))).click()
    print("done")

    time.sleep(5)

    return youtubeActions(driver, urls, getComment())

def main(email,password):
    driver = login(email, password)
    wait = WebDriverWait(driver, 50);
    # get keyword list and extract each key
    keywords = [];
    with open('video-titles.txt', 'r', encoding="utf8") as f:
        keywords = [line.strip() for line in f]

    time.sleep(1)
    for random_keyword in keywords:
        driver.get("https://www.youtube.com/")
        keys = spintax.spin(random_keyword)
        time.sleep(2)
        key = wait.until(EC.visibility_of_element_located((By.NAME, 'search_query')))
        for char in keys:
            key.send_keys(char)

        # click search icon
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#search-icon-legacy > yt-icon'))).click()

        time.sleep(3)
        title = wait.until(EC.visibility_of_element_located((By.XPATH,
                                                             '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div[2]/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[1]/div/h3/a')))
        urls = []
        # getting url from href attribute in title
        print(title.get_attribute('href'))
        urls.append(title.get_attribute('href'))
        if urls == []:
            print("There is not videos for this keyword at the moment")
        else:
            youtubeActions(driver, urls, getComment())
    driver.quit()

if __name__ == '__main__':
    with open('email.txt', 'r', encoding="utf8") as f:
        keywords = [line.strip() for line in f]
        for user in keywords:
            email_pass = user.split(",")
            main(email_pass[0],email_pass[1])

