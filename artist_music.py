import csv

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("headless")
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser, 5)  # @TODO


class ArtistMusicSpider:
    def __init__(self):
        self.base_url = "https://music.163.com/#/"
        self.homepage_dict = self.read_homepage_from_file("data/signed_artist.csv")

    def read_homepage_from_file(self, datafile):
        homepage_name_id_dict = {}
        with open(datafile, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                homepage_name_id_dict.update({row["artist_name"]: row["artist_homepage"]})
        return homepage_name_id_dict

    def loved_music(self, homepage_id: str):
        """get the artist's loved music list"""
        url = self.base_url + "playlist?id=" + str(homepage_id)
        browser.get(url)
        browser.switch_to.frame("g_iframe")
        html = browser.page_source
        soup = BeautifulSoup(html, "lxml")

        raw_loved_music_list = browser.find_elements_by_xpath("//a[contains(@href, '/song?id=')]")
        # due to my analysis, every music item contains three lines,
        # however, only line1 and line3 contain music name.
        # maybe this is the anti-crawler measure ?
        temp_music_file = "data/temp_loved_music.txt"
        with open(temp_music_file, "w", encoding="utf-8") as f:
            for idx, music in enumerate(raw_loved_music_list):
                f.write(str(music.text) + "\n")
        f.close()
        loved_music_list = []
        with open(temp_music_file, "r", encoding="utf-8") as f:
            line_count = 0
            music_name = ""
            for line in f.readlines():
                line_count += 1
                if line_count == 2:
                    continue
                elif line_count == 1:
                    music_name = str(line.strip())
                elif line_count == 3:
                    music_name += str(line.strip())
                    loved_music_list.append(music_name)
                    line_count = 0

        raw_album_list = browser.find_elements_by_xpath("//a[contains(@href, '/album?id=')]")
        # due to my analysis, every album item contains two lines,
        # line 1 and line 2 make up the album name together.
        temp_album_file = "data/temp_loved_music_album.txt"
        with open(temp_album_file, "w", encoding="utf-8") as f:
            for idx, album in enumerate(raw_album_list):
                f.write(str(album.text) + "\n")
        f.close()
        album_list = []
        with open(temp_album_file, "r", encoding="utf-8") as f:
            line_count = 0
            album_name = ""
            for line in f.readlines():
                line_count += 1
                if line_count == 1:
                    album_name = str(line.strip())
                else:
                    album_name += str(line.strip())
                    line_count = 0
                    album_list.append(album_name)

        assert (len(loved_music_list) == len(album_list))

        # match the music name and album name
        music_album_dict = {}
        for music_name, album_name in zip(loved_music_list, album_list):
            music_album_dict[music_name] = album_name
        return music_album_dict

    def save_all_loved_music_to_file(self, csv_file: str):
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            filednames = ["artist_name", "music", "album"]
            writer = csv.DictWriter(f, filednames)
            writer.writeheader()
            for homepage in self.homepage_dict.items():
                _name = homepage[0]
                _id = homepage[1]
                _music_album_dict = self.loved_music(_id)
                print("saving loved music of {0},"
                      " homepage id: {1}".format(_name, _id))
                for ele in _music_album_dict:
                    data = {"artist_name": _name,
                            "music": ele[0],
                            "album": ele[1]}
                    writer.writerow(data)


if __name__ == '__main__':
    artist_music_spider = ArtistMusicSpider()
    # test love_music
    # music_album = artist_music_spider.loved_music("46973796")
    # print(music_album)

    # test save_all_loved_music_to_file
    artist_music_spider.save_all_loved_music_to_file("data/artist_loved_music.csv")
