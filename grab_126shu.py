from book import *
from mylib import *
import os
class P126shu(Parser):
    def __init__(self):
        #super()是指继承父类，这里就是class Parser，即Parser.base_url="https://www.126shu.com/"
        super().__init__("https://www.126shu.com/")

    def get_chapter(self, url):
        doc = cm_util.soup(url)

        data = {"title": "unknow"}
        # 获取标题
        h1 = doc.select("#info .hh")
        if len(h1) > 0:
            data["title"] = h1[0].string

        # 获取所有链接
        links = doc.select("#headlink #list dl dd a")
        cp_arr = []
        for item in links:
            cp_arr.append(
                {"url": (url + "{}").format(item.get("href")), "name": item.string.replace("[126shu.com]","").replace("[www.126shu.com]","")
             .replace("?"," ").replace("/"," ").replace("\\"," ").replace("\""," ").replace(":"," ").replace("*"," ")
             .replace("<"," ").replace(">"," ").replace("|"," ")}
            )
        data["chapter"] = cp_arr
        return data

    #将每一章生成一个txt
    def get_text(self,item):
        '''
        dest_file = URL_TXT_CHAPTER.format(item["name"])
        if os.path.exists(dest_file):
            print("exist file, so we will use cache: %s " % dest_file)
            return dest_file
            '''
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
            #cm_util.write_file(dest_file, ("\n\n%s" % item["name"]) + txt, "a+")
            return txt
        return None

story_factory.registe_paser(P126shu())

if __name__ == "__main__":
    url = "https://www.126shu.com/16888/"
    URL_TXT_CHAPTER = "story/data2/{}/{}.txt"
    story_factory.run(url)