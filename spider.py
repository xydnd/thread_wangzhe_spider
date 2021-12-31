import threading
from urllib import parse,request
import queue
import requests
import json
import re
import os

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0'
}

#生产图片链接
#访问目标url，解析出需要的数据，获取到字段并存入图片链接队列中，并创建对应文件夹
#图片链接队列主要存储图片的命名和图片的url
class Product(threading.Thread):
    def __init__(self,page_queue,image_queue,*args,**kwargs):
        super(Product,self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.image_queue = image_queue
    def run(self):
        while not self.page_queue.empty():
            page_url = self.page_queue.get()
            resp = requests.get(page_url,headers=headers)
            #获得括号里的列表
            text = re.findall("^jQuery17107576856184049339_1640875389876\((.+)\)",resp.text)  
            text = text[0]
            #里面是字典字符串，转换为python的字典
            text_dict = json.loads(text)
            List = text_dict["List"]
            #获取信息列表
            for hero in List:
                image_url = []
                name = parse.unquote(hero["sProdName"])
                path = os.path.join("image",name)
                for img_index in range(1,9):
                    img = parse.unquote(hero["sProdImgNo_%d"%img_index])
                    image_url.append(img)
                # 
                if not os.path.exists(path):
                    os.mkdir(path)
                for index,image in enumerate(image_url):
                    data = {"name":os.path.join(path,"%d.jpg"%(index+1)),"image":image}
                    self.image_queue.put(data)

#下载图片链接
class Consumer(threading.Thread):
    def __init__(self,image_queue,*args,**kwargs):
        super(Consumer,self).__init__(*args,**kwargs)
        self.image_queue = image_queue

    def run(self) -> None:
        while not self.image_queue.empty():
            image_dict = self.image_queue.get(timeout=10)
            print(image_dict)
            name = image_dict["name"]
            image_url = image_dict["image"]
            try:
                request.urlretrieve(image_url,name)
                print("下载成功：",name)
            except:
                print("下载失败")
        print("下载完成")




def main():
    url = "https://apps.game.qq.com/cgi-bin/ams/module/ishow/V1.0/query/workList_inc.cgi?activityId=2735&sVerifyCode=ABCD&sDataType=JSON&iListNum=4&totalpage=0&page=&iOrder=0&iSortNumClose=1&jsoncallback=jQuery17107576856184049339_1640875389876&iAMSActivityId=51991&_everyRead=true&iTypeId=1&iFlowId=267733&iActId=2735&iModuleId=2735&_=1640875392538"
    page_queue = queue.Queue()
    image_queue = queue.Queue()
    page_queue.put(url)

    for i in range(3):
        p = Product(page_queue,image_queue)
        p.start()
    for i in range(5):
        c = Consumer(image_queue)
        c.start()
    

if __name__ == "__main__":
    main()