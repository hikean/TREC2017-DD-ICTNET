#! -*- encoding: utf-8 -*-

import codecs
import logging
import json
import re
import sys
import time
from functools import partial

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from se_suggestion import GoogleExtractor
from se_suggestion import BingExtractor


def retry(max_retry):
    def decrotor(func):
        def dotry(*args, **kwargs):
            for i in range(max_retry):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.exception("[!] retry exception: %s", e)
        return dotry
    return decrotor


def first(ls):
    if not isinstance(ls, list) or len(ls) == 0:
        return None
    return ls[0]


class Search(object):
    DRIVERPATH = "/Users/kean/bin/chromedriver"
    CHROMEPATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    @staticmethod
    def get_driver(driver_path=None, chrome_path=None):
        if driver_path is None:
            driver_path = Search.DRIVERPATH
        if chrome_path is None:
            chrome_path = Search.CHROMEPATH
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = chrome_path
        return webdriver.Chrome(
            executable_path=driver_path, chrome_options=chrome_options)

    @staticmethod
    def extract_number(text):
        return first(
            [int(val) for val in re.findall(r'\d+', text.replace(",", ""))]
        )

    def __init__(self, driver_path=None, chrome_path=None):
        self.driver = Search.get_driver(driver_path, chrome_path)
        self.current_url, self.last_url = None, None

    def clear(self):
        self.current_url, self.last_url = None, None

    def quit(self):
        self.driver.quit()

    def by_id(self, tid):
        return self.driver.find_element_by_id(tid)

    def by_xpath(self, xpath):
        return self.driver.find_element_by_xpath(xpath)

    def by_name(self, name):
        return self.driver.find_element_by_name(name)

    def by_class(self, class_name):
        return self.driver.find_element_by_class_name(class_name)

    def sby_id(self, tid):
        return self.driver.find_elements_by_id(tid)

    def sby_xpath(self, xpath):
        return self.driver.find_elements_by_xpath(xpath)

    def sby_name(self, name):
        return self.driver.find_elements_by_name(name)

    def sby_class(self, class_name):
        return self.driver.find_element_by_class_name(class_name)

    def click(self, element):
        if element.is_displayed():
            element.click()
            return True
        return False

    def result(self):
        return (self.result_stats, self.related_query, self.suggestions)

    def get(self, url):
        self.current_url = url
        self.driver.get(url)

    def updated(self, wait_count=100):
        while self.driver.current_url == self.current_url and wait_count > 0:
            time.sleep(0.03)
            wait_count -= 1
        self.current_url = self.driver.current_url
        return wait_count != 0

    @retry(3)
    def search_google(self, query, page_count=1):
        self.clear()
        if "https://www.google." not in self.driver.current_url:
            self.get("https://www.google.com/ncr")
        textbox = self.driver.find_element_by_id("lst-ib")
        textbox.clear()
        textbox.send_keys(query)
        try:
            sulist = self.by_xpath('//*[@id="sbtc"]/div[2]')
            suggestions = sulist.text.split("\n")
        except Exception:
            suggestions = []
            pass
        textbox.send_keys(Keys.RETURN)
        self.dowhile(self.updated, False, 1)
        result = GoogleExtractor(
            url=self.driver.current_url,
            html=self.driver.page_source
        ).extract_all()
        result["query"] = query
        if len(result["suggestions"]) == 0:
            result["suggestions"] = suggestions
        for i in range(1, page_count):
            self.by_xpath('//*[@id="pnnext"]').click()
            self.dowhile(self.updated, False, 1)
            result["results"].extend(
                GoogleExtractor(
                    url=self.driver.current_url,
                    html=self.driver.page_source
                ).extract_results()
            )
        return result

    @staticmethod
    def dowhile(func, result=True, retry_count=200):
        while func() is result and retry_count > 0:
            time.sleep(0.01)
            retry_count -= 1

    @retry(3)
    def search_bing(self, query, page_count=1):
        self.clear()
        if "http://cn.bing" not in self.driver.current_url:
            self.get("http://cn.bing.com/?mkt=en-US&intlF=")
            en_btn = self.by_id("est_en")
            Search.dowhile(partial(self.click, en_btn), False)
        form = self.by_id("sb_form_q")
        form.clear()
        form.send_keys(query)
        try:
            sa_ul = self.by_id("sw_as")
            Search.dowhile(sa_ul.is_displayed, False)
            suggestions = sa_ul.text.split("\n")
        except Exception:
            suggestions = []
        form.send_keys(Keys.RETURN)
        self.dowhile(self.updated, False, 1)
        result = BingExtractor(
            url=self.driver.current_url,
            html=self.dirver.page_source
        ).extract_all()
        result["query"] = query

        if len(result["suggestions"]) == 0:
            result["suggestions"] = suggestions
        return result

    @retry(3)
    def search_baidu(self, query, page_count=1):
        self.clear()

    def search_yandex(self, query, page_count=1):
        self.clear()

    def search(self, query, se_name, page_count=1):
        logging.info("[#]: <%s>, QUERY: <%s>", query, se_name)
        if se_name == "google":
            return self.search_google(query, page_count)
        elif se_name == "bing":
            return self.search_bing(query, page_count)
        elif se_name == "yandex":
            return self.search_yandex(query, page_count)
        elif se_name == "baidu":
            return self.search_baidu(query, page_count)
        else:
            raise ValueError("se_name can't be '{}'".foramt(se_name))


