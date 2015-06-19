# coding=utf-8

import requests
import urllib
import re
import sys, os
import HTMLParser
from urlparse import urlparse, parse_qs

reload(sys)
sys.setdefaultencoding('utf8')

class PixivHackLib(object):
	
	def __init__(self):
		self.__session_id = ''
		self.__session = requests.Session()
		self.__session.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.125 Safari/537.36'})
		self.__keyword = 'kancolle'
		self.__min_ratings = 0
		self.__max_pics = 10
		self.__pic_downloaded_count = 0
		self.__download_manga = True

	@property
	def session_id(self):
		return self.__session_id

	@session_id.setter
	def session_id(self, id_str):
		self.__session_id = id_str

	def config(self, keyword, min_ratings, max_pics, download_manga):
		self.__keyword = keyword
		self.__min_ratings = min_ratings
		self.__max_pics = max_pics
		self.__download_manga = download_manga

	def crawl(self):
		self.__pic_downloaded_count = 0
		page = 1
		while self.__pic_downloaded_count < self.__max_pics :
			search_result = self.__get_search_result(page)
			if (len(search_result)==0 or page>1000):
				print('No more result found. ')
				break
			for link in search_result:
				if (self.__pic_downloaded_count >= self.__max_pics):
					break
				self.__enter_illustration_page(link)
			page = page + 1
			print('************************Moving to next page************************')
		print('All Done!')

	def __get_search_result(self, page):
		try:
			search_result = self.__session.get('http://www.pixiv.net/search.php?word=' + urllib.quote(self.__keyword) + '&p=' + str(page), cookies={'PHPSESSID': self.__session_id})
		except Exception:
			print('Connection failure. Retrying...')
			self.__get_search_result(page)
			return
		
		result_list = re.findall(r'<a href="(/member_illust\.php\?mode=.*?&amp;illust_id=.*?)">', search_result.text)
		return ['http://www.pixiv.net'+self.__html_decode(link) for link in result_list if (not '"' in link)]

	def __enter_illustration_page(self, url):
		print('********************Entering illustration page*********************')
		print('Entering ' + url)

		try:
			page_result = self.__session.get(url, cookies={'PHPSESSID': self.__session_id})
		except Exception:
			print('Connection failure. Retrying...')
			self.__enter_illustration_page(url)
			return
		
		re_result_ratings = re.findall(r'<dd class="rated-count">(.*?)</dd>', page_result.text)
		ratings = re_result_ratings[0]
		pixiv_id = parse_qs(urlparse(url).query)['illust_id'][0]
		re_result_author_id = re.findall(r'<a href="/member\.php\?id=(.*?)" class="user-link">', page_result.text)
		pixiv_author_id = re_result_author_id[0]
		print('pixiv_id=' + pixiv_id)
		print('ratings='+ratings)
		print('author_id='+pixiv_author_id)
		if (int(ratings) < self.__min_ratings):
			print('Ratings < ' + str(self.__min_ratings) + ' , Skipping...')
			return
		re_manga_result = re.findall(r'<a href="(member_illust\.php\?mode=manga&amp;illust_id=.*?)"', page_result.text)
		re_image_result = re.findall(r'data-src="(.*?/img-original/.*?)"', page_result.text)
		if (len(re_manga_result) > 0):
			if (self.__download_manga == False):
				print('Illustration is manga. Skipping...')
				return
			print('Illustration is manga. Entering manga page.')
			self.__enter_manga_page('http://www.pixiv.net/' + self.__html_decode(re_manga_result[0]), pixiv_id)
			self.__pic_downloaded_count = self.__pic_downloaded_count + 1
		elif (len(re_image_result) > 0):
			print('Illustration is image. Downloading image...')

			try:
				download_result = self.__session.get(self.__html_decode(re_image_result[0]), cookies={'PHPSESSID': self.__session_id}, headers={'Referer':url})
			except Exception:
				print('Connection failure. Retrying...')
				self.__enter_illustration_page(url)
				return
			
			self.__pic_downloaded_count = self.__pic_downloaded_count + 1
			if (download_result.status_code != 200):
				print('Download Error')
				print(download_result.text)
			url_parsed_array = re_image_result[0].split('/')
			file_name = url_parsed_array[len(url_parsed_array)-1]
			with open('images/' + file_name, 'wb+') as f:
				for chunk in download_result.iter_content():
					f.write(chunk)
				f.close()
			print('Download completed.')
		else:
			print('Illustration mode not supported. Skipping...')


	def __enter_manga_page(self, url, pixiv_id):
		print('********************Entering manga page**************************')
		print('Entering ' + url)
		if not os.path.exists('images/' + pixiv_id):
			os.makedirs('images/' + pixiv_id)

		try:
			page_result = self.__session.get(url, cookies={'PHPSESSID': self.__session_id})
		except Exception:
			print('Connection failure. Retrying...')
			self.__enter_manga_page(url, pixiv_id)
			return

		re_manga_page_result = re.findall(r'<a href="(/member_illust\.php\?mode=manga_big.*?)"', page_result.text)
		for link in re_manga_page_result:
			self.__enter_manga_big_page('http://www.pixiv.net' + self.__html_decode(link), pixiv_id)

	def __enter_manga_big_page(self, url, pixiv_id):
		print('********************Entering manga-big page***************************')
		print('Entering ' + url)

		try:
			page_result = self.__session.get(url, cookies={'PHPSESSID': self.__session_id})
		except Exception:
			print('Connection failure. Retrying...')
			self.__enter_manga_big_page(url, pixiv_id)
			return
		
		re_image_result = re.findall(r'<img src="(.*?)"', page_result.text)
		url_parsed_array = re_image_result[0].split('/')
		file_name = url_parsed_array[len(url_parsed_array)-1]
		print('Downloading manga-big image...')

		try:
			download_result = self.__session.get(self.__html_decode(re_image_result[0]), cookies={'PHPSESSID': self.__session_id}, headers={'Referer':url})
		except Exception:
			print('Connection failure. Retrying...')
			self.__enter_manga_big_page(url, pixiv_id)
			return

		if (download_result.status_code != 200):
			print('Download Error')
			print(download_result.text)
		with open('images/' + pixiv_id + '/' + file_name, 'wb+') as f:
			for chunk in download_result.iter_content():
				f.write(chunk)
			f.close()
		print('Download completed.')


	def __html_decode(self, string):
		h = HTMLParser.HTMLParser()
		return h.unescape(string)
