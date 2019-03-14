#-*- coding:utf-8 -*-
#网址：https://shenzhen.anjuke.com/?pi=PZ-baidu-pc-all-biaoti
#文件名：anjuke.py
#作者: huanghong
#创建日期: 2017-010-28
#功能描述: 安居客全国新房信息
#完成状况：完成
import requests
from lxml import etree
import sys
import codecs,csv
from bs4 import BeautifulSoup
import urllib
import urllib2
import re
import time
import os.path
import threading
from datetime import datetime
import sqlite3
import MySQLdb as db
from multiprocessing import Pool,Lock
import multiprocessing
reload(sys)
sys.setdefaultencoding('utf-8')
lock = threading.Lock()
Loc = Lock()
se = requests.session()
headers={
		"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
		"X-Requested-With":"XMLHttpRequest"
		}

old_href=[]
New_href=[]
filename=unicode(os.path.join(sys.path[0],'安居客新房信息.db'),'utf-8')
logg=unicode(os.path.join(sys.path[0],'logs.log'),'utf-8')
usv=unicode(os.path.join(sys.path[0],'url.csv'),'utf-8')
#log日志
def loggs(strs):
    with open(logg,'ab') as f:
        time = str(datetime.now())[:-7]
        t = os.linesep
        s = time+' : '+str(strs)
        print s
        f.write(s+t)




class Get_link():
	"""docstring for Get_LINK"""
	def __init__(self):
		self.Href=list(set(self.read_set1()))
		self.cherk_href=[]
		
	def read_set1(self):
		v=[]
		with codecs.open (usv,'r') as f:
			a=f.readlines()
			for i in a:
				i=i.replace('\n','')
				v.append(i)				
		return v
	
	def get_data(self):	
		while True:
			lock.acquire()
			if len(self.Href)==0:
				lock.release()
				break
			else:
				po=self.Href.pop(0)
				print po
				lock.release()
				try:
					req=requests.get(po,headers=headers).content
				except Exception as e:
					pass
				lng=re.findall('lat:(.*), lng:(.*)\}\)',req)
				if len(lng)!=0:
					try:
						html=etree.HTML(req.decode('utf-8'))
					except Exception as e:
						pass
					city=html.xpath(u"//div[@class='crumb-item fl']/a[position()=1]/text()")[0].replace(u'安居客','')
					h1=html.xpath("//h1[@id='j-triggerlayer']/text()")[0]
					div=re.findall('class="district-mod"',req)
					dizhi=html.xpath('//span[@class="lpAddr-text"]/text()')[0].replace(' ','').replace('[','').split(']')
					if len(div)==0:
						na='no'
					else:
						na='yes'
					shijian=time.strftime('%Y-%m-%d',time.localtime(time.time()))
					data=[city,dizhi[0],h1,dizhi[1],lng[0][0].replace(' ',''),lng[0][1].replace(' ',''),na,shijian,po]								
					
					try:
						lock.acquire()
						savesql(data,filename)
						lock.release()
					except Exception as e:
						continue		
					
					
					

#===========================================================================================================#获取所有房源连接
#获取各个城市连接
class Get_city():
	"""docstring for Get_city"""
	def __init__(self):
		self.city_link = self.get_city()
	def get_city(self):	
		city_link=[]
		req=requests.get('https://www.anjuke.com/sy-city.html',headers=headers).content
		soup=BeautifulSoup(req,'lxml')
		div=soup.find_all('div',class_="letter_city")[0]
		a=div.find_all('a')
		yi=0
		for i in a:	
			yi+=1
			text=i.text
			link=i.get('href')
			city_link.append(link)
			
		return city_link	
			
	# 获取新房连接，存到data_url	
	def get_link(self):			
		while True:
			lock.acquire()
			if len(self.city_link)==0:
				lock.release()
				break
			else:
				url=self.city_link.pop(0)
				lock.release()
	 		#翻页
				print url
				ti=0
				try:
					req=requests.get(url,headers=headers).content
				except Exception as e:
					pass
				url2=re.findall(r'<a class="a_navnew" hidefocus="true" href="(https://.*?.fang.anjuke.com/)" _soj="navigation">新 房</a>',req)
				if len(url2)!=0:
					ti=0
					while True:
						ti+=1
						urls=url2[0]+'loupan/all/p%s/'%ti
						print urls	
						try:
							req2=requests.get(urls,headers=headers).content
						except Exception as e:
							pass
						html=etree.HTML(req2)
						a=html.xpath(u"//div[@class='key-list']/div[@class='item-mod ']/a[@class='pic']/@href")
						if len(a)==0:
							break					
						for i in a:							
							lock.acquire()
							with codecs.open(usv,'ab') as f:
								w = csv.writer(f)
								w.writerow([i])
							lock.release()	
	


