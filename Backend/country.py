import csv
from urllib.request import urlopen
from bs4 import BeautifulSoup



countries = []
countrylst = []
countrylistnew = []

def countrylistfunc():
    with open("countrylist.csv") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            row = str(row)
            countries.append(row)
    for i in range(len(countries)):
        # print(i)
        m = countries[i][2:-2]
        countrylst.append(m)
    for j in countrylst:
        remspace = j.replace(' ','_')
        countrylistnew.append(remspace)
    return countrylistnew
if __name__ == '__main__':
    countrylist = countrylistfunc()
    print(countrylist)
    for k in countrylist:
        url = 'https://en.wikipedia.org/wiki/' + k
        try:
            page = urlopen(url)
        except:
            print("Error opening the URL")
        soup = BeautifulSoup(page, 'html.parser')
        content = soup.find('div', {"class": "mw-parser-output"})
        article = ''
        for i in content.findAll('p'):
            article = article + ' ' + i.text
        # print(article)
        with open('scraped_text.txt', 'a', encoding="utf-8") as f:
            f.write(k)
            f.write(article)