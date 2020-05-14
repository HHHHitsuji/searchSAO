import logging
import json
import time
import requests, re
from saucenao import SauceNao
from bs4 import BeautifulSoup


api_key = 'f97b00f6ea3c0fe68b9d9568be351287859416e6'
file_path = 'test.jpg'

your_username = ''
your_password = ''
your_proxy = ''


def getSauceNao(api_key):
    saucenao = SauceNao(directory='.', databases=5, minimum_similarity=65, combine_api_types=False, api_key=api_key,
                        exclude_categories='', move_to_categories=False,  use_author_as_category=False,
                        output_type=SauceNao.API_JSON_TYPE, start_file='.', log_level=logging.ERROR,
                        title_minimum_similarity=60)
    return saucenao


def getPixivID(file_path, saucenao):
    origin = saucenao.check_file(file_path)[0]['header']

    return origin


def login():
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Referer': 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=64503210'
    }

    # 用requests的session模块记录登录的cookie

    session = requests.session()

    # 首先进入登录页获取post_key，我用的是正则表达式
    if your_proxy != '':
        response = session.get('https://accounts.pixiv.net/login?lang=zh',
                               proxies={'http': 'http://' + your_proxy, 'https': 'https://' + your_proxy})
    else:
        response = session.get('https://accounts.pixiv.net/login?lang=zh')
    post_key = re.findall('<input type="hidden" name="post_key" value=".*?">',
                          response.text)[0]
    post_key = re.findall('value=".*?"', post_key)[0]
    post_key = re.sub('value="', '', post_key)
    post_key = re.sub('"', '', post_key)

    # 将传入的参数用字典的形式表示出来，return_to可以去掉
    data = {
        'pixiv_id': your_username,
        'password': your_password,
        'return_to': 'https://www.pixiv.net/',
        'post_key': post_key,
    }

    # 将data post给登录页面，完成登录
    if your_proxy != '':
        session.post("https://accounts.pixiv.net/login?lang=zh", data=data, headers=head,
                    proxies={'http': 'http://' + your_proxy, 'https': 'https://' + your_proxy})
    else:
        session.post("https://accounts.pixiv.net/login?lang=zh")

    print("登录成功")
    return session


def downloadFromPixiv(image_id, session, page, member_id):
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Referer': 'https://www.pixiv.net/artworks/' + image_id}

    url1 = 'https://www.pixiv.net/ajax/illust/' + image_id + '/pages'
    if your_proxy != '':
        request = session.get(url1,
                            proxies={'http': 'http://' + your_proxy, 'https': 'https://' + your_proxy})
    else:
        request = session.get(url1)

    soup1 = BeautifulSoup(request.content, "html.parser")
    original = json.loads(soup1.string)['body'][page]['urls']['original']
    if your_proxy != '':
        img_res = requests.get(original, headers=head,
                           proxies={'http': 'http://' + your_proxy, 'https': 'https://' + your_proxy})
    else:
        img_res = requests.get(original)
    with open('./image/' + str(member_id) + '_' + image_id + '_p' + str(page) + '.jpg',
              'wb') as jpg:
        jpg.write(img_res.content)


if __name__ == '__main__':
    saucenao = getSauceNao(api_key)
    # session = login()
    for i in range(5):
        try:
            origin = getPixivID(file_path, saucenao)
        except Exception as e:
            print(str(e))
            time.sleep(3)
        print(origin)