def make_query(query, affix="ebola"):
    if affix in query.lower():
        return query
    return " & ".join([affix, query])


def main(out_file, se_name, topic_set):
    from es_test import TOPICS as eb_topics
    from es_test import NY_TOPICS as ny_topics
    from es_test import PL_TOPICS as pl_topics
    topics = []
    logging.root.setLevel(logging.INFO)
    if "all" in topic_set:
        topics = eb_topics + ny_topics
    if "ALL" in topic_set:
        topics = eb_topics + pl_topics + ny_topics
    if "ebola" in topic_set:
        topics.extend(eb_topics)
    if "nytimes" in topic_set:
        topics.extend(ny_topics)
    if "polar" in topic_set:
        topics.extend(pl_topics)
    if "test" in topic_set:
        topics = topics[:2]
    se = Search()
    results = {
        topic_id: se.search(make_query(topic), se_name, 5)
        for topic_id, topic in topics[:27]
    }
    # logging.info(json.dumps(results, indent=4))
    json.dump(obj=results, fp=codecs.open(out_file, "w", "utf-8"), indent=4)


def usage():
    print((
        "Usage:\n" +
        "\t{0} <search_engine_name>\n" +
        "\t{0} <search_engine_name> <data_set>\n" +
        "\t{0} <search_engine_name> <data_set> <out_file_suffix>\n" +
        "\tdata_set can be 'all', 'ebola', 'nytimes', 'test', 'nytimes_test'"
    ).format(sys.argv[0].split("/")[-1]))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        usage()
    else:
        se_name = sys.argv[1]
        data_set = "ebola_test"
        if len(sys.argv) >= 3:
            data_set = sys.argv[2]

        if len(sys.argv) >= 4:
            main(
                "../../datas/{}_{}_{}_head.json".format(
                    se_name, data_set, sys.argv[3]
                ), se_name, data_set
            )
        else:
            main(
                "../../datas/{}_{}_head.json".format(
                    se_name, data_set
                ), se_name, data_set
            )


# def main(out_file, se_name):
#     from es_test import TOPICS as eb_topics
#     from es_test import NY_TOPICS as ny_topics
#     logging.root.setLevel(logging.INFO)
#     topics = eb_topics + ny_topics
#     se = Search()
#     results = {
#         topic_id: se.search(" & ".join(["ebola", topic]), se_name, 5)
#         for topic_id, topic in topics[:27]
#     }
#     # logging.info(json.dumps(results, indent=4))
#     json.dump(obj=results, fp=codecs.open(out_file, "w", "utf-8"))


# def usage():
#     print((
#         "Usage:\n" +
#         "    {0} <search_engine_name>\n" +
#         "    {0} <search_engine_name> <out_file_suffix>"
#     ).format(sys.argv[0].split("/")[-1]))


# if __name__ == "__main__":
#     if len(sys.argv) == 1:
#         usage()
#     else:
#         se_name = sys.argv[1]
#         out_file = "../../datas/{}.json".format(se_name)
#         if len(sys.argv) == 3:
#             out_file = "../../datas/{}_{}.json".format(
#                 se_name, sys.argv[2])
#         main(out_file, se_name)
