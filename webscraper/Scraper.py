#Scaper.py
#Scrape Trading View For
#1. Stock Indicator Values and ratings ->everything they have lol
#2. Stock News -> Hugiging Face Sentiment Analysis of Headings
#3. Stock Price -> pretty straightforward

#importing libraries for scraper
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import json
from model import get_financial_sentiment
from preprocess import pre_process

def get_stock_indicators(driver):
    wait = WebDriverWait(driver, 10)
    try:
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='button-vll9ujXF' and contains(text(), 'More technicals')]")))
    except:
        driver.quit()
    
    button.click()

    # Now we need to save the elements we want to scrape to our csv
    #Oscillators
    time.sleep(2)
    elements = driver.find_elements(By.CSS_SELECTOR, ".cell-hvDpy38G.largePadding-hvDpy38G")
    if(elements == None):
        driver.quit()

    data = []
    for i in range(0, len(elements), 3):
        # Assuming elements[i], elements[i+1], and elements[i+2] exist
        # You might want to add checks to ensure you have enough elements
        group = {
            'first_element': elements[i].text,
            'second_element': elements[i + 1].text,
            'third_element': elements[i + 2].text
        }
        data.append(group)

# Writing the list of dictionaries to a JSON file
    with open('webscraper/indicators.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_stock_news(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".clamp.svelte-w27v8j")))
        time.sleep(10)
    except:
        driver.quit()
    
    headlines = driver.find_elements(By.CSS_SELECTOR, "p.clamp.svelte-w27v8j")
    headlines = [headline.text for headline in headlines if headline.text != '']
    return headlines

# Above .20 buy, below -.20 sell
def sentiment_analysis_from_headlines(headlines):
    '''
    returns avg positive, negative, and neutral headlines, avg pos, avg, neg, avg neutral 
    '''
    dict = {}
    running_sum = 0
    for headline in headlines:
        sentiment = get_financial_sentiment(headline)
        dict[headline] = (sentiment['positive'], sentiment['neutral'], sentiment['negative'])
        running_sum += 1*sentiment['positive'] + -1*sentiment['negative']
    average = running_sum / len(headlines)
    print(average)
    for headline in dict:
        print(headline)
        print(dict[headline])
        print('\n')

def scrape(ticker):
    # Set up the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Go to the website you want to scrape
    url = "https://www.tradingview.com/chart/?symbol=" + ticker
    driver.get(url)

    # Now, you can find elements by their tag, class, id or other attributes

    #get stock indicators
    get_stock_indicators(driver)

    #reset back to main page so we can get the news
    url = "https://finance.yahoo.com/quote/" + ticker + "/news/"
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".svelte-3a2v0c")))
    except:
        driver.quit()

    #get stock news
    headlines = get_stock_news(driver)
    sentiment_analysis_from_headlines(headlines)

    time.sleep(5)
    # Always remember to close the driver after you're done
    driver.quit()







