import csv
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser, 5)  # @TODO


class SignedArtistSpider:
    def __init__(self):
        self.idlist = [1001, 1002, 1003, 2001, 2002, 2003, 6001, 6002, 6003,
                       7001, 7002, 4001, 4002, 4003]
        self.initial_letter = [i for i in range(65, 91)]
        self.initial_letter.append(0)
        self.base_url = "https://music.163.com/#/discover/artist/cat?"
        self.url_list = [self.base_url + "id={0}&initial={1}".format(i, j)
                         for i in self.idlist for j in self.initial_letter]

    @staticmethod
    def get_all_artist(url):
        browser.get(url)
        browser.switch_to.frame("g_iframe")
        html = browser.page_source
        soup = BeautifulSoup(html, "lxml")
        artist_info = soup.select(".nm.nm-icn.f-thide.s-fc0")
        homepage_info = soup.select(".f-tdn")
        artists = {}
        homepages = {}
        for artist in artist_info:
            name = str(artist.get_text()).replace("\xa0", " ")
            id = str(re.findall('href="(.*?)"', str(artist))).split("=")[1].split("\'")[0]
            artists[name] = id
        for homepage in homepage_info:
            homepage_id = str(re.findall('href="(.*?)"', str(homepage))).split("=")[1].split("\'")[0]
            homepage_name = str(re.findall('title="(.*?)"', str(homepage))).split("的个人主页")[0].split("\'")[1].replace(
                "\\xa0", " ")
            homepages[homepage_name] = homepage_id
        return artists, homepages

    @staticmethod
    def select_signed_artist(url):
        artists, homepages = SignedArtistSpider.get_all_artist(url)
        signed_artist_name_id = {}
        signed_artist_name_homepage = {}
        data = []
        for name in artists.keys():
            if name in homepages.keys():
                signed_artist_name_id[name] = artists[name]
                signed_artist_name_homepage[name] = homepages[name]
                data.append({"artist_name": name,
                             "artist_id": artists[name],
                             "artist_homepage": homepages[name]})
        return signed_artist_name_id, signed_artist_name_homepage, data

    def homepage_list(self, csv_file: str):
        homepage_list = {}
        for _url in self.url_list:
            _, homepage, _ = SignedArtistSpider.select_signed_artist(_url)
            homepage_list.update(homepage)
        return homepage_list

    def save2file(self, csv_file: str):
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["artist_name", "artist_id", "artist_homepage"]
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for _url in self.url_list:
                print("Crawling url: " + str(_url))
                _, _, data = SignedArtistSpider.select_signed_artist(_url)
                writer.writerows(data)


if __name__ == '__main__':
    artist_spider = SignedArtistSpider()

    # test get_all_artist
    # a, b = artist_spider.get_all_artist("https://music.163.com/#/discover/artist/cat?id=1001&initial=65")
    # print("artist name", a)
    # print("artist homepage", b)

    # test select_signed_artist
    # id, _, _ = artist_spider.select_signed_artist("https://music.163.com/#/discover/artist/cat?id=1001&initial=65")
    # print("artist_name_id:", id)

    artist_spider.save2file("data/signed_artists_total.csv")

    browser.quit()
