from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd

driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
if __name__ == '__main__':
    # try:

    driver.get('https://www.worldometers.info/coronavirus/country/mexico/')
    page = driver.page_source
    # except:
    #     print("Error opening the URL")
    soup = BeautifulSoup(page, 'html.parser')
    content = soup.findAll('div', {"class": "maincounter-number"})
    print(content[0].text)
    print(content[1].text)
    # article = ''
    # result = []
    # k = 'Afghanistan'
    # for i in content.findAll('p'):
    #     article = article + ' ' + i.text
    #     result.append(article)
    # df = pd.DataFrame({'Country Name': k, 'Content': result})
    # df.to_csv('countrydetails.csv', index=False, encoding='utf-8')
    # print(article)
    # with open('scraped_text.txt', 'a', encoding="utf-8") as f:
    #     f.write("Afghanistan")
    #     f.write(article)