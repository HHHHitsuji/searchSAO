#!/usr/bin/env python -u
# This script requires Python 3+, Requests, and Pillow, a modern fork of PIL, the Python Imaging Library: 'easy_install Pillow' and 'easy_install requests'
# For Windows easy_install setup, download and run: https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
# After Installation of easy_install, it will be located in the python scripts directory.

# This is a basic, likley broken example of how to use the very beta saucenao API...
# There are several signifigant holes in the api, and in the way in which the site responds and reports error conditions.
# These holes will likley be filled at some point in the future, and it may impact the status checks used below.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#################CONFIG##################

api_key = "Your api_key"
EnableRename = False
minsim = '80!'  # forcing minsim to 80 is generally safe for complex images, but may miss some edge cases. If images being checked are primarily low detail, such as simple sketches on white paper, increase this to cut down on false positives.
your_username = 'aaaa'
your_password = '123456'
your_proxy = '127.0.0.1:10809'


##############END CONFIG#################
import sys
import os
import io
import unicodedata
import requests
from PIL import Image
import json
import codecs
import re
import time
from collections import OrderedDict
import requests, re
import json
from bs4 import BeautifulSoup


def login():
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Referer': 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=64503210'
    }

    # 用requests的session模块记录登录的cookie

    session = requests.session()

    # 首先进入登录页获取post_key，我用的是正则表达式
    response = session.get('https://accounts.pixiv.net/login?lang=zh',
                           proxies={'http': 'http://127.0.0.1:10809', 'https': 'https://127.0.0.1:10809'})
    post_key = re.findall('<input type="hidden" name="post_key" value=".*?">',
                          response.text)[0]
    post_key = re.findall('value=".*?"', post_key)[0]
    post_key = re.sub('value="', '', post_key)
    post_key = re.sub('"', '', post_key)

    print(post_key)

    # 将传入的参数用字典的形式表示出来，return_to可以去掉
    data = {
        'pixiv_id': your_username,
        'password': your_password,
        'return_to': 'https://www.pixiv.net/',
        'post_key': post_key,
    }

    # 将data post给登录页面，完成登录
    session.post("https://accounts.pixiv.net/login?lang=zh", data=data, headers=head,
                 proxies={'http': 'http://'+your_proxy, 'https': 'https://'+your_proxy})
    return session


session = login()


def downloadFromPixiv(image_id, session, page, member_id):
	session = session
	page = int(page[-1])

	head = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
		'Referer': 'https://www.pixiv.net/artworks/' + image_id}

	url1 = 'https://www.pixiv.net/ajax/illust/' + image_id + '/pages'
	request = session.get(url1,
						  proxies={'http': 'http://'+your_proxy, 'https': 'https://'+your_proxy})

	soup1 = BeautifulSoup(request.content, "html.parser")
	original = json.loads(soup1.string)['body'][page]['urls']['original']
	img_res = requests.get(original, headers=head,
						   proxies={'http': 'http://'+your_proxy, 'https': 'https://'+your_proxy})

	with open('D:/git_project/searchSAO/image/'+ str(member_id)+'_' + image_id + '_p'+str(page) +'.jpg', 'wb') as jpg:
		jpg.write(img_res.content)


sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())

extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
thumbSize = (250, 250)

# enable or disable indexes
index_hmags = '0'
index_reserved = '0'
index_hcg = '0'
index_ddbobjects = '0'
index_ddbsamples = '0'
index_pixiv = '1'
index_pixivhistorical = '1'
index_reserved = '0'
index_seigaillust = '1'
index_danbooru = '0'
index_drawr = '1'
index_nijie = '1'
index_yandere = '0'
index_animeop = '0'
index_reserved = '0'
index_shutterstock = '0'
index_fakku = '0'
index_hmisc = '0'
index_2dmarket = '0'
index_medibang = '0'
index_anime = '0'
index_hanime = '0'
index_movies = '0'
index_shows = '0'
index_gelbooru = '0'
index_konachan = '0'
index_sankaku = '0'
index_animepictures = '0'
index_e621 = '0'
index_idolcomplex = '0'
index_bcyillust = '0'
index_bcycosplay = '0'
index_portalgraphics = '0'
index_da = '1'
index_pawoo = '0'
index_madokami = '0'
index_mangadex = '0'

# generate appropriate bitmask
db_bitmask = int(
    index_mangadex + index_madokami + index_pawoo + index_da + index_portalgraphics + index_bcycosplay + index_bcyillust + index_idolcomplex + index_e621 + index_animepictures + index_sankaku + index_konachan + index_gelbooru + index_shows + index_movies + index_hanime + index_anime + index_medibang + index_2dmarket + index_hmisc + index_fakku + index_shutterstock + index_reserved + index_animeop + index_yandere + index_nijie + index_drawr + index_danbooru + index_seigaillust + index_anime + index_pixivhistorical + index_pixiv + index_ddbsamples + index_ddbobjects + index_hcg + index_hanime + index_hmags,
    2)
print("dbmask=" + str(db_bitmask))


