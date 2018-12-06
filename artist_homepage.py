import csv
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("headless")
browser = webdriver.Chrome(chrome_options=chrome_options)
browser.set_window_size(1000, 30000)
wait = WebDriverWait(browser, 5)  # @TODO


# missing_url = []  # for crawling missing url


class HomepageSpider:
    def __init__(self):
        self.base_url = "https://music.163.com/#/user/"
        self.homepage_name_id_dict = self.read_homepage_from_file("data/signed_artists_total.csv")
        self.homepage_id_name_dict = {v: k for k, v in self.homepage_name_id_dict.items()}
        # self.artist_spider = SignedArtistSpider()
        # self.homepage_id_list = self.artist_spider.homepage_list()

    @staticmethod
    def read_homepage_from_file(datafile):
        homepage_name_id_dict = {}
        with open(datafile, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                homepage_name_id_dict.update({row["artist_name"]: row["artist_homepage"]})
        return homepage_name_id_dict

    def follows_list(self, homepage_id):
        """
        :return {name: homepage_id}
        """
        url = self.base_url + "follows?id=" + homepage_id
        browser.get(url)
        browser.switch_to.frame("g_iframe")
        follows = {}
        while True:
            html = browser.page_source
            soup = BeautifulSoup(html, "lxml")
            follows_info = soup.select(".s-fc7.f-fs1.nm.f-thide")
            for follow in follows_info:
                name = follow.get_text()
                id = str(re.findall('href="(.*?)"', str(follow))).split("=")[1].split("\'")[0]
                follows[name] = id
            # print(follows)
            next_page = browser.find_elements_by_xpath("//a[contains(text(), '下一页')]")
            if len(next_page) == 0:
                break
            elif str(next_page[0].get_attribute("class")).__contains__("js-disabled"):
                break
            else:
                next_page[0].click()
                time.sleep(1.6)
        return follows

    def save_all_follows_list_to_file(self, csv_file: str):
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["artist_name", "follows", "follows_homepage"]
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            count = 0
            for homepage in self.homepage_name_id_dict.items():
                count += 1
                _name = homepage[0]
                _id = homepage[1]
                _follows_list = self.follows_list(_id)
                print("saving follows list of %s, count: %d" % (_name, count))
                for follows in _follows_list:
                    data = {"artist_name": _name,
                            "follows": follows,
                            "follows_homepage": _follows_list[follows]}
                    writer.writerow(data)

    def events_follows_fans_nums(self, homepage_id):
        """return number of events, follows and fans of the artist"""
        url = self.base_url + "home?id=" + homepage_id
        browser.get(url)
        browser.switch_to.frame("g_iframe")
        html = browser.page_source
        soup = BeautifulSoup(html, "lxml")
        event_counts = soup.select("#event_count")  # search via id
        for count in event_counts:
            event_count = count.get_text()
        follow_counts = soup.select("#follow_count")
        for count in follow_counts:
            follow_count = count.get_text()
        fan_counts = soup.select("#fan_count")
        for count in fan_counts:
            fan_count = count.get_text()
        return event_count, follow_count, fan_count

    def save_events_follows_fans_nums_to_file(self, csv_file: str):
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            fieldnames = ["artist_name", "events_count",
                          "follows_count", "fans_count"]
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            count = 0
            for homepage in self.homepage_name_id_dict.items():
                count += 1
                _name = homepage[0]
                _id = homepage[1]
                print("Saving three nums of %s's homepage, count = %d"
                      % (_name, count))
                _ec, _fc, _fan_c = self.events_follows_fans_nums(_id)
                data = {"artist_name": _name,
                        "events_count": _ec,
                        "follows_count": _fc,
                        "fans_count": _fan_c}
                writer.writerow(data)

    def find_artists_in_events(self, homepage_id):  # @TODO
        """find all user in the artist's events page"""
        url = self.base_url + "event?id=" + homepage_id
        browser.get(url)
        browser.switch_to.frame("g_iframe")
        raw_at_user = browser.find_elements_by_xpath(
            "//a[contains(@href, '/user/home?id=') or contains(@href, '/user/home?nickname=') and @class='s-fc7']")
        artists_dict = {}
        artists_list = []
        for ele in raw_at_user:
            # print(ele.text)
            if str(ele.text).startswith("@"):
                name = str(ele.text).split("@")[1].strip()
                id = str(ele.get_attribute("href")).split("=")[1]
                artists_list.append(name)
                artists_dict[name] = id
        # print(artists_set)
        return artists_list, artists_dict

    def save_all_artists_in_event_to_file(self, csv_file: str):
        """save all artists' events related artists to file"""
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            fieldnames = ["artist_name", "at_artist", "at_artist_id"]
            writer = csv.DictWriter(f, fieldnames)
            # writer.writeheader()
            count = 0
            for homepage in self.homepage_name_id_dict.items():
                count += 1
                _name = homepage[0]
                _id = homepage[1]
                print("saving artists in %s's event, "
                      "homepage_id: %s, count: %d" % (_name, _id, count))
                _artists_list, _artists_dict = self.find_artists_in_events(_id)
                for artist in _artists_list:
                    data = {"artist_name": _name,
                            "at_artist": artist,
                            "at_artist_id": _artists_dict[artist]}
                    writer.writerow(data)

    def get_music_in_events(self, homepage_id):
        """find all music in the artist's events page"""
        url = self.base_url + "event?id=" + homepage_id
        browser.get(url)
        browser.switch_to.frame("g_iframe")
        raw_music = browser.find_elements_by_xpath("//a[contains(@href, '/song?id=') and @class='s-fc1']")
        music_id_dict = {}
        music_author_dict = {}
        for ele in raw_music:
            _name = str(ele.text)
            _song_id = str(ele.get_attribute("href")).split("=")[1]
            _data_event_id = ele.get_attribute("data-event-id")
            authors = browser.find_elements_by_xpath("//a[@data-event-id='{0}'"
                                                     " and @class='s-fc3']"
                                                     .format(_data_event_id))
            author_list = []
            for author in authors:
                # print(_name, "author:", author.text)
                author_list.append(author.text)
            music_author_dict[_name] = author_list
            music_id_dict[_name] = _song_id
        return music_id_dict, music_author_dict

    def save_all_music_in_event_to_file(self, csv_file: str):
        """save music occurred in one's event for all artists"""
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["artist_name", "music_name",
                          "music_id", "music_author"]
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for homepage in self.homepage_name_id_dict.items():
                _name = homepage[0]
                _id = homepage[1]
                print("saving music in %s's event, "
                      "homepage_id: %s" % (_name, _id))
                _music_id_dict, _music_author_dict = self.get_music_in_events(_id)
                for music in _music_id_dict:
                    data = {"artist_name": _name,
                            "music_name": music,
                            "music_id": _music_id_dict[music],
                            "music_author": _music_author_dict[music]}
                    writer.writerow(data)

    def get_loved_music_url_id(self, homepage_id: str):
        """get the url id of the artist's loved music"""
        url = self.base_url + "home?id=" + homepage_id
        browser.get(url)
        browser.switch_to.frame("g_iframe")

        all_links = browser.find_elements_by_xpath("//a[contains(@title, '喜欢的音乐')]")
        while len(all_links) == 0:  # find until all_links contains what we want.
            print("enter while")
            all_links = browser.find_elements_by_xpath("//a[contains(@title, '喜欢的音乐')]")
        _url_id = str(all_links[0].get_attribute("href")).split("=")[1]
        print(_url_id)
        try:
            assert len(_url_id) > 0
        except:
            print("Exception", _url_id)
        return _url_id

    def save_all_loved_music_url_id_to_file(self, csv_file: str):
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            fieldnames = ["artist_name", "loved_music_url_id"]
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            count = 0
            for homepage in self.homepage_name_id_dict.items():
                count += 1
                _name = homepage[0]
                _id = homepage[1]
                print("saving loved music file of", _name, "count:", count)
                _url_id = self.get_loved_music_url_id(_id)
                data = {"artist_name": _name,
                        "loved_music_url_id": _url_id}
                writer.writerow(data)


if __name__ == '__main__':
    hp_spider = HomepageSpider()

    # test follows_list
    # follows_list = hp_spider.follows_list("93249076")
    # follows_list = hp_spider.follows_list("72145909")
    # follows_list = hp_spider.follows_list("265145")
    # print(follows_list)
    hp_spider.save_all_follows_list_to_file("data/follows_list_total.csv")

    # test events_follows_fans_nums
    # hp_spider.save_events_follows_fans_nums_to_file("data/events_follows_fans_num_total.csv")

    # test find_artists_in_events
    # hp_spider.find_artists_in_events("29879272")
    # hp_spider.find_artists_in_events("60279611")
    # hp_spider.find_artists_in_events("135214753")

    # test save_all_artists_in_event_to_file
    # hp_spider.save_all_artists_in_event_to_file("data/artists_in_events_total.csv")

    # test get_music_in_events
    # hp_spider.get_music_in_events("135214753")

    # test save_all_music_in_event_to_file
    # hp_spider.save_all_music_in_event_to_file("data/music_in_events.csv")

    # test get_loved_music_url_id
    # url_id = hp_spider.get_loved_music_url_id("3434543")
    # print(url_id)

    # test save_all_loved_music_utl_id_to_file
    # hp_spider.save_all_loved_music_url_id_to_file("data/loved_music_url_id_2.csv")

    # for homepage in hp_spider.homepage_dict.items():
    #     name = homepage[0]
    #     id = homepage[1]
    #     event, follow, fan = hp_spider.events_follows_fans_nums(id)
    #     print(name, event, follow, fan)
    browser.quit()
    # with open("data/missing_url.txt", "w", encoding="utf-8") as f:
    #     for i in missing_url:
    #         f.write(i + "\n")
#