#=========================================================================================================== # 开启进程+线程
def thread():
	with Loc:	
		da=Get_city()
		tasks = [] #任务列表
		for x in range(15):
			t = threading.Thread(target=da.get_link) #准备线程函数及参数
			t.setDaemon(True) #设置守护线程（主线程退出，子线程也会退出，不会挂起占用资源）
			tasks.append(t)
		for t in tasks:
			t.start() #启动多线程（任务列表有多少个值，就会启动多少个线程）
		for t in tasks:
			t.join()

def pool():
	pool = multiprocessing.Pool(processes = 4)
	pool.apply_async(thread)
	pool.close()
	pool.join()				
#===========================================================================================================#
def savesql(data,savepoint_name):  
    con=sqlite3.connect(savepoint_name)
    con.execute('''CREATE TABLE IF NOT  EXISTS data
        (
        city varchar(200) NOT NULL,
        zone varchar(100) DEFAULT NULL,
        company varchar(1000) DEFAULT NULL, 
        lng varchar(100) DEFAULT NULL,
        lat varchar(100) DEFAULT NULL,
        address varchar(1000) DEFAULT NULL,
        fromram  varchar(100) DEFAULT NULL,
        updatime varchar(100) DEFAULT NULL,
        deaser varchar(100) DEFAULT NULL ,
        url varchar(300) primary key NOT NULL);''')
# 插入数据   
    sql='insert into data(city,zone,company,address,lng,lat,fromram,updatime,url)\
       values("%s","%s","%s","%s","%s","%s","%s","%s","%s")'%(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])
    con.execute(sql)
    con.commit()
    con.close()
#===========================================================================================================## 开启进程+线程
def thread2():
	with Loc:	
		da=Get_link()
		tasks = [] #任务列表
		for x in range(20):	
			t = threading.Thread(target=da.get_data) #准备线程函数及参数
			t.setDaemon(True) #设置守护线程（主线程退出，子线程也会退出，不会挂起占用资源）
			tasks.append(t)
		for t in tasks:
			t.start() #启动多线程（任务列表有多少个值，就会启动多少个线程）
		for t in tasks:
			t.join()
def pool2():
	pool = multiprocessing.Pool(processes = 4)
	pool.apply_async(thread2)
	pool.close()
	pool.join()	

 #=================================================主函数 第一次跑下所有数据

#==================================================================================添加新的房源信息

#查询数据所有url 与之后获取URL对比有无新url
def chark_data(savepoint_name): 
    con=sqlite3.connect(savepoint_name)
    datas=con.execute('SELECT url from data')
    for i in datas:
    	old_href.append(i[0]) 	
    con.commit()
    con.close()





#得到新连接后入库
def get_data2():
	while True:
		lock.acquire()
		if len(New_href)==0:
			lock.release()
			break
		else:
			po=New_href.pop(0)
			lock.release()		
			try:
				req=requests.get(po,headers=headers).content
			except Exception as e:
				pass
			print po
			lng=re.findall('lat:(.*), lng:(.*)\}\)',req)	
			if len(lng)!=0:
				html=etree.HTML(req.decode('utf-8'))
				city=html.xpath(u"//div[@class='crumb-item fl']/a[position()=1]/text()")[0].replace(u'安居客','')
				h1=html.xpath("//h1[@id='j-triggerlayer']/text()")[0]
				div=re.findall('class="district-mod"',req)
				dizhi=html.xpath('//span[@class="lpAddr-text"]/text()')[0].replace(' ','').replace('[','').split(']')
				if len(div)==0:
					na='no'
				else:
					na='yes'
				shijian=time.strftime('%Y-%m-%d',time.localtime(time.time()))
				data=[city,dizhi[0],h1,dizhi[1],lng[0][0].replace(' ',''),lng[0][1].replace(' ',''),na,shijian,po]				
				try:
					lock.acquire()
					savesql(data,filename)
					lock.release()
				except Exception as e:
					continue		
									

