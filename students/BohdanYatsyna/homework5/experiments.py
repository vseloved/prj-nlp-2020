from bs4 import BeautifulSoup


def read_file(filename):
    with open(filename) as input_file:
        text = input_file.read()
    return text


def parse_user_datafile_bs(filename):
    results = []
    text = read_file(filename)

    soup = BeautifulSoup(text, 'html.parser')
    blender_list = soup.find_all('li', {'class': 'catalog-grid__cell'})
    for item in blender_list:
        product_id = item.find('div', {'class': 'g-id'})
        print(product_id)
    print(blender_list)
    t = 1
    # items = film_list.find_all('div', {'class': ['item', 'item even']})
    # for item in items:
    #     # getting movie_id
    #     movie_link = item.find('div', {'class': 'nameRus'}).find('a').get('href')
    #     movie_desc = item.find('div', {'class': 'nameRus'}).find('a').text
    #     movie_id = re.findall('\d+', movie_link)[0]
    #
    #     # getting english name
    #     name_eng = item.find('div', {'class': 'nameEng'}).text
    #
    #     #getting watch time
    #     watch_datetime = item.find('div', {'class': 'date'}).text
    #     date_watched, time_watched = re.match('(\d{2}\.\d{2}\.\d{4}), (\d{2}:\d{2})', watch_datetime).groups()
    #
    #     # getting user rating
    #     user_rating = item.find('div', {'class': 'vote'}).text
    #     if user_rating:
    #         user_rating = int(user_rating)
    #
    #     results.append({
    #         'movie_id': movie_id,
    #         'name_eng': name_eng,
    #         'date_watched': date_watched,
    #         'time_watched': time_watched,
    #         'user_rating': user_rating,
    #         'movie_desc': movie_desc
    #     })
    # return results


filename = "test.html"

f = read_file(filename)
parse_user_datafile_bs(filename)
