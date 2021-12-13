import csv
import requests

countries = []
countrylist = []
if __name__ == '__main__':
    with open("countrylist.csv") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            row = str(row)
            countries.append(row)
    for i in range(len(countries)):
        # print(i)
        m = countries[i][2:-2]
        countrylist.append(m)
    print(countrylist[0])
    r = requests.get('https://en.wikipedia.org/wiki/Afghanistan', timeout=20)
    print(r.text)
