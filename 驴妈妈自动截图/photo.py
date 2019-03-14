#coding=utf-8

#网址：https://so.ly.com/scenery?q=%E6%B8%A9%E5%B7%9E
#文件名：photo.py
#作者: huanghong
#创建日期: 2018-05-05
#功能描述: 驴妈妈景点收集
#完成状况：完成

# # phantomjs 的方法截图 
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import codecs,csv,time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
path3=os.path.join(os.getcwd(),'imgs')
path1=unicode(os.path.join(sys.path[0],'驴妈妈景点.csv'),'utf-8')
city_list = '湖州、金华、青岛、台州、天津、威海、潍坊、武汉、烟台、长春、淄博、西安、苏州、哈尔滨、大庆、齐齐哈尔、吉林、沈阳、大连、营口、呼和浩特、包头、鄂尔多斯、太原、大同、咸阳、渭南、银川、西宁、兰州、乌鲁木齐、拉萨、贵阳、南昌、九江、海口、三亚、江门、肇庆、潮州、揭阳、舟山'.split('、')



def smain(weburl):
    # for weburl in hreflist:
    # pathname = pathn+weburl.split('?')[-1]
    dcap = dict(DesiredCapabilities.PHANTOMJS)  #设置userAgent
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 ") 
    obj = webdriver.PhantomJS(executable_path='C:\Python27\phantomjs.exe',desired_capabilities=dcap) #加载网址
    # try:
    obj.get(weburl[2])#打开网址
    # time.sleep(5)
    path4 = os.path.join(path3,weburl[0])
    obj.save_screenshot(os.path.join(path4,weburl[1]+".png"))   #截图保存
    obj.quit()
    # time.sleep(1)
    # except Exception as e:
    #     time.sleep(5)
    #     smain(weburl,pathn)


def read_path3():
    data=[]
    with codecs.open(path1,'r') as f:
        reads = csv.reader(f)
        t=0
        for i in reads:
            t+=1
            if t>835:
                data.append([i[0].decode('utf-8'),i[1].decode('utf-8'),i[8].decode('utf-8')])
                # print i[1],i[2],i[8]
    print len(data)
    return data 

def main():
    for city in city_list:
        paths=unicode(os.path.join(path3,city),'utf-8')
        if not os.path.exists(paths):
            os.makedirs(paths)
    data = read_path3()
    t=0
    for  i in data:
    	t+=1
    	print t
        print i[1],i[2]
        smain(i)

if __name__ == '__main__':
    main()


    