# ===================================================================================检查楼栋信息

class Gengxin():
	"""docstring for Gengxi"""
	def __init__(self):
		self.cherk_href =self.chark_data2(filename)
		
	def get_data3(self):			
		while True:
			lock.acquire()
			if len(self.cherk_href)==0:
				lock.release()
				break
			else:
				po=self.cherk_href.pop(0)
				print po
				lock.release()		
				try:
					req=requests.get(po,headers=headers).content
				except Exception as e:
					pass					
				lng=re.findall('lat:(.*), lng:(.*)\}\)',req)			
				if len(lng)!=0:
					html=etree.HTML(req.decode('utf-8'))
					city=html.xpath(u"//div[@class='crumb-item fl']/a[position()=1]/text()")[0].replace(u'安居客','')
					h1=html.xpath("//h1[@id='j-triggerlayer']/text()")[0]
					div=re.findall('class="district-mod"',req)
					dizhi=html.xpath('//span[@class="lpAddr-text"]/text()')[0].replace(' ','').replace('[','').split(']')
					if len(div)==0:
						na='no'
					else:
						na='yes'
					if na=='yes':
						shijian=time.strftime('%Y-%m-%d',time.localtime(time.time()))
						data=[city,dizhi[0],h1,dizhi[1],lng[0][0].replace(' ',''),lng[0][1].replace(' ',''),na,shijian,po]					
						lock.acquire()
						genxin_data(data,filename)
						lock.release()



	def chark_data2(self,savepoint_name):
	    v=[] 
	    con=sqlite3.connect(savepoint_name)
	    datas=con.execute('SELECT url from data where fromram="no" ')
	    for i in datas:
	    	v.append(i[0]) 	
	    con.commit()
	    con.close()
	    return v

#更新是否有楼栋信息yes    
def genxin_data(data,savepoint_name):
    con=sqlite3.connect(savepoint_name)
    sql2='update data set fromram="%s",updatime="%s",deaser="YES" where url="%s"'%(data[6],data[7],data[8])
    con.execute(sql2)
    con.commit()
    con.close()


def thread3():
	with Loc:
		dag=Gengxin()
		tasks = [] #任务列表
		for x in range(20):	
			t = threading.Thread(target=dag.get_data3) #准备线程函数及参数
			t.setDaemon(True) #设置守护线程（主线程退出，子线程也会退出，不会挂起占用资源）
			tasks.append(t)
		for t in tasks:
			t.start() #启动多线程（任务列表有多少个值，就会启动多少个线程）
		for t in tasks:
			t.join()	

def pool3():
	pool = multiprocessing.Pool(processes = 4)	
	pool.apply_async(thread3)
	pool.close()
	pool.join()

def threadl(function):	
	tasks = [] #任务列表
	for x in range(20):	
		t = threading.Thread(target=function) #准备线程函数及参数
		t.setDaemon(True) #设置守护线程（主线程退出，子线程也会退出，不会挂起占用资源）
		tasks.append(t)
	for t in tasks:
		t.start() #启动多线程（任务列表有多少个值，就会启动多少个线程）
	for t in tasks:
		t.join()
def main():
	# print u'检查到%s个城市'%(len(city_link))		
	pool()
	da=Get_link()	
	# print u'检查到%s个房源信息'%(len(da.Href))
	print len(da.Href)
	print len(set(da.Href))
	pool2()
	os.remove(usv)

def gengxin():
	if os.path.exists(usv):
		os.remove(usv)
	chark_data(filename)
	pool()
	da=Get_link()
	print u'原有%s个房源信息'%(len(old_href))
	print u'检查到%s个房源信息'%(len(da.Href))
	print u'正添加数据....'
	t=0
	for i in da.Href:
		t+=1
		if i not in old_href:
			New_href.append(i)
	print u'添加%s个房源信息'%(len(New_href))
	print len(New_href)
	dag=Gengxin()
	if len(New_href)!=0:
		threadl(get_data2)
	os.remove(usv)	
	# # print len(dag.cherk_href)
	print u'开始检查楼栋信息是否存在变动'	
	pool3()
	
#========================================================================判断是否更新

def main2():
	if os.path.exists(filename):
		gengxin()
	else:
		main()
if __name__ == '__main__':
	try:
		main2()
	except Exception as e:
		loggs(e)
	