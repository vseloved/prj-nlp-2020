import re
import pandas as pd
from typing import List

from selenium.webdriver import ActionChains

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import time


class RozetkaParser:
    PROS_TAG = "достоинства:"
    CONS_TAG = "недостатки:"
    RESPONSE_TAG = "ответить"

    NO_REVIEWS_TAG = "оставить отзыв"

    EMPTY_RESULT = {
        'title': [],
        'pros': [],
        'cons': [],
        'rating': []
    }

    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--kiosk")


    def acquire_urls(self, start_url, page_from, page_to):

        driver = webdriver.Chrome(executable_path="/home/dbabenko/_Dev/Tools/chromedriver",
                                  chrome_options=self.chrome_options)

        urls = []
        for page in range(page_from, page_to + 1):

            page_url = f"{start_url}page={page}/"

            driver.get(page_url)
            driver.implicitly_wait(100)

            elements = driver.find_elements_by_class_name('goods-tile__picture')
            for element in elements:
                href = element.get_attribute('href')
                url = f"{href}/comments"
                urls.append(url)


        return urls


    def parse_urls(self, urls: List[str], csv_file):

        driver = webdriver.Chrome(executable_path="/home/dbabenko/_Dev/Tools/chromedriver",
                                  chrome_options=self.chrome_options)

        result = {
            'title': [],
            'pros': [],
            'cons': [],
            'rating': []
        }

        for i in range(0, len(urls)):
            url = urls[i]
            try:
                tmp_result = self.parse_url(url, driver)

                pd.DataFrame(tmp_result).to_csv(csv_file, mode='a', header=False, index=False)
                print(i)

                result['title'] += tmp_result['title']
                result['pros'] += tmp_result['pros']
                result['cons'] += tmp_result['cons']
                result['rating'] += tmp_result['rating']
            except:
                print("Exception here")
                driver = webdriver.Chrome(executable_path="/home/dbabenko/_Dev/Tools/chromedriver",
                                          chrome_options=self.chrome_options)

                continue

        return result

    def parse_url(self, url, driver):
        url = url.strip()
        print(url)

        driver.get(url)
        driver.implicitly_wait(100)

        if self.__is_url_contains_comments_review(url, driver) is False:
            return self.EMPTY_RESULT

        self.__sort_by_buyers(driver)
        self.__show_all_comments(driver)

        print("Start parsing document: ")
        result = self.__parse_product_comments(driver)
        return result

    def __sort_by_buyers(self, driver):
        el = driver.find_element_by_id('comments-sort-select')
        el.click()

        el.send_keys(Keys.ARROW_DOWN)
        el.send_keys(Keys.ARROW_DOWN)
        el.send_keys(Keys.RETURN)


    def __find_show_more_comments_button(self, driver):
        buttons = driver.find_elements_by_tag_name('button')
        for button in buttons:
            if self.__check_button_class(button, "button button_size_medium product-comments__show-more"):
                return button

        return None

    def __check_button_class(self, button_el, class_name):
        try:
            if button_el.get_attribute('class') == class_name:
                return True
        except:
            return False
        return False

    def __show_all_comments(self, driver):

        show_more_comments_button = None
        while True:
            try:
                if show_more_comments_button is None:
                    show_more_comments_button = self.__find_show_more_comments_button(driver)

                if show_more_comments_button is None:
                    break

                if show_more_comments_button.is_enabled() is False:
                    break

                actions = ActionChains(driver)
                actions.move_to_element_with_offset(show_more_comments_button, xoffset=0, yoffset=0)
                actions.perform()
                span = show_more_comments_button.find_element_by_tag_name('span')
                span.click()

            except Exception as e:
                print("Exception: ", e)
                break

    def __parse_product_comments(self, driver):
        result = {
            'title': [],
            'pros': [],
            'cons': [],
            'rating': []
        }

        product_comment_els = driver.find_elements_by_class_name('product-comment')
        for product_comment_el in product_comment_els:

            try:
                if product_comment_el.tag_name != "div":
                    continue

                print("product_comment_el.find_element_by_class_name('product-comment__inner')", "start")
                inner_el = product_comment_el.find_element_by_class_name('product-comment__inner')
                print("product_comment_el.find_element_by_class_name('product-comment__inner')", "end")

                rate = None
                print("inner_el.find_elements_by_tag_name('div')", "start")
                divs = inner_el.find_elements_by_tag_name('div')
                print("inner_el.find_elements_by_tag_name('div')", "end")
                for div in divs:
                    if div.get_attribute('class') != 'product-comment__rating':
                        continue

                    print("div.find_elements_by_tag_name('svg')", "start")
                    svgs = div.find_elements_by_tag_name('svg')
                    print("div.find_elements_by_tag_name('svg')", "end")

                    if len(svgs) == 0:
                        continue

                    rating_star_info = svgs[0].get_attribute('aria-label')
                    rate = self.__parse_rating(rating_star_info)
                    break

                if rate is None:
                    continue

                print("self.__parse_comment_text(product_comment_el)", "start")
                title, pros, cons = self.__parse_comment_text(product_comment_el)
                print("self.__parse_comment_text(product_comment_el)", "end")

                result['title'].append(title)
                result['pros'].append(pros)
                result['cons'].append(cons)
                result['rating'].append(rate)

            except Exception as e:
                print(e)
                continue

        return result

    def __parse_rating(self, rating_info_str: str):
        m = re.search(r"\d", rating_info_str)
        if m is None:
            return None

        return int(rating_info_str[m.start()])

    def __parse_comment_text(self, product_comment_el):
        body_element = product_comment_el.find_element_by_class_name("product-comment__body")
        return self.__parse_comment_text_helper(body_element.text)
        # div_elements = body_element.find_elements_by_tag_name('div')
        # for element in div_elements:
        #     if element.get_attribute('class') == "product-comment__body":
        #         return self.__parse_comment_text_helper(element.text)
        #
        # return None, None, None

    def __parse_comment_text_helper(self, comment_text: str):
        lines = comment_text.split('\n')
        if len(lines) == 0:
            return None, None, None

        title, title_end_pos = self.__parse_title(lines, 0)
        pros, pos = self.__parse_pros(lines, title_end_pos)
        if pros is None:
            pos = title_end_pos
        cons, pos = self.__parse_cons(lines, pos)

        return title, pros, cons

    def __parse_title(self, lines, start_pos):
        title = None
        for i in range(start_pos, len(lines)):
            if lines[i] == '\n':
                continue

            cur_line = lines[i].lower()
            if self.PROS_TAG in cur_line or self.CONS_TAG in cur_line or self.RESPONSE_TAG in cur_line:
                return title, i

            if title is None:
                title = lines[i]
            else:
                title += " "
                title += lines[i]

        return title, len(lines)

    def __parse_pros(self, lines, start_pos):
        if start_pos >= len(lines):
            return None, start_pos

        if self.PROS_TAG not in lines[start_pos].lower():
            return None, start_pos

        start_pos += 1


        title = None
        for i in range(start_pos, len(lines)):
            if lines[i] == '\n':
                continue

            cur_line = lines[i].lower()
            if self.CONS_TAG in cur_line or self.RESPONSE_TAG in cur_line:
                return title, i

            if title is None:
                title = lines[i]
            else:
                title += " "
                title += lines[i]

        return title, len(lines)

    def __parse_cons(self, lines, start_pos):
        if start_pos >= len(lines):
            return None, start_pos

        if self.CONS_TAG not in lines[start_pos].lower():
            return None, start_pos

        start_pos += 1


        title = None
        for i in range(start_pos, len(lines)):
            if lines[i] == '\n':
                continue
            cur_line = lines[i].lower()
            if self.PROS_TAG in cur_line or self.RESPONSE_TAG in cur_line:
                return title, i

            if title is None:
                title = lines[i]
            else:
                title += " "
                title += lines[i]

        return title, len(lines)

    def __is_url_contains_comments_review(self, url, driver):
        try:
            element = driver.find_element_by_class_name('product__rating-reviews')
            if self.NO_REVIEWS_TAG in element.text.lower():
                return False
            return True
        except:
            return False



def write_lines_to_file(file, lines):
    with open(file, 'a') as f:
        for line in lines:
            f.write(line)
            f.write('\n')

def read_lines(file):
    with open(file) as f:
        lines = f.readlines()
    return lines


urls = read_lines('data/hard_urls.txt')
parser = RozetkaParser()

start_time = time.time()
result = parser.parse_urls(urls, 'data/rozetka-hard-comments.csv')
pd.DataFrame(result).to_csv('data/rozetka-hard-comments-all.csv')

print(time.time() - start_time)

# result = parser.parse_urls(urls, 'rozetka-router-comments-all.csv')
# print(len(tmp_result))

# result = parser.parse_urls(urls)

# print(result)







#
# parser = RozetkaParser()
#
# urls = parser.acquire_urls("https://rozetka.com.ua/routers/c80193/", 1, 34)
#
# write_lines_to_file('router_urls.txt', urls)
#
# print(urls)
# print(len(urls))

# result = parser.parse_url(url)


# print(result)
