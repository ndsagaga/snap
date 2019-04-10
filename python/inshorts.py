import json
import re
from datetime import datetime

import geograpy
import geopy
import nltk
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from nltk import pos_tag

import nationality_map_new


def getNews(data):
    # newsDictionary = {
    #     'success': True,
    #     'category': category,
    #     'data': []
    # }

    # try:
    #     htmlBody = requests.get('https://www.inshorts.com/en/read/' + category)
    # except requests.exceptions.RequestException as e:
    #     newsDictionary['success'] = False
    #     newsDictionary['errorMessage'] = str(e.message)
    #     return newsDictionary

    newsDictionary = dict()
    newsDictionary['data'] = []
    soup = BeautifulSoup(data, 'lxml')
    newsCards = soup.find_all(class_='news-card')
    titles = set()

    # if not newsCards:
    #     newsDictionary['success'] = False
    #     newsDictionary['errorMessage'] = 'Invalid Category'
    #     return newsDictionary

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
            'date': date,
            'time': time,
            'readMoreUrl': readMoreUrl
        }

        newsDictionary['data'].append(newsObject)

    with open("data.json", "w") as outfile:
        outfile.write(json.dumps(newsDictionary))


def chunkMeUp():
    with open('data.json', encoding="utf8") as infile:
        newsDictionary = json.loads(infile.read())
    id = 1
    for i in range(6):
        chunkDictionary = dict()
        chunkDictionary['data'] = []
        for c in range(i * 500, ((i + 1) * 500)):
            newsDictionary['data'][c]['id'] = id
            chunkDictionary['data'].append(newsDictionary['data'][c])
            id += 1
        with open("data_" + str(i + 1) + ".json", "w") as outfile:
            outfile.write(json.dumps(chunkDictionary))

    chunkDictionary = dict()
    chunkDictionary['data'] = []
    for c in range(3000, len(newsDictionary['data'])):
        newsDictionary['data'][c]['id'] = id
        chunkDictionary['data'].append(newsDictionary['data'][c])
        id += 1
    with open("data_7.json", "w") as outfile:
        outfile.write(json.dumps(chunkDictionary))


def addLocations(files):
    location_coordinates = dict()
    for file in files:
        with open(file, encoding="utf8") as infile:
            newsDictionary = json.loads(infile.read())

        with open("updated_" + file, "w") as outfile:
            outfile.write("{\"data\":[\n")
            articles = newsDictionary['data']
            geolocator = Nominatim(user_agent="ns9805@rit.edu")

            count = 0
            for article in articles:
                article['location'] = dict()
                article['location']['coordinates'] = []
                isLocSet = 0
                places = geograpy.get_place_context(text=article['content'])

                count += 1
                print(str(count))

                regionSet = set()

                for region in places.region_mentions:
                    if region[0] in nationality_map_new.mapp:
                        print(region[0] + " *TO* " + nationality_map_new.mapp[region[0]])
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
                                print(region + " L " + str(location.latitude) + "," + str(location.longitude))
                                article['location']['coordinates'].append([location.longitude, location.latitude])
                                isLocSet += 1
                            break
                        except geopy.exc.GeocoderServiceError as e:
                            print(e)
                            continue

                    if isLocSet >= 3:
                        break

                print(article)
                if 'location' not in article:
                    print("ERROR: Empty")
                    article['location'] = {'type': 'MultiPoint', 'coordinates': []}
                if len(article['location']['coordinates']) == 0:
                    print("ERROR: Nothing added!")

                outfile.write(json.dumps(article))
                outfile.write(",\n")
                outfile.flush()

            outfile.write("]\n}")
            outfile.flush()

                # hashlib.md5(s.encode()).hexdigest()


def divideData(files):
    goodArticles = []
    badArticles = []

    for file in files:
        print(file)
        with open(file, encoding="utf8") as infile:
            newsDictionary = json.loads(infile.read())

        articles = newsDictionary['data']

        for article in articles:
            if len(article['location']['coordinates']) == 0:
                badArticles.append(article)
            else:
                goodArticles.append(article)

    with open("compiled_good_data_new.json", "w", encoding="utf-8") as outfile:
        newsDictionary['data'] = goodArticles
        outfile.write(json.dumps(newsDictionary))

    with open("compiled_bad_data_new.json", "w", encoding="utf-8") as outfile:
        newsDictionary['data'] = badArticles
        outfile.write(json.dumps(newsDictionary))


def newLocation(file):
    with open(file, encoding="utf-8") as infile:
        newsDictionary = json.loads(infile.read())

    articles = newsDictionary['data']
    geolocator = Nominatim(user_agent="ns9805@rit.edu")
    location_dict = dict()

    for article in articles:
        article['location']['coordinates'] = []
        article['content'] = article['content'].replace("-", " ")
        tokens = pos_tag(nltk.word_tokenize(article['content']))
        locs = set()

        for token in tokens:
            if token[0] in nationality_map_new.mapp:
                locs.add(nationality_map_new.mapp[token[0]])
            elif token[0].capitalize() in nationality_map_new.mapp:
                locs.add(nationality_map_new.mapp[token[0].capitalize()])

        print(tokens)
        print(locs)

        for loc in locs:
            if loc in location_dict:
                location = location_dict[loc]
            else:
                location = geolocator.geocode(loc)
                location_dict[loc] = location

            if location:
                article['location']['coordinates'].append([location.longitude, location.latitude])

    with open("updated_" + file, "w", encoding="utf-8") as infile:
        newsDictionary['data'] = articles
        infile.write(json.dumps(newsDictionary))


def useAndThrow(file):
    with open(file, encoding="utf-8") as infile:
        newsDictionary = json.loads(infile.read())

    for article in newsDictionary:
        article['timestamp'] = getTimestamp(article['date'], article['time'])
        article.pop('date')
        article.pop('time')

    with open("new_" + file, "w", encoding="utf-8") as infile:
        infile.write(json.dumps(newsDictionary))


def getTimestamp(date, time):
    months = {"Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12, "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4}
    date = re.split(r'[\s,]', date)
    del date[-1]

    time = re.split(r'[\s:]', time)
    if time[-1] == 'pm':
        time[0] = str(int(time[0]) + 11)
    del time[-1]

    return int(datetime(int(date[2]), months[date[1]], int(date[0]), int(time[0]), int(time[1])).timestamp())


if __name__ == '__main__':
    # files = os.listdir("C:/Users/nirup/PycharmProjects/inshorts-scrapper/data")
    # divideData(['updated_data_1.json','updated_data_2.json','updated_data_3.json','updated_data_4.json','updated_data_5.json','updated_data_6.json','updated_data_7.json'])

    # with open("inshorts.txt",encoding="utf-8") as infile:
    #     data = infile.read()
    # getNews(data)
    # print(geograpy.get_place_context(text="The UK Parliament's lower house passed a bill by one vote to force PM Theresa May to extend the April 12 deadline for Brexit if no deal has been agreed to. The legislation, put forward by Labour MP Yvette Cooper, was approved at the final stage by 313 votes to 312. It now has to pass in the upper chamber.").region_mentions)

    # newLocation("compiled_bad_data.json")
    # divideData(["updated_compiled_bad_data.json"])
    useAndThrow("data.json")
