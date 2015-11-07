# coding=utf-8

#Author: Chion82<sdspeedonion@gmail.com>

import requests
import urllib
import re
import sys, os
import HTMLParser
import json
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
		self.__download_big_images = True
		self.__author_ratings = []
		if not os.path.exists('pixivimages'):
			os.makedirs('pixivimages')

	@property
	def session_id(self):
		return self.__session_id

	@session_id.setter
	def session_id(self, id_str):
		self.__session_id = id_str

	def config(self, keyword, min_ratings, max_pics, download_manga, download_big_images):
		self.__keyword = keyword
		self.__min_ratings = min_ratings
		self.__max_pics = max_pics
		self.__download_manga = download_manga
		self.__download_big_images = download_big_images

	def crawl(self):
		self.__pic_downloaded_count = 0
		self.__author_ratings = []
		page = 1
		while self.__pic_downloaded_count < self.__max_pics :
			try:
				search_result = self.__get_search_result(page, None)
				if (len(search_result)==0 or page>1000):
					print('No more result found. ')
					break
				for link in search_result:
					if (self.__pic_downloaded_count >= self.__max_pics):
						break
					self.__enter_illustration_page(link, 'pixivimages')
				page = page + 1
				print('************************Moving to next page************************')
			except Exception:
				print('Crawl error. Skipping page...')
				page = page + 1
				continue
		print('All Done! Saving author info...')
		self.__save_author_ratings()

	def crawl_by_author(self, author_list, max_pics_per_author):
		for author_id in author_list:
			print('***********************Crawling by author*************************')
			print('author Pixiv ID : ' + author_id)
			self.__pic_downloaded_count = 0
			page = 1
			if not os.path.exists('pixivimages/' + author_id):
				os.makedirs('pixivimages/' + author_id)
			while self.__pic_downloaded_count < max_pics_per_author:
				try:
					search_result = self.__get_search_result(page, author_id)
					if (len(search_result) == 0):
						print('No more result found.')
						break
					for link in search_result:
						if (self.__pic_downloaded_count >= max_pics_per_author):
							break
						self.__enter_illustration_page(link, 'pixivimages/' + author_id)
					page = page + 1
					print('************************Moving to next page***************************')
				except Exception:
					print('Crawl error. Skipping page...')
					page = page + 1
					continue
			print('***********************Moving to next author**************************')
		print('All Done!')

	def __get_search_result(self, page, author_id):
		try:
			if (author_id == None):
				search_result = self.__session.get('http://www.pixiv.net/search.php?word=' + urllib.quote(self.__keyword) + '&p=' + str(page), cookies={'PHPSESSID': self.__session_id})
			else:
				search_result = self.__session.get('http://www.pixiv.net/member_illust.php?id=' + author_id + '&type=all&p=' + str(page), cookies={'PHPSESSID': self.__session_id})
		except Exception:
			print('Connection failure. Retrying...')
			return self.__get_search_result(page, author_id)
			
		result_list = re.findall(r'<a href="(/member_illust\.php\?mode=.*?&amp;illust_id=.*?)">', search_result.text)
		return ['http://www.pixiv.net'+self.__html_decode(link) for link in result_list if (not '"' in link)]

	def __enter_illustration_page(self, url, directory):
		print('********************Entering illustration page*********************')
		print('Entering ' + url)

		try:
			page_result = self.__session.get(url, cookies={'PHPSESSID': self.__session_id})
		except Exception:
			print('Connection failure. Retrying...')
			self.__enter_illustration_page(url, directory)
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
		self.__increment_author_ratings(pixiv_author_id, int(ratings), pixiv_id)
		re_manga_result = re.findall(r'<a href="(member_illust\.php\?mode=manga&amp;illust_id=.*?)"', page_result.text)
		re_image_result = re.findall(r'data-src="(.*?)" class="original-image"', page_result.text)
		re_big_image_result = re.findall(r'<a href="(member_illust\.php\?mode=big&amp;illust_id=.*?)"', page_result.text)
		if (len(re_manga_result) > 0):
			if (self.__download_manga == False):
				print('Illustration is manga. Skipping...')
				return
			print('Illustration is manga. Entering manga page.')
			self.__enter_manga_page('http://www.pixiv.net/' + self.__html_decode(re_manga_result[0]), pixiv_id, url, directory)
			self.__pic_downloaded_count = self.__pic_downloaded_count + 1
		elif (len(re_image_result) > 0):
			print('Illustration is image. Downloading image...')
			self.__pic_downloaded_count = self.__pic_downloaded_count + 1
			self.__download_image(self.__html_decode(re_image_result[0]), url, directory)
			print('Download completed.')
		elif (len(re_big_image_result) > 0):
			if (self.__download_big_images == False):
				print('Illustration is big-image. Skipping...')
				return
			print('Illustration mode is big-image. Entering big-image page.')
			self.__enter_big_image_page('http://www.pixiv.net/' + self.__html_decode(re_big_image_result[0]), url, directory)
			self.__pic_downloaded_count = self.__pic_downloaded_count + 1
		else:
			print('Illustration mode not supported. Skipping...')

	def __enter_big_image_page(self, url, referer, directory):
		print('********************Entering big-image page************************')
		print('Entering ' + url)
		try:
			page_result = self.__session.get(url, cookies={'PHPSESSID': self.__session_id}, headers={'Referer':referer})
		except Exception:
			print('Connection failure. Retrying...')
			self.__enter_big_image_page(url, referer, directory)
			return

		re_big_image_url = re.findall(r'<img src="(.*?)"', page_result.text)
		print('Downloading big-image.')
		self.__download_image(self.__html_decode(re_big_image_url[0]), url, directory)
		print('Download completed.')

	def __enter_manga_page(self, url, pixiv_id, referer,directory):
		print('********************Entering manga page**************************')
		print('Entering ' + url)
		if not os.path.exists(directory + '/' + pixiv_id):
			os.makedirs(directory + '/' + pixiv_id)

		try:
			page_result = self.__session.get(url, cookies={'PHPSESSID': self.__session_id}, headers={'Referer':referer})
		except Exception:
			print('Connection failure. Retrying...')
			self.__enter_manga_page(url, pixiv_id, referer,directory)
			return

		re_manga_page_result = re.findall(r'<a href="(/member_illust\.php\?mode=manga_big.*?)"', page_result.text)
		for link in re_manga_page_result:
			self.__enter_manga_big_page('http://www.pixiv.net' + self.__html_decode(link), url, directory + '/' + pixiv_id)

	def __enter_manga_big_page(self, url, referer, directory):
		print('********************Entering manga-big page***************************')
		print('Entering ' + url)

		try:
			page_result = self.__session.get(url, cookies={'PHPSESSID': self.__session_id}, headers={'Referer':referer})
		except Exception:
			print('Connection failure. Retrying...')
			self.__enter_manga_big_page(url, referer, directory)
			return
		
		re_image_result = re.findall(r'<img src="(.*?)"', page_result.text)
		print('Downloading manga-big image...')
		self.__download_image(self.__html_decode(re_image_result[0]), url, directory)
		print('Download completed.')

	def __increment_author_ratings(self, author_id, increment, pixiv_id):
		for author in self.__author_ratings:
			if (author['author_id'] == author_id):
				if (pixiv_id in author['illust_id']):
					return
				author['total_ratings'] = author['total_ratings'] + increment
				author['illust_id'].append(pixiv_id)
				return
		self.__author_ratings.append({'author_id':author_id, 'total_ratings':increment, 'illust_id':[pixiv_id]})

	def __save_author_ratings(self):
		self.__author_ratings = sorted(self.__author_ratings, key=lambda author:author['total_ratings'], reverse=True)
		f = open('author_info.json','w+')
		f.write(json.dumps(self.__author_ratings))
		f.close()

	def __html_decode(self, string):
		h = HTMLParser.HTMLParser()
		return h.unescape(string)

	def __download_image(self, url, referer, directory):
		try:
			download_result = self.__session.get(url, cookies={'PHPSESSID': self.__session_id}, headers={'Referer':referer})
		except Exception:
			print('Connection failure. Retrying...')
			self.__download_image(url, referer, directory)
			return

		if (download_result.status_code != 200):
			print('Download Error')
			print(download_result.text)
			return
		url_parsed_array = url.split('/')
		file_name = url_parsed_array[len(url_parsed_array)-1]
		with open(directory + '/' + file_name, 'wb+') as f:
			for chunk in download_result.iter_content():
				f.write(chunk)
			f.close()
