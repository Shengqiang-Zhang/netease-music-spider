from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import csv
import re

from get_signed_artist import SignedArtistSpider


class HomepageSpider:
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 5)  # @TODO
        self.base_url = "https://music.163.com/#/user/"
        self.artist_spider = SignedArtistSpider()
        self.homepage_id_list = self.artist_spider.homepage_list()

    def follows_list(self, homepage_id):
        url = self.base_url + "follows?id=" + homepage_id
        self.browser.get(url)
        self.browser.switch_to.frame("g_iframe")
        html = self.browser.page_source
        soup = BeautifulSoup(html, "lxml")
        follows_info = soup.select(".s-fc7.f-fs1.nm.f-thide")
        follows = {}
        for follow in follows_info:
            name = follow.get_text()
            id = str(re.findall('href="(.*?)"', str(follow))).split("=")[1].split("\'")[0]
            follows[name] = id

    def events_follows_fans_nums(self, homepage_id):
        """return number of events, follows and fans of the artist"""
        url = self.base_url + "home?id=" + homepage_id
        self.browser.get(url)
        self.browser.switch_to.frame("g_iframe")
        html = self.browser.page_source
        soup = BeautifulSoup(html, "lxml")

    # def fans(self):

    # def event_list(self):
#
if __name__ == '__main__':
    hp_spider = HomepageSpider()
    print(hp_spider.homepage_id_list)
