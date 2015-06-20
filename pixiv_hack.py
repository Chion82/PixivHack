# coding=utf-8

#Author: Chion82<sdspeedonion@gmail.com>

from lib.cls_crawl import PixivHackLib
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--authorlist', help='Crawl illustrations by author IDs. A JSON file containg the list of Pixiv member IDs is required.')
args = parser.parse_args()

if __name__ == '__main__':
	print('Enter PHPSESSID:')
	PHPSESSID = raw_input()
	print('Enter minimum ratings:')
	min_ratings = raw_input()
	print('Download manga? (Y/n)')
	download_manga_str = raw_input()
	if (download_manga_str == 'Y' or download_manga_str == 'y'):
		print('Will download manga.')
		download_manga = True
	else:
		print('Will not download manga.')
		download_manga = False
	lib = PixivHackLib()
	lib.session_id = PHPSESSID
	
	if (args.authorlist):
		print('Will crawl using author ID list.')
		print('JSON file : ' + args.authorlist)
		f = open(args.authorlist, 'r')
		author_list = json.loads(f.read())
		f.close()
		author_list = [str(x['author_id']) if type(x)==dict else str(x) for x in author_list]
		print('Enter maximum number of illustrations per author:')
		max_pics_per_author = raw_input()
		lib.config('', int(min_ratings), 0, download_manga)
		lib.crawl_by_author(author_list, int(max_pics_per_author))
	else:
		print('Will crawl using keyword.')
		print('Enter keyword:')
		key_word = raw_input()
		print('Enter maximum number of illustrations to download:')
		max_pics = raw_input()
		lib.config(key_word, int(min_ratings), int(max_pics), download_manga)
		lib.crawl()
