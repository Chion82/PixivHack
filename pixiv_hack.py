from lib.cls_crawl import PixivHackLib

if __name__ == '__main__':
	print('Enter PHPSESSID:')
	PHPSESSID = raw_input()
	print('Enter key word:')
	key_word = raw_input()
	print('Enter minimum ratings:')
	min_ratings = raw_input()
	print('Enter maximum illustrations to download:')
	max_pics = raw_input()
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
	lib.config('kancolle', int(min_ratings), int(max_pics), download_manga)
	lib.crawl()
