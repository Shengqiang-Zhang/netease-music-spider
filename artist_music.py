import csv

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("headless")
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser, 5)  # @TODO


class ArtistMusicSpider:
    def __init__(self):
        self.base_url = "https://music.163.com/#/"
        # self.homepage_dict = self.read_homepage_from_file("data/signed_artist.csv")
        self.loved_music_url_id = self.read_loved_music_url_id("data/loved_music_url_id.csv")

    @staticmethod
    def read_homepage_from_file(datafile):
        homepage_name_id_dict = {}
        with open(datafile, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                homepage_name_id_dict.update({row["artist_name"]: row["artist_homepage"]})
        return homepage_name_id_dict

    @staticmethod
    def read_loved_music_url_id(datafile):
        url_id_dict = {}
        with open(datafile, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url_id_dict.update({row["artist_name"]: row["loved_music_url_id"]})
        return url_id_dict

    def loved_music(self, playlist_id: str):
        """get the artist's loved music list"""
        url = self.base_url + "playlist?id=" + str(playlist_id)
        browser.get(url)
        browser.switch_to.frame("g_iframe")

        raw_loved_music_list = browser.find_elements_by_xpath("//a[contains(@href, '/song?id=')]/b[@title]")

        loved_music_list = []  # @TODO: I think saving not only music name but also music id would be better here
        for music in raw_loved_music_list:
            _name = str(music.get_attribute("title")).replace("\xa0", " ")
            loved_music_list.append(_name)

        raw_album_list = browser.find_elements_by_xpath("//a[contains(@href, '/album?id=')]")
        album_name_list = []  # name may be replicate
        album_id_list = []
        for album in raw_album_list:
            _name = str(album.get_attribute("title")).replace("\xa0", " ")
            _id = str(album.get_attribute("href")).split("=")[1]
            album_name_list.append(_name)
            album_id_list.append(_id)

        assert len(loved_music_list) == len(album_name_list) == len(album_id_list)

        # match the music name and album name, album id
        music_album_dict = {}
        for music_name, album_name, album_id in zip(loved_music_list,
                                                    album_name_list,
                                                    album_id_list):
            music_album_dict[music_name] = {album_name: album_id}
        return music_album_dict

    def save_all_loved_music_to_file(self, csv_file: str):
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            filednames = ["artist_name", "music", "album_name", "album_id"]
            writer = csv.DictWriter(f, filednames)
            writer.writeheader()
            for playlist_id in self.loved_music_url_id.items():
                _name = playlist_id[0]
                _id = playlist_id[1]
                _music_album_dict = self.loved_music(_id)
                print("saving loved music of {0},"
                      " playlist id: {1}".format(_name, _id))
                for ele in _music_album_dict:
                    _album_name = list(_music_album_dict[ele].keys())[0]
                    _album_id = _music_album_dict[ele][_album_name]
                    data = {"artist_name": _name,
                            "music": ele,
                            "album_name": _album_name,
                            "album_id": _album_id}
                    writer.writerow(data)


if __name__ == '__main__':
    artist_music_spider = ArtistMusicSpider()

    # test love_music
    # music_album = artist_music_spider.loved_music("61037035")
    # print(music_album)

    # test save_all_loved_music_to_file
    artist_music_spider.save_all_loved_music_to_file("data/artist_loved_music.csv")
