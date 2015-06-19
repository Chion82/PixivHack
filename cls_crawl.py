# coding=utf-8

import requests
import urllib
import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class PixivHack(object):
	
	def __init__(self):
		self.__session_id = ''
		self.__session = requests.Session()
		self.__session.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.125 Safari/537.36'})
		self.__keyword = 'kancolle'
		self.__min_ratings = 0
		self.__max_pics = 10

	@property
	def session_id(self):
		return self.__session_id

	@session_id.setter
	def session_id(self, id_str):
		self.__session_id = id_str
		print('Setting PHPSESSID...Accessing www.pixiv.net')
		self.__session.get('http://www.pixiv.net', cookies={'PHPSESSID': self.__session_id})

	def config(self, keyword, min_ratings, max_pics):
		self.__keyword = keyword
		self.__min_ratings = min_ratings
		self.__max_pics = max_pics

	def crawl(self):
		search_list = self.__get_search_result()
		for link in search_list:
			print(link)

	def __get_search_result(self):
		search_result = self.__session.get('http://www.pixiv.net/search.php?word=' + urllib.quote(self.__keyword))
		result_list = re.findall(r'<a href="(/member_illust\.php\?mode=medium&amp;illust_id=.*?)">', search_result.text)
		return [link for link in result_list if (not '"' in link)]

test = PixivHack()
test.session_id = '14127528_7f4835b61dc9c369e33bc0d88a579031'
test.config('kancolle', 0, 10)
test.crawl()
