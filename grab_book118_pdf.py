import requests
import json
import re
import time
import os   # 这个库后来想想实际上可以不用
import sys
from bs4 import BeautifulSoup
from PIL import Image

# https://max.book118.com/
# made by wenz
#2019-9-11
#problems: 1.combine png->pdf 2.frenquent visit require verification 3.try/except
#问题：1、没有加入图片自动合成pdf的功能 2、频繁的访问要求验证 3、没有写完整try/except，哪里出bug就倒霉了
def header(url):
    HEADER_CONFIG = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'gzip',
        'Connection': 'close',
        'Host': 'max.book118.com',
        'Referer':url  # 注意如果依然不能抓取的话，这里可以设置抓取网站的host
        }
    return HEADER_CONFIG

def getPreviewData():
#这个函数用于获取该文档的预览数据
    aid = urlD()
    playload = {'g': 'Home','m': 'NewView','a': 'index','aid': aid}
    host = 'https://max.book118.com/index.php'
    rep = requests.get(host,headers=header(host),params=playload)
    if rep.text.find('验证') != -1:
    # 过于频繁的访问返回的会是要求验证的网页，验证的代码就没写了，如果要写url在下面注释
        # reps = requests.get('https://max.book118.com//index.php?m=Public&a=verify')
        # img = reps.content
        print('need verify')
    else:
        bs = BeautifulSoup(rep.text, 'lxml')
        for sc in bs.find_all('script'):
            js = sc.get_text()
            if js.find('PREVIEW_PAGE') > -1:
                #compile定义好匹配规则，给下面的findall来使用,找出xx'xx'
                p1 = re.compile(r".+?'(.+?)'")
                #splitlines() 按照行('\r', '\r\n', \n')分隔，返回一个包含各行作为元素的列表,参数为True则保留换行符
                js_line = js.splitlines(1)
                book = {
                    'pageAll': p1.findall(js_line[1])[0],
                    'pagePre': p1.findall(js_line[1])[1],
                    'aid': p1.findall(js_line[6])[0],
                    'viewToken': p1.findall(js_line[6])[1],
                    'title' : ''
                }
                return book


def getUrlDict(book):
#这个函数用于获取文档的所有预览图片地址，输入的是文档预览数据，返回预览页面dict
    page = { 'max': int(book['pageAll']) , 'pre': int(book['pagePre']) , 'num': 1 , 'repeat': 0 }
    url_dict = {}
    while page['num'] < page['pre']:
        url = 'https://openapi.book118.com/getPreview.html'
        playload = {
            'project_id': 1,
            'aid': book['aid'],
            'view_token': book['viewToken'],
            'page': page['num']
        }
        rep = requests.get(url, params=playload)
        rep_dict = json.loads(rep.text[12:-2])
        try:
            if rep_dict['data'][str(page['num'])] != '': #获取得到url则更新进字典
                url_dict.update(rep_dict['data'])
                page['num'] = page['num'] + 6
                page['repeat'] = 0
            else: #获取不到url（主要是网络原因）则休息一会后重试
                if page['repeat'] > 3:
                    sys.stdout.write('\r{0}'.format(str(page['num']) + " : Repeat too much.\n !get nothing, sleep 5 second."))
                    sys.stdout.flush()
                    time.sleep(5)
                else:
                    sys.stdout.write('\r{0}'.format(str(page['num']) + " : !get nothing, sleep 2 second."))
                    sys.stdout.flush()
                    time.sleep(2)
                page['repeat'] = page['repeat'] + 1
        except:
            print("get dict wrong!!!")
            break
    print('\n')
    print(url_dict)
    return url_dict


def saveImg(aid , num, sourceUrl):
#保存图片的函数，输入文档的aid、页数、下载地址
    # load page image
    if int(num) < 10:
        num = '00' + num
    elif int(num) < 100:
        num = '0' + num
    url = 'http:' + sourceUrl
    re.sub=('http:http:','http:',url)
    rep = requests.get(url)
    time.sleep(2)
    image = open('./{aid}/{num}.png'.format(aid=aid,num=num), 'wb')
    image.write(rep.content)
    image.close()

def mkdir(path):
#判断图片文件夹是否存在，不存在则创建文件夹
    folder = os.path.exists(path)
    if folder != True:
        os.makedirs(path)
        print("---  new folder:{}...  ---".format(path))
    else:
        print("---  folder:{} exist...  ---".format(path))

def urlD():
#对输入的url进行处理（获取文档的aid），并得到文档的标题（这个好像没啥用）
    url = input("Input the book URL:")
    reg = re.compile(r".+?/(\d+?)\.shtm")
    aid = reg.findall(url)
    #rep = requests.get(url,headers=header(url))
    #rep.encoding = 'utf-8'
    #soup = BeautifulSoup(rep.text,'lxml')
    #title = soup.title
    return aid#,title

def image_2_pdf(picfolder):
    file_list = os.listdir('./%s' %picfolder)
    pic_name = []
    im_list = []
    for x in file_list:
        if "jpg" in x or 'png' in x or 'jpeg' in x:
            pic_name.append(picfolder + "/" + x)
    pic_name.sort()

    # 合并为pdf
    im1 = Image.open(pic_name[0])
    pic_name.pop(0)
    for i in pic_name:
        img = Image.open(i)
        if img.mode != "RGB":
            img = img.convert('RGB')
            im_list.append(img)
        else:
            im_list.append(img)
    im1.save("{}.pdf".format(picfolder), "PDF", resolution=100.0, save_all=True, append_images=im_list)
    print("save images to {}.pdf successful".format(picfolder))

def main():
#程序主入口
    book = getPreviewData()
    print('\n getting %s data...'%book['aid'])
    print('getting URL data...')
    url_dict = getUrlDict(book)
    print('\n---   Total: {pagea} pages, {pagep} can be downloaded   ---'.format(pagea = book['pageAll'],pagep = book['pagePre']))
    print('\n---   get %s urls success...   ---'%len(url_dict))
    #flag = input('Start download? [y/n]:')
    #if flag != 'n':
    mkdir('./%s' %book['aid'])
    for item in url_dict:
        try:
            saveImg(book['aid'], item, url_dict[item])
            #time.sleep(2)
            sys.stdout.write('\r{0}'.format('download {num}/{total} success'.format(num = item , total = len(url_dict))))
            sys.stdout.flush()
        except:
            print('%s download wrong'%item)
    input("\n---   download finished, the photo save in %s folder   ---"%book['aid'])
    image_2_pdf(str(book['aid']))

main()