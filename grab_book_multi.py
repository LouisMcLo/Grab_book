
import time
import json
import sys
import os
from mylib import *


URL1 = "https://www.126shu.com/2320/"
URL_CONTENT = "http://www.126shu.com/{}"

URL_RESULT = "story/result/{}.txt"
URL_DATA = "story/data/{}.txt"

def get_cpt(url):
    doc = cm_util.soup(url)
    #创建一个字典存储小说标题，章节，链接
    data = {"name": "unknow"}
    # 获取标题 id=info class=hh
    h1 = doc.select("#info .hh")
    if len(h1) > 0:
        data["name"] = h1[0].string

    # 获取所有链接 id= headlink or list,tag= dl or dd or a
    links = doc.select("#headlink #list dl dd a")
    cp_arr = []
    for item in links:
        #获取章节名和链接，并去掉章节名中的[126shu.com]
        cp_arr.append(
            {"url": URL_CONTENT.format(item.get("href")), "name": item.string.replace("[126shu.com]","").replace("[www.126shu.com]","")
             .replace("?"," ").replace("/"," ").replace("\\"," ").replace("\""," ").replace(":"," ").replace("*"," ")
             .replace("<"," ").replace(">"," ").replace("|"," ")}
        )
    data["cp"] = cp_arr
    return data

#将每一章生成一个txt
def get_text(item):
    dest_file = URL_DATA.format(item["name"])
    if os.path.exists(dest_file):
        print("exist file, so we will use cache: %s " % dest_file)
        return dest_file
    doc = cm_util.soup(item["url"])
    con = doc.select("#content")

    if len(con) > 0:
        con_l = con[0].select(".zjtj")
        if len(con_l) > 0:
            con_l[0].extract()
        con_l = con[0].select(".zjxs")
        if len(con_l) > 0:
            con_l[0].extract()
        c = con[0].text
        txt = (
            c.replace("www.126shu.com", "")
            .replace("\r", "")
            .replace("请百度搜索（）", "")
            .replace("\xa0", "\n")
            .replace("\n\n\n\n", "\n\n")
            .replace("\n\n\n\n", "\n\n")
        )  # replace("\r", "\n\n").replace("         ", "")
        print("get data: %s" % item["name"])
        cm_util.write_file(dest_file, ("\n\n%s" % item["name"]) + txt, "a+")
        return dest_file
    return None


# 定义章节字典
text_path = {}
#item包含name:url
def get_text_thread(item, id, name):
    #生成章节文件并将章节文件名dest_file给path
    path = get_text(item)
    if path:
        text_path[item["name"]] = path
    else:
        print("[warn]: cannot find content: %s,%s" % (item["url"], item["name"]))


def get_content(data):
    # 全本小说文件名
    dest_file = URL_RESULT.format(data["name"])
    #创建小说文件
    cm_util.write_file(dest_file, "")
    #定义线程管理器
    manager = ThreadManager(len(data["cp"]))
    thread_names = [
        "thread_a",
        "thread_b",
        "thread_c",
        "thread_d"
    ]
    #将章节链接列表放入队列
    manager.put_data(data["cp"])
    #生成线程，put_cbk_thread调用CBThread调用process_data循环调get_text_thread
    manager.put_cbk_thread(thread_names, get_text_thread)
    # 等待队列清空
    manager.wait()
    # 通知线程是时候退出
    manager.exit()
    # 等待所有线程完成
    manager.join()

    # 按照顺序合并
    for item in data["cp"]:
        path = text_path.get(item["name"], None)
        if path:
            txt = cm_util.read_file(path)
            cm_util.append_file(dest_file, txt)

if __name__ == "__main__":
    cm_util.recode_begin()
    get_content(get_cpt(URL1))
    cm_util.recode_end()
