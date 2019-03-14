#-*- coding:utf-8 -*-
#网址：http://s.lvmama.com/ticket/?keyword=%E6%B8%A9%E5%B7%9E&k=0#list
#文件名：lv.py
#作者: huanghong
#创建日期: 2018-05-02
#功能描述: 驴妈妈网站景点收集
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

from multiprocessing import Pool,Lock
import multiprocessing
reload(sys)
sys.setdefaultencoding('utf-8')
city_list='湖州、金华、青岛、台州、天津、威海、潍坊、武汉、烟台、长春、淄博、西安、苏州、哈尔滨、大庆、齐齐哈尔、吉林、沈阳、大连、营口、呼和浩特、包头、鄂尔多斯、太原、大同、咸阳、渭南、银川、西宁、兰州、乌鲁木齐、拉萨、贵阳、南昌、九江、海口、三亚、江门、肇庆、潮州、揭阳、舟山'.decode('utf-8').split('、')

headers={
		"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
		"X-Requested-With":"XMLHttpRequest"
		}

def get_data(city):
	page=0
	params={
	'keyword': city,
	'tabType': 'ticket'
	}
	while True:
		page+=1
		req= requests.get('http://s.lvmama.com/ticket/P%s?keyword=%s&tabType=ticket#list'%(page,city),headers=headers,params=params).content 
		html=etree.HTML(req.decode('utf-8'))
		div = html.xpath('//div[@class="product-item product-ticket searchTicket clearfix"]/div[@class="product-regular clearfix"]/div[@class="product-section"]')
		if len(div) ==0:
			break
		for data in div:
			name = data.xpath('./h3/a/text()')[0]
			href = data.xpath('./h3/a/@href')[0]
			span = data.xpath('./h3/span[@class="level"]/text()')
			if len(span)!=0:
				A = span[0]
			else:
				A=''	
			dl = data.xpath('./dl[@class="product-details clearfix"]')
			if dl>2:
				try:
					adress = dl[0].xpath('./dd/@title')[0].replace('\r\n','').replace(' ','').replace('	','')
				except Exception as e:
					adress = ''
				try:
					time = dl[1].xpath('./dd/div[@class="product-ticket-dropdown"]/text()')[1].replace('\r','').replace('\n','').replace(' ','').replace('	','')
				except Exception as e:
					time = ''
			else:	
				adress = ''
				time = ''	
			jwd = get_jwd(href)
			if len(jwd)!=0:
				data=[city,name,adress,time,A,'1010-6060',jwd[0],jwd[1],href]
			else:
				data=[city,name,adress,time,A,'1010-6060','','',href]
			with codecs.open(u'驴妈妈景点.csv','ab') as f:
				w = csv.writer(f)
				w.writerow(data)

def get_jwd(url):
	req = requests.get(url,headers=headers).content
	jwd = re.findall(r' \{ lng: (.*?), lat: (.*?) \}',req)
	if len(jwd) == 0:
		jwdl=[]
	else:
		jwdl=jwd[0]
	return jwdl

def main():
	with codecs.open(u'驴妈妈景点.csv','wb') as f:
		w = csv.writer(f)
		w.writerow([u'城市',u'名称',u'地址',u'营业时间',u'几A景区',u'电话','lng','lat',u'网址'])
	for city in city_list:
		get_data(city)			

if __name__ == '__main__':
	main()