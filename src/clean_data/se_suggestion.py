# -*- encoding: utf-8 -*-

import codecs
import json
import logging
import re
import sys
import time

import requests
from lxml import etree
from nltk import ngrams

# from urllib import urlencode, quote
# import HTMLParser


def except_wrap(func):
    def doexcept(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception("[!] %s %s", func.__name__, e)
            return []
    return doexcept


def first(ls, empty_value=None):
    if not isinstance(ls, list) or len(ls) == 0:
        return empty_value
    return ls[0]


def cut_words(document, ignorecase=False):
    if ignorecase:
        return re.findall(r"\w+", document.lower(), re.UNICODE)
    else:
        return document.split(" ")
        # return re.findall(r"\w+", document, re.UNICODE)


def make_ngram(words, ngram):
    if isinstance(words, str):
        words = cut_words(words)
    return ngrams(words, ngram)


class Extractor(object):
    @property
    def base_url(self):
        if self._base_url is None or self._base_url not in self.url:
            url = [x for x in self.url.split("/") if len(x) > 0]
            if ":" in url[0]:
                self._base_url = "//".join(url[:2])
            else:
                self._base_url = url[0]
        return self._base_url

    def __init__(self, url, html=None, root=None):
        self.root = root
        self._base_url, self.url = None, url
        if html is not None:
            self.root = etree.HTML(html)
        if html is None and root is None:
            raise ValueError("html and root can't both be None")

    def update(self, url, html=None, root=None):
        self.__init__(url=url, html=html, root=root)

    @staticmethod
    def get_text(element, seperator=" "):
        if not isinstance(element, list):
            return seperator.join([x.strip() for x in element.itertext()])
        else:
            return seperator.join([Extractor.get_text(x) for x in element])

    def extract_results(self):
        raise NotImplementedError("extract_results need to be implemented")

    def extract_related(self):
        raise NotImplementedError("extract_results need to be implemented")

    def extract_suggestion(self):
        raise NotImplementedError("extract_results need to be implemented")

    def extract_next_links(self):
        raise NotImplementedError("extract_results need to be implemented")

    def extract_count(self):
        raise NotImplementedError("extract_results need to be implemented")

    def extract_all(self):
        return {
            "results": self.extract_results(),
            "related": self.extract_related(),
            "suggestions": self.extract_suggestion(),
            "next_links": self.extract_next_links(),
            "count": self.extract_count()
        }


class GoogleExtractor(Extractor):
    def extract_results(self):
        for xpath in [
            '//div[@class="g"]/div/div[@class="rc"]',
            '//div[@class="rc"]'
        ]:
            rc = self.root.xpath(xpath)
            if len(rc) != 0:
                break
        return [
            {
                "title": Extractor.get_text(
                    div.xpath("h3") +
                    div.xpath("div/h3") +
                    div.xpath("div/div/h3")
                ),
                "abstract": Extractor.get_text(
                    div.xpath("*/*/*/span") +
                    div.xpath("div/div/span") +
                    div.xpath("div/span") +
                    div.xpath("span")
                ),
                "url": first(
                    div.xpath("h3/a/@href") +
                    div.xpath("div/h3/a/@href") +
                    div.xpath("div/div/h3/a/@href")
                )
            }
            for div in rc
        ]

    def extract_count(self):
        text = first(self.root.xpath('//*[@id="resultStats"]/text()'), "0")
        logging.info("[#]: result count %s", text)
        return int(re.findall(r"\d+", text.replace(",", ""))[0])

    def extract_next_links(self):
        return [
            self.base_url + url
            for url in self.root.xpath('//*[@id="nav"]/tr/td/a/@href')
        ]

    def extract_related(self):
        return [
            Extractor.get_text(p)
            for p in self.root.xpath('//*[@class="brs_col"]/p')
        ]

    def extract_suggestion(self):
        return []


class BingExtractor(Extractor):
    def extract_results(self):
        return [
            {
                "title": Extractor.get_text(
                    li.xpath("h2") + li.xpath("div/h2") +
                    li.xpath("div/div/h2")
                ),
                "abstract": Extractor.get_text(
                    li.xpath("div/p") + li.xpath("div/div/p") +
                    li.xpath("div/*/*/p")
                ),
                "url": li.xpath("//h2/a/@href")[0]
            }
            for li in self.root.xpath(
                '//*[@id="b_results"]/li[@class="b_algo"]')
        ]

    def extract_related(self):
        b_rs = self.root.xpath(
            '//*[@id="b_results"]/*[@class="b_ans"]/div[@class="b_rs"]')
        if len(b_rs) == 0:
            return []
        else:
            return [
                Extractor.get_text(li) for li in(
                    b_rs[0].xpath("div/div/div/ul/li") +
                    b_rs[0].xpath("div/div/ul/li") +
                    b_rs[0].xpath("div/ul/li") +
                    b_rs[0].xpath("ul/li")
                )
            ]

    def extract_count(self):
        try:
            return int(
                self.root.xpath(
                    '//span[@class="sb_count"]/text()'
                )[0].split(" ")[0].replace(",", "")
            )
        except Exception as e:
            logging.exception("[!] extract_count exception: %s", e)
            return 0

    def extract_next_links(self):
        b_pag = self.root.xpath('//*[@id="b_results"]/li[@class="b_pag"]')
        if len(b_pag) == 0:
            return []
        else:
            return [
                self.base_url + x for x in
                (
                    b_pag[0].xpath("*/*/*/a/@href") +
                    b_pag[0].xpath("*/*/a/@href") +
                    b_pag[0].xpath("*/a/@href")
                )
                if x.startswith("/search?")
            ]

    def extract_suggestion(self):
        return []


class Suggester(object):
    HEADERS = {
    "User-Agent": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Mobile Safari/537.36"
        ][-1]
    }

    def __init__(self, proxies=None, proxies_flag=False):
        self.proxies = proxies
        if proxies is None and proxies_flag:
            self.proxies = Suggester.get_proxies()
        self.response = None
        self.conn, self._cvid = requests.Session(), None
        self._base_url = None
        self.init_bing()
        self.init_google()

    def get(self, url, headers=None, cookies=None, proxies=None,
            proxies_flag=True):
        logging.info("[#] GET %s", url)
        if "google.com" in url:
            time.sleep(1)
        if proxies is None:
            proxies = self.proxies
        if headers is None:
            headers = Suggester.HEADERS
        if not proxies_flag:
            proxies = None
        if cookies is None:
            self.response = self.conn.get(
                url=url, headers=headers, proxies=proxies,
            )
        else:
            self.response = self.conn.get(
                url=url, headers=headers, cookies=cookies, proxies=proxies
            )
        return self.response

    @staticmethod
    def get_proxies(ip="socks5://127.0.0.1:1080"):
        return {"http": ip, "https": ip}

    @staticmethod
    def load_baidu(response, query):
        res = response.text.replace(',', '"')
        return [x for x in res.split('"') if x.startswith(query)]

    def xpath(self, text, pattern):
        return etree.HTML(text).xpath(pattern)

    @staticmethod
    def get_text(element, seperator=" "):
        if not isinstance(element, list):
            return seperator.join([x.strip() for x in element.itertext()])
        else:
            return seperator.join([Suggester.get_text(x) for x in element])

    def suggest_baidu(self, query):
        url = u"https://sp0.baidu.com/5a1Fazu8AA54nxGko9WTAnF6hhy/su?wd={}"
        url = url.format(query)
        response = self.get(url=url, headers=Suggester.HEADERS)
        return Suggester.load_baidu(response, query)

    def search_baidu(self, query, page_count=1):
        pass

    @staticmethod
    def load_google(response, query):
        js = json.loads(response.text)[1]
        return [x[0].replace("<b>", "").replace("</b>", "") for x in js]

    @staticmethod
    def strip_args(url):
        return url.split("?")[0]

    def suggest_google(self, query, proxies=None, proxies_flag=True):
        url = "https://www.google.com/complete/search?client=psy-ab&hl=en&q={}"
        url = url.format(query)
        response = self.get(
            url=url, headers=Suggester.HEADERS, proxies=proxies,
            proxies_flag=proxies_flag
        )
        return Suggester.load_google(response, query)

    def search_google(self, query, page_count=1):
        url = "https://www.google.com/search?source=hp&q={0}&oq={0}".format(
            query.replace("&", "%26").replace(" ", "+")
        )
        self.get(url=url)
        codecs.open("google.html", "w", "utf-8").write(self.response.text)
        # logging.info(self.response.text)

        ex = GoogleExtractor(url=url, html=self.response.text)
        results = ex.extract_results()
        related = ex.extract_related()
        next_links = ex.extract_next_links()
        result_count = ex.extract_count()
        for link in next_links[: page_count - 1]:
            self.get(url=link)
            ex.update(url=link, html=self.response.text)
            results.extend(ex.extract_results())
        if len(next_links) == 0:
            for i in range(page_count - 1):
                url = first(ex.root.xpath('//a[@id="pnnext"]/@href'))
                next_links.append(url)
                if url is not None:
                    url = self.base_url + url
                    self.get(url=url)
                    ex.update(url=url, html=self.response.text)
                    results.extend(ex.extract_results())

        return {
            "results": results,
            "related": related,
            "suggestions": self.suggest_google(query),
            "next_links": next_links,
            "count": result_count
        }

    def _find_cvid(self):
        res = re.findall(r',IG:"([0-9A-Za-z]+)",', self.response.text)
        return first(res, None)

    @property
    def base_url(self):
        if self.response is None:
            return ""
        if self._base_url not in self.response.url:
            url = [x for x in self.response.url.split("/") if len(x) > 0]
            if ":" in url[0]:
                self._base_url = "//".join(url[:2])
            else:
                self._base_url = url[0]
        return self._base_url

    def init_bing(self):
        if self._cvid is not None:
            return
        self.get("http://www.bing.com/?mkt=en-US")
        self._cvid = self._find_cvid()
        self._base_url = self.response.url.split("?")[0][:-1]
        logging.info("[#] base url: %s", self.base_url)

    def init_google(self):
        try:
            self.get(url="https://www.google.com")
        except Exception as e:
            logging.exception("[!] INIT_GOOGLE: %s", e)

    @property
    def cvid(self):
        if self._cvid is None:
            return "0CF2272F9A7D491691D1D824F5FC6547"
        return self._cvid

    def bing_search_url(self, query):
        # http://www.bing.com/search?q=apple&FORM=QSRE5
        url = "http://www.bing.com/search?q={0}&qs=n&sp=-1&pq={0}&cvid={1}"
        return url.format(query, self.cvid)

    def bing_suggest_url(self, query):
        url = "http://www.bing.com/AS/Suggestions?pt=page.home&mkt=en-us&"
        url += "qry={0}&cp=2&cvid={1}"
        return url.format(query, self.cvid)

    def suggest_bing(self, query):
        url = self.bing_suggest_url(query)
        response = self.get(url=url, headers=Suggester.HEADERS)
        return re.findall(r'query="([a-zA-Z\- _\w]+)"',
                          response.text, flags=re.U)

    def print_element(self, element):
        print etree.tostring(element, pretty_print=True)

    def search_bing(self, query, page_count=1):
        link = self.bing_search_url(query)
        self.get(url=link)
        codecs.open("bing.html", "w", "utf-8").write(self.response.text)
        ex = BingExtractor(link, self.response.text)
        result = {
            "results": ex.extract_results(),
            "related": ex.extract_related(),
            "count": ex.extract_count(),
            "suggestions": self.suggest_bing(query),
            "next_links": ex.extract_next_links()
        }
        for next_link in result["next_links"][:page_count - 1]:
            self.get(url=next_link)
            ex.update(url=next_link, html=self.response.text)
            result["results"].extend(ex.extract_results())
        return result

    def search_yandex(self, query, page_count=1):
        pass

    def suggest_yandex(self, query):
        url = "https://www.yandex.com/suggest-spok/suggest-ya.cgi?"
        url += "n=10&bemjson=1&html=1&portal=1&latin=1&part={}&pos={}"
        url = url.format(query, len(query))
        response = self.get(url=url)
        return self.load_baidu(response.text)

    def test_goole(self):
        url = "https://www.google.com"
        self.get(url=url)

    def suggest(self, query, se_name="bing"):
        # html = HTMLParser.HTMLParser()
        # [html.unescape(x) for x in se.suggest(topic, se_name)]
        if se_name == "google":
            return self.suggest_google(query)
        elif se_name == "bing":
            return self.suggest_bing(query)
        elif se_name == "yandex":
            return self.suggest_yandex(query)
        elif se_name == "baidu":
            return self.suggest_baidu(query)
        else:
            raise ValueError("se_name can't be '{}'".foramt(se_name))

    def search(self, query, se_name, page_count=1):
        logging.info("[#]: [%s], QUERY: <%s>", se_name, query)
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

    def search_and_suggest(self, query, se_name):
        pass


def make_query(query, data_type, affix="ebola"):
    if "ebola" not in data_type or affix in query.lower():
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

    se = Suggester(proxies_flag=True)
    results = {
        topic_id: se.search(make_query(topic, topic_set), se_name, 5)
        for topic_id, topic in topics
    }
    # logging.info(json.dumps(results, indent=4))
    json.dump(obj=results, fp=codecs.open(out_file, "w", "utf-8"), indent=4)


def usage():
    print((
        "Usage:\n" +
        "\t{0} <search_engine_name>\n" +
        "\t{0} <search_engine_name> <data_set>\n" +
        "\t{0} <search_engine_name> <data_set> <out_file_suffix>\n" +
        "\tdata_set can be 'all', 'ebola', 'nytimes', 'test', 'nytimes_test'" +
        " 'polar'"
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
                "../../datas/{}_{}_{}.json".format(
                    se_name, data_set, sys.argv[3]
                ), se_name, data_set
            )
        else:
            main(
                "../../datas/{}_{}.json".format(
                    se_name, data_set
                ), se_name, data_set
            )
