import json

import geograpy
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


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

    # if not newsCards:
    #     newsDictionary['success'] = False
    #     newsDictionary['errorMessage'] = 'Invalid Category'
    #     return newsDictionary

    for card in newsCards:
        try:
            title = card.find(class_='news-card-title').find('a').text
        except AttributeError:
            title = None

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


def addLocations(files):
    for file in files:
        og = file
        file = "data/" + file
        with open(file, encoding="utf8") as infile:
            newsDictionary = json.loads(infile.read())
            articles = newsDictionary['data']
            geolocator = Nominatim(user_agent="specify_your_app_name_here")

            count = 0
            for article in articles:
                count += 1
                print(str(count))
                places = geograpy.get_place_context(text=article['content'])
                for region in places.region_mentions:
                    isLocSet = False
                    for attempt in range(2):
                        try:
                            location = geolocator.geocode(region[0])
                            if location:
                                article['loc'] = {'latitude': location.latitude, 'longitude': location.longitude}
                                isLocSet = True
                            break
                        except:
                            continue

                    if isLocSet:
                        break

                if 'loc' not in article:
                    print("Empty")
                    article['loc'] = {}

                # hashlib.md5(s.encode()).hexdigest()

            newsDictionary['data'] = articles
            with open("updated_" + og, "w") as outfile:
                outfile.write(json.dumps(newsDictionary))


if __name__ == '__main__':
    # with open('data.json', encoding="utf8") as infile:
    #     newsDictionary = json.loads(infile.read())
    #     for i in range(10):
    #         chunkDictionary = dict()
    #         chunkDictionary['data'] = newsDictionary['data'][(i*1000):((i+1)*1000)]
    #         with open("data_"+str(i+1)+".json", "w") as outfile:
    #             outfile.write(json.dumps(chunkDictionary))
    #
    #     chunkDictionary = dict()
    #     chunkDictionary['data'] = newsDictionary['data'][10000:]
    #     with open("data_11.json", "w") as outfile:
    #         outfile.write(json.dumps(chunkDictionary))
    #
    # exit()

    # files = os.listdir("C:/Users/nirup/PycharmProjects/inshorts-scrapper/data")
    addLocations(['data_2.json', 'data_3.json'])
