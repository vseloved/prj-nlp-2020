import re
# import en_core_web_md

# nlp = en_core_web_md.load()

# with open('./bs_1.txt') as f:
#     band_page_content = f.read()

# doc = nlp(band_page_content)


def has_num(sent):
    return re.findall('\d{4}', sent)


def is_title(string):
    return string[0].isupper()


def get_albums(sent):
    titles = re.findall(
        '([A-Z][a-z]+[\s\w\.\.\.\']+([A-Z][a-z]+)?(?:\s+\(\d+\)))', sent)
#     print('>>> titles', titles)
    albums = []
    for v in titles:
        res = []
        title = v[0]
        print('>> ttt', title)
        t = title.split(' ')
        for i in range(0, len(t)):
            if len(t) - 1 > i:
                next_token = t[i+1]
                if is_title(t[i]) and t[i] not in res:
                    res.append(t[i])
                if (is_title(next_token) or len(next_token) < 4):
                    if next_token not in res:
                        res.append(next_token)
            else:
                # last word in the sentense
                if is_title(t[i]) and not t[i] in res:
                    res.append(t[i])
        albums.append(
            {'title': ' '.join(res), 'year': re.search('\d+', title).group(0)})
    return albums


sent = "The band helped define the genre with releases such as Black Sabbath (1970), Paranoid (1970), and Master of Reality (1971)."


albs = get_albums(sent)
print(albs)
