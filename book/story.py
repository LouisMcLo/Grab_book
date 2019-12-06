# coding=utf-8
import os
from mylib import *

URL_RESULT = "story/result2/{}.txt"
URL_DATA = "story/data2/{}"
URL_TXT_CHAPTER = "story/data2/{}/{}.txt"
CONFIG_DATA = "story/data2/{}/config.json"

class Parser:
    def __init__(self, base_url=""):
        self.base_url = base_url

    def get_chapter(self, url):
        return None

    def get_text(self, item):
        return None

class StoryFactory:
    def __init__(self):
        self.url_matcher = {}
        self.max_thread_size = 10

    # 注册
    def registe(self, base_url, get_chapter, get_text):
        self.url_matcher[base_url] = {
            "base_url": base_url,
            "get_cpt": get_chapter,
            "get_text": get_text,
        }

    def registe_paser(self, p):
        self.registe(p.base_url, p.get_chapter, p.get_text)

    def match(self, url):
        print("self.url_matcher=")
        print(self.url_matcher)
        for base_url in self.url_matcher:
            #检查url是否以base_url开头，startswith方法用于检查字符串是否是以指定子字符串开头
            if url.startswith(base_url):
                return base_url
        return None

    def get_text_thread(self, item, id, name):
        conf_path = CONFIG_DATA.format(item["book_key"])
        chap_data = cm_util.read_file(conf_path)

        get_text = self.url_matcher[chap_data["base_url"]].get(
            "get_text", None
        )  # (item)
        if not get_text:
            print("[warn] not match url: %s" % item["url"])
            return
        txt = get_text(item)
        if txt:
            cm_util.write_file(
                URL_TXT_CHAPTER.format(item["book_key"], cm_util.md5(item["name"])), txt
            )
        else:
            print("[warn]: cannot find content: %s,%s " % (item["url"], item["name"]))

    def run(self, url):
        key = cm_util.md5(url)
        cm_util.recode_begin(key)
        #比对小说网址是否以主页网址开头
        base_url = self.match(url)
        if not base_url:
            print("[warn] not match url: %s" % url)
            return

        print("[info] url:[%s] %s - %s" % (key, url, base_url))
        if not os.path.exists(URL_DATA.format(key)):
            os.makedirs(URL_DATA.format(key))

        matcher = self.url_matcher[base_url].get("get_cpt", None)
        if not matcher:
            print("[warn] not match url: %s" % url)
            return
        chap_data = matcher(url)
        conf_path = CONFIG_DATA.format(key)
        if os.path.exists(conf_path):
            chap_data = cm_util.read_file(conf_path)
        else:
            chap_data["base_url"] = base_url
            for item in chap_data["chapter"]:
                name = item.get("name", None)
                if name:
                    item["key"] = cm_util.md5(name)
                item["book_key"] = key
            cm_util.write_file(conf_path, chap_data)

        manager = ThreadManager(len(chap_data["chapter"]))
        thread_names = []
        for ch in range(self.max_thread_size):
            thread_names.append("thread_%d" % ch)

        manager.put_data(chap_data["chapter"])
        manager.put_cbk_thread(thread_names, self.get_text_thread)
        # 等待队列清空
        manager.wait()
        # 通知线程是时候退出
        manager.exit()
        # 等待所有线程完成
        manager.join()

        # 小说名称
        dest_file = URL_RESULT.format(chap_data["title"])
        cm_util.write_file(dest_file, "")
        # 按照顺序合并
        for item in chap_data["chapter"]:
            ch_path = URL_TXT_CHAPTER.format(key, cm_util.md5(item["name"]))
            txt = cm_util.read_file(ch_path)
            if txt:
                cm_util.append_file(dest_file, txt)
        cm_util.recode_end(key)


story_factory = StoryFactory()