# encoded print - handle random crap
def printe(line):
    print(str(line).encode(sys.getdefaultencoding(), 'replace'))  # ignore or replace


for root, _, files in os.walk(u'.', topdown=False):
	if root == '.\input':
		for f in files:
			fname = os.path.join(root, f)
			for ext in extensions:
				if fname.lower().endswith(ext):
					print(fname)
					image = Image.open(fname)
					image = image.convert('RGB')
					image.thumbnail(thumbSize, resample=Image.ANTIALIAS)
					imageData = io.BytesIO()
					image.save(imageData, format='PNG')

					url = 'http://saucenao.com/search.php?output_type=2&numres=1&minsim=' + minsim + '&dbmask=' + str(
						db_bitmask) + '&api_key=' + api_key
					files = {'file': ("image.png", imageData.getvalue())}
					imageData.close()

					processResults = True
					while True:
						r = requests.post(url, files=files)
						if r.status_code != 200:
							if r.status_code == 403:
								print('Incorrect or Invalid API Key! Please Edit Script to Configure...')
								sys.exit(1)
							else:
								# generally non 200 statuses are due to either overloaded servers or the user is out of searches
								print("status code: " + str(r.status_code))
								time.sleep(10)
						else:
							results = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(r.text)
							if int(results['header']['user_id']) > 0:
								# api responded
								print(
									'Remaining Searches 30s|24h: ' + str(results['header']['short_remaining']) + '|' + str(
										results['header']['long_remaining']))
								if int(results['header']['status']) == 0:
									# search succeeded for all indexes, results usable
									break
								else:
									if int(results['header']['status']) > 0:
										# One or more indexes are having an issue.
										# This search is considered partially successful, even if all indexes failed, so is still counted against your limit.
										# The error may be transient, but because we don't want to waste searches, allow time for recovery.
										print('API Error. Retrying in 600 seconds...')
										time.sleep(600)
									else:
										# Problem with search as submitted, bad image, or impossible request.
										# Issue is unclear, so don't flood requests.
										print('Bad image or other request error. Skipping in 10 seconds...')
										processResults = False
										time.sleep(10)
										break
							else:
								# General issue, api did not respond. Normal site took over for this error state.
								# Issue is unclear, so don't flood requests.
								print('Bad image, or API failure. Skipping in 10 seconds...')
								processResults = False
								time.sleep(10)
								break

					if processResults:
						# print(results)

						if int(results['header']['results_returned']) > 0:
							# one or more results were returned
							if float(results['results'][0]['header']['similarity']) > float(
									results['header']['minimum_similarity']):
								print('hit! ' + str(results['results'][0]['header']['similarity']))

								# get vars to use
								service_name = ''
								illust_id = 0
								member_id = -1
								index_id = results['results'][0]['header']['index_id']
								page_string = ''
								page_match = re.search('(_p[\d]+)\.', results['results'][0]['header']['thumbnail'])
								if page_match:
									page_string = page_match.group(1)

								if index_id == 5 or index_id == 6:
									# 5->pixiv 6->pixiv historical
									service_name = 'pixiv'
									member_id = results['results'][0]['data']['member_id']
									illust_id = results['results'][0]['data']['pixiv_id']
								elif index_id == 8:
									# 8->nico nico seiga
									service_name = 'seiga'
									member_id = results['results'][0]['data']['member_id']
									illust_id = results['results'][0]['data']['seiga_id']
								elif index_id == 10:
									# 10->drawr
									service_name = 'drawr'
									member_id = results['results'][0]['data']['member_id']
									illust_id = results['results'][0]['data']['drawr_id']
								elif index_id == 11:
									# 11->nijie
									service_name = 'nijie'
									member_id = results['results'][0]['data']['member_id']
									illust_id = results['results'][0]['data']['nijie_id']
								elif index_id == 34:
									# 34->da
									service_name = 'da'
									illust_id = results['results'][0]['data']['da_id']
								else:
									# unknown
									print('Unhandled Index! Exiting...')
									sys.exit(2)
							try:
								if member_id >= 0:
									newfname = os.path.join(root, service_name + '_' + str(member_id) + '_' + str(
										illust_id) + page_string + '.' + fname.split(".")[-1].lower())
								else:
									newfname = os.path.join(root,
															service_name + '_' + str(illust_id) + page_string + '.' +
															fname.split(".")[-1].lower())
								print('New Name: ' + newfname)
								downloadFromPixiv(str(illust_id), session, page_string, member_id)

							except Exception as e:
								print(e)
								sys.exit(3)
						else:
							print('miss... ' + str(results['results'][0]['header']['similarity']))

					else:
						print('no results... ;_;')

					if int(results['header']['long_remaining']) < 1:  # could potentially be negative
						print('Out of searches for today. Sleeping for 6 hours...')
						time.sleep(6 * 60 * 60)
					if int(results['header']['short_remaining']) < 1:
						print('Out of searches for this 30 second period. Sleeping for 25 seconds...')
						time.sleep(25)

print('All Done!')
