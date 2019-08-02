import json
import re
from datetime import datetime
import geograpy
import geopy
import nltk
import math
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from nltk import pos_tag
import nationality_map_new


#   Code from https://github.com/pari08tosh/Inshorts-API/blob/master/inshorts.py
#   Write it to the file and chunk it up
def getNews(filename):
    newsDictionary = {
        'success': True,
        'category': "world",
        'data': []
    }

    try:
        htmlBody = requests.get('https://www.inshorts.com/en/read/' + category)
    except requests.exceptions.RequestException as e:
        newsDictionary['success'] = False
        newsDictionary['errorMessage'] = str(e.message)
        return newsDictionary

    soup = BeautifulSoup(data, 'lxml')
    newsCards = soup.find_all(class_='news-card')

    if not newsCards:
        newsDictionary['success'] = False
        newsDictionary['errorMessage'] = 'Invalid Category'
        return newsDictionary

    for card in newsCards:
        try:
            title = card.find(class_='news-card-title').find('a').text
        except AttributeError:
            title = None
            continue

        if title in titles:
            continue
        titles.add(title)

        try:
            imageUrl = card.find(
                class_='news-card-image')['style'].split("'")[1]
        except AttributeError:
            imageUrl = None

        try:
            url = ('https://www.inshorts.com' + card.find(class_='news-card-title')
                   .find('a').get('href'))
        except AttributeError:
            url = None

        try:
            content = card.find(class_='news-card-content').find('div').text
        except AttributeError:
            content = None

        try:
            author = card.find(class_='author').text
        except AttributeError:
            author = None

        try:
            date = card.find(clas='date').text
        except AttributeError:
            date = None

        try:
            time = card.find(class_='time').text
        except AttributeError:
            time = None

        try:
            readMoreUrl = card.find(class_='read-more').find('a').get('href')
        except AttributeError:
            readMoreUrl = None

        # get location

        newsObject = {
            'title': title,
            'imageUrl': imageUrl,
            'url': url,
            'content': content,
            'author': author,
            'timestamp': _getTimestamp(date,time),
            'time': time,
            'readMoreUrl': readMoreUrl
        }

        newsDictionary['data'].append(newsObject)

    with open(filename, "w") as outfile:
        outfile.write(json.dumps(newsDictionary))


# For each article in each chunk file
#   1. Use geograpy to fetch possible tokens that represent places in the article
#   2. Sometimes nationality is mistakenly identified as place. If so, fetch the actual nation from nationality_map_new
#   3. Get only the top 3 locations from article and find its coordinates using geolocator
#   4. If either no location or if no coordinates was extracted, try to go mideival by tokenizing and matching the words directly with nationality_map_new
#   5. Write articles in chunk to the new chunk file
def addLocations(file, newFilePrefix="updated_"):
    location_coordinates = dict()
    
    with open(file, encoding="utf8") as infile:
        newsDictionary = json.loads(infile.read())

    with open(newFilePrefix + file, "w") as outfile:
        updatedNewsDictionary = dict();
        updatedNewsDictionary['data'] = []
        
        articles = newsDictionary['data']
        geolocator = Nominatim(user_agent="ns9805@rit.edu")

        count = 0
        for article in articles:
            article['location'] = dict()
            article['location']['coordinates'] = []
            article['location']['type'] = 'MultiPoint'

            isLocSet = 0
            places = geograpy.get_place_context(text=article['content'])
            count += 1
            regionSet = set()

            for region in places.region_mentions:
                if region[0] in nationality_map_new.mapp:
                    regionSet.add(nationality_map_new.mapp[region[0]])
                else:
                    regionSet.add(region[0])

                if len(regionSet) >= 3:
                    break

            for region in regionSet:
                for attempt in range(2):
                    try:
                        if region in location_coordinates:
                            location = location_coordinates[region]
                            print("dictionary")
                        else:
                            location = geolocator.geocode(region)
                            location_coordinates[region] = location

                        if location:
                            article['location']['coordinates'].append([location.longitude, location.latitude])
                            isLocSet += 1
                        break
                    except geopy.exc.GeocoderServiceError as e:
                        print(e)
                        continue

                if isLocSet >= 3:
                    break

            if len(article['location']['coordinates']) == 0:
                tokens = pos_tag(nltk.word_tokenize(article['content']))
                locs = set()

                for token in tokens:
                    if token[0] in nationality_map_new.mapp:
                        locs.add(nationality_map_new.mapp[token[0]])
                    elif token[0].capitalize() in nationality_map_new.mapp:
                        locs.add(nationality_map_new.mapp[token[0].capitalize()])

                for loc in locs:
                    if loc in location_coordinates:
                        location = location_coordinates[loc]
                    else:
                        location = geolocator.geocode(loc)
                        location_coordinates[loc] = location

                    if location:
                        article['location']['coordinates'].append([location.longitude, location.latitude])
                
            newsDictionary['data'].append(article);

        outfile.write(json.dumps(updatedNewsDictionary))
        outfile.flush()


# Helper function to convert date and time into timestamp
def _getTimestamp(date, time):
    months = {"Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12, "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4}
    date = re.split(r'[\s,]', date)
    del date[-1]

    time = re.split(r'[\s:]', time)
    if time[-1] == 'pm':
        time[0] = str(int(time[0]) + 11)
    del time[-1]

    return int(datetime(int(date[2]), months[date[1]], int(date[0]), int(time[0]), int(time[1])).timestamp())


# 1. Get the articles
#   a. Get the latest news and save to data.json
#   b. Chunk it up into multiple files
# 2. Add locations to each article
def run():
    getNews("data.json")
    addLocations("data.json", newFilePrefix="updated_")
    print("Updated articles written to updated_data.json")


if __name__ == '__main__':
    run()
