from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import csv
import re

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 5)    # @TODO


class SignedArtistSpider:
    def __init__(self):
        self.idlist = [1001]
        self.initial_letter = [i for i in range(65, 67)]
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
            name = artist.get_text()
            id = str(re.findall('href="(.*?)"', str(artist))).split("=")[1].split("\'")[0]
            artists[name] = id
        for homepage in homepage_info:
            homepage_id = str(re.findall('href="(.*?)"', str(homepage))).split("=")[1].split("\'")[0]
            homepage_name = str(re.findall('title="(.*?)"', str(homepage))).split("的个人主页")[0].split("\'")[1]
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

    def homepage_list(self):
        homepage_list = {}
        for _url in self.url_list:
            _, homepage, _ = SignedArtistSpider.select_signed_artist(_url)
            homepage_list.update(homepage)
        return homepage_list

    @staticmethod
    def save2csv(url, csv_file: str):
        print("save to file...")
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            fieldnames = ["artist_name", "artist_id", "artist_homepage"]
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            _, _, data = SignedArtistSpider.select_signed_artist(url)
            print(data)
            writer.writerows(data)
            print("save successed")

    def main(self):
        for _url in self.url_list:
            self.save2csv(_url, "data/signed_artist.csv")


if __name__ == '__main__':
    artist_spider = SignedArtistSpider()
    artist_spider.main()
