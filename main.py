import csv
import requests
from lxml import etree
import re
import time
from setting import INTERVAL, PASSPORT, SUID, SUV, KEYWORD, MAX_PAGE
import execjs, re

ses = requests.session()
ses.cookies.set("SUID", SUID)
ses.cookies.set("SUV", SUV)
ses.cookies.set("PASSPORT", PASSPORT)


def get_params(keyword, page):
    params = {
        "query": keyword,
        "_sug_type_": "1",
        "s_from": "input",
        "_sug_": "n",
        "type": "2",
        "page": page,
        "ie": "utf8",
    }
    return params


def time_format(timestamp):
    time_array = time.localtime(timestamp)
    ret = time.strftime("%Y/%m/%d %H:%M:%S", time_array)
    return ret


def check_status(doc):
    if doc.xpath("//span[text()='您的访问出错了']"):
        return -1
    if doc.xpath("//p[text()='\r\n\t\t没有找到相关的微信公众号文章。\r\n\t\t']"):
        return -2
    return 1


def get_new_cookies():
    url = "https://v.sogou.com"
    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.24"
    }
    rst = requests.get(
        url=url,
        headers=_headers,
        allow_redirects=False,
    )
    cookies = rst.cookies
    return cookies


def get_content(keyword, page, interval):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.24",
        "Referer": r"https://weixin.sogou.com/antispider/?from=%2fweixin&antip=wx_hb",
    }
    time.sleep(interval)
    params = get_params(keyword, page)
    res = ses.get("https://wx.sogou.com/weixin", params=params, headers=headers)
    res.close()
    res.encoding = "utf-8"
    text = (
        res.text.replace("<em>", "")
        .replace("</em>", "")
        .replace("<!--red_beg-->", "")
        .replace("<!--red_end-->", "")
        .replace("&ldquo;", "“")
        .replace("&rdquo;", "”")
    )
    doc = etree.HTML(text)
    return doc


def get_real_url(url):
    # time.sleep(0.5)
    res = ses.get(url)
    res.encoding = "utf-8"
    html = res.text
    doc = etree.HTML(html)
    status = check_status(doc)
    if status == 1:
        js = (
            "function s() {"
            + "".join(re.findall('\{.*?url.replace\("@", ""\);', html, re.S))
            + "return url}}"
        )
        new_url = execjs.compile(js).call("s")
        return new_url
    elif status == -1:
        ses.cookies = get_new_cookies()
        ses.cookies.set("PASSPORT", PASSPORT)
        print("重新生成cookie")
        return get_real_url(url)


def search(keyword, page, interval):
    doc = get_content(keyword, page, interval)
    status = check_status(doc)
    if status == 1:
        title = doc.xpath("//div[@class='txt-box']/h3/a[1]/text()")
        author = doc.xpath("//div[@class='txt-box']/div/a/text()")
        info_urls = [
            "https://wx.sogou.com" + i
            for i in doc.xpath("//div[@class='txt-box']/div/a/@href")
        ]
        time_list = [
            time_format(int(re.search("[0-9]+", i).group(0)))
            for i in doc.xpath("//span[@class='s2']/script/text()")
        ]
        content = doc.xpath("//div[@class='txt-box']/p/text()")
        urls = [
            "https://wx.sogou.com" + i
            for i in doc.xpath("//div[@class='txt-box']/h3/a[1]/@href")
        ]
        urls = list(map(get_real_url, urls))
        info_urls = list(map(get_real_url, info_urls))
        result = list(zip(time_list, title, author, content, info_urls, urls))
        if result == []:
            print("未登录")
        return result
    elif status == -1:
        ses.cookies = get_new_cookies()
        ses.cookies.set("PASSPORT", PASSPORT)
        print("重新生成cookie")
        return search(keyword, page, interval)
    elif status == -2:
        print("爬取完毕")
        return -2


if __name__ == "__main__":
    for page in range(1, MAX_PAGE + 1):
        print(f"页数{page}开始")
        results = search(KEYWORD, page, INTERVAL)
        if results == -2:
            break
        print(f"{results.__len__()}条内容已解析")
        with open(f"{KEYWORD}.csv", mode="a", encoding="utf-8-sig", newline="") as f:
            # 基于打开的文件，创建 csv.DictWriter 实例，将 header 列表作为参数传入。
            writer = csv.writer(f)
            writer.writerows(results)
