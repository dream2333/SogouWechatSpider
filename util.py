import csv
import os
import re
def get_v_code(s,res,doc,headers):
    auuid = re.search('auuid = "(.*)"',res.text).group(1)
    cookie = res.cookies
    vcode_url = "https://weixin.sogou.com/antispider/" +doc.xpath("//img[@id = 'seccodeImage']/@src")[0]
    res = s.get(vcode_url ,headers=headers)
    with open("vcode.jpg","wb") as img:
        img.write(res.content)
    vcode = input()
    data = rf"c={vcode}&r=%252Fweixin&p=wx_hb&v=5&suuid=&auuid={auuid}"
    res = s.post("https://weixin.sogou.com/antispider/thank.php" ,data=data,headers=headers)
    msg = res.json()
    res.close()
    res.request
    result = res.text
    print(result)
    return result

def save_csv(filename: str, data: dict, mode: str = "a"):
    """将dict保存到csv文件
    参数：
        filename : 文件路径
        data : dict数据
        mode : 写入类型，"a"为追加，"w"为覆盖
    """
    # 文件不存在则创建空文件,并写入表头
    if mode == "a" and not os.path.isfile(filename):
        f = open(filename, "w", encoding="utf-8-sig", newline="")
        writer = csv.DictWriter(f, list(data[0].keys()))
        writer.writeheader()
        f.close()
    with open(filename, mode=mode, encoding="utf-8-sig", newline="") as f:
        # 基于打开的文件，创建 csv.DictWriter 实例，将 header 列表作为参数传入。
        writer = csv.DictWriter(f, list(data[0].keys()))
        # 写入数据,如果是覆盖数据则额外写入表头
        if mode == "w":
            writer.writeheader()
        writer.writerows(data)